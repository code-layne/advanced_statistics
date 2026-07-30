#!/usr/bin/env python3
"""Generate a per-unit binder cover sheet: a two-page letter PDF whose
background art is built from that unit's own lessons.

    python3 shared/cover.py unit01

Both pages are the same sheet: page 1 goes in the front of the binder, page 2
in the back.

Content comes from one of two places:

  unitNN/binder_cover/spec.py   a hand-tuned content spec: ELEMENTS, a list of
                                dicts with a type, a payload, and a placement.
                                Authoritative when present.
  auto-discovery                otherwise, the unit's lesson sources are
                                scanned for plotted functions, worked
                                solutions, and display equations, and those
                                are laid out on a jittered grid. Deterministic
                                for a given --seed, so make stays honest.

The unit number comes from the directory name and the unit title from
\\UnitNumberName in unitNN/lesson*/main.tex — never hardcoded here. Both the
\\newcommand and the \\def form of that definition are recognised.

Ink budget is a hard constraint: these print on a school printer. White
background, no solid fills, line work in grays #5f5f5f–#c9c9c9, #ffffff fills
used only for occlusion. Math is set in Latin Modern so it matches the LaTeX
output; the four OTFs this needs (lmroman10-regular/italic, latinmodern-math,
texgyretermes-regular, texgyrechorus-mediumitalic) must be installed where the
OS font service can see them — run with --check-fonts to verify.
"""
from __future__ import annotations

import argparse
import importlib.util
import math
import random
import re
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

# ── Page and palette ─────────────────────────────────────────────────────────
# 850x1100 user units at 8.5in x 11in — 100 units to the inch.
W, H = 850, 1100

COURSE = "AP Statistics"

GRID  = "#c9c9c9"   # faint grid lines
EDGE  = "#9a9a9a"   # solid geometry edges
DASH  = "#b5b5b5"   # hidden / dashed edges
CURVE = "#5f5f5f"   # function curves
AXIS  = "#7d7d7d"   # axes and tick labels
TXT   = "#3a3a3a"   # title text
TXT2  = "#5e5e5e"   # background math text
FRAME = "#d4d4d4"   # page border

# The title block occupies this band; auto-layout keeps art out of it.
TITLE_BAND = (96, 448, W - 96, 724)

# ── Fonts ────────────────────────────────────────────────────────────────────
# Each role maps to (SVG font-family, SVG font-style, filename). The file is
# used for measuring with PIL; the family goes in the SVG.
#
# The family is the face's PostScript name, not its family name. cairo selects
# through the "toy" font API, and on macOS a family name plus font-style="italic"
# does NOT reach the italic face — it silently returns the roman one, which
# would set every math variable upright. Naming the face outright is exact.
FONTS = {
    "math":    ("LMRoman10-Regular",          "normal", "lmroman10-regular.otf"),
    "mathit":  ("LMRoman10-Italic",           "normal", "lmroman10-italic.otf"),
    "mathsym": ("LatinModernMath-Regular",    "normal", "latinmodern-math.otf"),
    "serif":   ("TeXGyreTermes-Regular",      "normal", "texgyretermes-regular.otf"),
    "script":  ("TeXGyreChorus-MediumItalic", "normal", "texgyrechorus-mediumitalic.otf"),
}

_FONT_SEARCH = [
    Path.home() / "Library" / "Fonts",
    Path("/Library/Fonts"),
    Path("/usr/local/texlive/2026/texmf-dist/fonts/opentype/public/lm"),
    Path("/usr/local/texlive/2026/texmf-dist/fonts/opentype/public/lm-math"),
    Path("/usr/local/texlive/2026/texmf-dist/fonts/opentype/public/tex-gyre"),
]


@lru_cache(maxsize=None)
def _font_path(role: str) -> Path | None:
    fname = FONTS[role][2]
    for d in _FONT_SEARCH:
        p = d / fname
        if p.exists():
            return p
    return None


@lru_cache(maxsize=None)
def _pil(role: str, size: int):
    from PIL import ImageFont
    p = _font_path(role)
    if p is None:
        return None
    return ImageFont.truetype(str(p), size)


def measure(text: str, role: str, size: float) -> float:
    """Advance width of `text` in `role` at `size`, from the real font metrics."""
    if not text:
        return 0.0
    f = _pil(role, 100)
    if f is None:                       # no metrics: fall back to an estimate
        return len(text) * size * 0.5
    return f.getlength(text) * size / 100.0


@lru_cache(maxsize=None)
def _has_glyph(role: str, ch: str) -> bool:
    if ch.isspace():
        return True
    f = _pil(role, 40)
    if f is None:
        return False
    try:
        return f.getmask(ch).size[1] > 0
    except Exception:
        return False


def font_runs(text: str, italic: bool) -> list[tuple[str, str]]:
    """Split `text` into (run, role) pairs.

    Math convention: letters are italic, digits and operators upright. Anything
    Latin Modern Roman has no glyph for (relations, set symbols, Greek) falls
    back to Latin Modern Math, which is the same typeface design.
    """
    runs: list[tuple[str, str]] = []
    for ch in text:
        role = "mathit" if (italic and ch.isalpha()) else "math"
        if not _has_glyph(role, ch):
            role = "mathsym" if _has_glyph("mathsym", ch) else role
        if runs and runs[-1][1] == role:
            runs[-1] = (runs[-1][0] + ch, role)
        else:
            runs.append((ch, role))
    return runs


def check_fonts() -> list[str]:
    return [f"{role}: {FONTS[role][2]} not found" for role in FONTS
            if _font_path(role) is None]


# ── SVG helpers ──────────────────────────────────────────────────────────────

def esc(s: str) -> str:
    return (s.replace("&", "&amp;").replace("<", "&lt;")
             .replace(">", "&gt;").replace('"', "&quot;"))


def path(d: str, stroke=CURVE, width=1.5, dash=None, fill="none", cap=None) -> str:
    a = f' stroke-dasharray="{dash}"' if dash else ""
    a += f' stroke-linecap="{cap}"' if cap else ""
    return (f'<path d="{d}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{width}"{a} stroke-linejoin="round"/>')


def polyline(pts, stroke=CURVE, width=1.7, dash=None) -> str:
    if len(pts) < 2:
        return ""
    d = "M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in pts)
    return path(d, stroke=stroke, width=width, dash=dash)


def arrow(x1, y1, x2, y2, stroke=AXIS, width=1.1, head=6) -> str:
    ang = math.atan2(y2 - y1, x2 - x1)
    p1 = (x2 - head * math.cos(ang - 0.42), y2 - head * math.sin(ang - 0.42))
    p2 = (x2 - head * math.cos(ang + 0.42), y2 - head * math.sin(ang + 0.42))
    return (path(f"M{x1:.1f} {y1:.1f}L{x2:.1f} {y2:.1f}", stroke=stroke, width=width)
            + f'<path d="M{x2:.1f} {y2:.1f}L{p1[0]:.1f} {p1[1]:.1f}'
              f'L{p2[0]:.1f} {p2[1]:.1f}Z" fill="{stroke}"/>')


def label(x, y, s, size=11, fill=AXIS, anchor="middle", italic=False) -> str:
    fam, style, _ = FONTS["mathit" if italic else "math"]
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-family="{fam}" font-style="{style}" '
            f'font-size="{size}" fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>')


# ── Math typesetting ─────────────────────────────────────────────────────────
# A small TeX subset: ^ _ \frac \dfrac \tfrac \sqrt \sqrt[n] \text {} and the
# symbol names below. Enough for every expression Algebra 2 puts on a cover.

SYMBOLS = {
    # Operators and relations carry their own thin spaces, as they do in TeX.
    # Without them a scraped or hand-written expression sets as "4 \u00b1\u221a44".
    "pm": "\u2009\u00b1\u2009", "mp": "\u2009\u2213\u2009",
    "ne": "\u2009\u2260\u2009", "neq": "\u2009\u2260\u2009",
    "le": "\u2009\u2264\u2009", "leq": "\u2009\u2264\u2009",
    "ge": "\u2009\u2265\u2009", "geq": "\u2009\u2265\u2009",
    "cdot": "\u2009\u00b7\u2009", "times": "\u2009\u00d7\u2009", "div": "\u2009\u00f7\u2009",
    "to": "\u2009\u2192\u2009", "Rightarrow": "\u2009\u21d2\u2009",
    "implies": "\u2009\u21d2\u2009",
    "ldots": "\u2026", "dots": "\u2026", "infty": "\u221e",
    "in": "\u2009\u2208\u2009", "subset": "\u2009\u2282\u2009",
    "subseteq": "\u2009\u2286\u2009",
    "pi": "\u03c0", "theta": "\u03b8", "Delta": "\u0394", "alpha": "\u03b1",
    "R": "\u211d", "Q": "\u211a", "Z": "\u2124", "N": "\u2115",
    "quad": "\u2003", "qquad": "\u2003\u2003",
}


def parse_math(src: str) -> list[dict]:
    """Parse the TeX subset into a node list."""
    nodes: list[dict] = []
    i, n = 0, len(src)

    def group(j: int) -> tuple[list[dict], int]:
        """Read one argument starting at j: a {...} group or a single token."""
        while j < n and src[j] == " ":
            j += 1
        if j < n and src[j] == "{":
            depth, k = 1, j + 1
            while k < n and depth:
                depth += {"{": 1, "}": -1}.get(src[k], 0)
                k += 1
            return parse_math(src[j + 1:k - 1]), k
        if j < n and src[j] == "\\":
            k = j + 1
            while k < n and src[k].isalpha():
                k += 1
            return parse_math(src[j:k]), k
        return ([{"t": "txt", "s": src[j]}] if j < n else []), j + 1

    def push(s: str):
        if nodes and nodes[-1]["t"] == "txt":
            nodes[-1]["s"] += s
        else:
            nodes.append({"t": "txt", "s": s})

    while i < n:
        c = src[i]
        if c == "\\":
            j = i + 1
            while j < n and src[j].isalpha():
                j += 1
            name = src[i + 1:j]
            if name in ("frac", "dfrac", "tfrac"):
                num, j = group(j)
                den, j = group(j)
                nodes.append({"t": "frac", "num": num, "den": den})
            elif name == "sqrt":
                idx = None
                while j < n and src[j] == " ":
                    j += 1
                if j < n and src[j] == "[":
                    k = src.index("]", j)
                    idx = parse_math(src[j + 1:k])
                    j = k + 1
                rad, j = group(j)
                nodes.append({"t": "sqrt", "idx": idx, "rad": rad})
            elif name in ("text", "mathrm", "operatorname"):
                body, j = group(j)
                nodes.append({"t": "upright", "n": body})
            elif name in SYMBOLS:
                sym = SYMBOLS[name]
                # A symbol that carries its own thin spaces absorbs the plain
                # ones around it, so "4 \pm \sqrt{44}" and "4\pm\sqrt{44}"
                # set identically instead of one gaining a double gap.
                if sym.startswith(" ") and nodes and nodes[-1]["t"] == "txt":
                    nodes[-1]["s"] = nodes[-1]["s"].rstrip(" ")
                push(sym)
                if j < n and src[j] == " ":
                    j += 1          # a control word eats the space after it
            elif name == "":            # \\, \; \! and friends: thin spaces
                push(" " if src[j:j + 1] in (",", ";", " ") else "")
                j = i + 2
            i = j
            continue
        if c == "^" or c == "_":
            body, i = group(i + 1)
            nodes.append({"t": "sup" if c == "^" else "sub", "n": body})
            continue
        if c == "{":
            body, i = group(i)
            nodes.extend(body)
            continue
        if c == "-":
            push("\u2212")              # proper minus, not hyphen
            i += 1
            continue
        push(c)
        i += 1
    return nodes


class Box:
    """A laid-out fragment: width, extent above/below the baseline, and a
    draw(x, baseline) that emits SVG."""

    def __init__(self, w, asc, desc, draw):
        self.w, self.asc, self.desc, self.draw = w, asc, desc, draw


# TeX's italic correction: these letters overhang their advance width, so an
# upright glyph set right after one collides with it — most visibly the f in
# f(x), whose hook runs straight into the parenthesis.
ITALIC_CORR = {"f": 0.11, "j": 0.06, "y": 0.03, "v": 0.02, "w": 0.02,
               "l": 0.03, "t": 0.03}


def _text_box(text: str, size: float, fill: str, italic: bool) -> Box:
    runs = font_runs(text, italic)
    corr = [0.0] * len(runs)
    for i, (t, role) in enumerate(runs[:-1]):
        if role == "mathit" and t:
            corr[i] = ITALIC_CORR.get(t[-1], 0.0) * size
    w = sum(measure(t, r, size) + c for (t, r), c in zip(runs, corr))

    def draw(x, y, runs=runs, corr=corr, size=size, fill=fill):
        out, cx = [], x
        for (t, role), c in zip(runs, corr):
            fam, style, _ = FONTS[role]
            out.append(f'<text x="{cx:.2f}" y="{y:.2f}" font-family="{fam}" '
                       f'font-style="{style}" font-size="{size:.2f}" fill="{fill}" '
                       f'xml:space="preserve">{esc(t)}</text>')
            cx += measure(t, role, size) + c
        return "".join(out)

    return Box(w, size * 0.72, size * 0.24, draw)


def layout(nodes: list[dict], size: float, fill: str = TXT2,
           italic: bool = True) -> Box:
    boxes: list[Box] = []
    for nd in nodes:
        t = nd["t"]
        if t == "txt":
            boxes.append(_text_box(nd["s"], size, fill, italic))
        elif t == "upright":
            boxes.append(layout(nd["n"], size, fill, italic=False))
        elif t in ("sup", "sub"):
            inner = layout(nd["n"], size * 0.7, fill, italic)
            shift = -size * 0.42 if t == "sup" else size * 0.22
            boxes.append(Box(
                inner.w,
                max(0.0, inner.asc - shift),
                max(0.0, inner.desc + shift),
                (lambda x, y, inner=inner, shift=shift: inner.draw(x, y + shift)),
            ))
        elif t == "frac":
            num = layout(nd["num"], size * 0.88, fill, italic)
            den = layout(nd["den"], size * 0.88, fill, italic)
            pad = size * 0.20
            w = max(num.w, den.w) + 2 * pad
            rule_up = size * 0.28                     # rule sits above baseline
            asc = rule_up + num.desc + num.asc + size * 0.14
            desc = -rule_up + den.asc + den.desc + size * 0.20

            def draw(x, y, num=num, den=den, w=w, pad=pad, rule_up=rule_up,
                     size=size, fill=fill):
                ry = y - rule_up
                return (num.draw(x + (w - num.w) / 2, ry - size * 0.14 - num.desc)
                        + den.draw(x + (w - den.w) / 2, ry + size * 0.20 + den.asc)
                        + path(f"M{x + pad * 0.4:.2f} {ry:.2f}H{x + w - pad * 0.4:.2f}",
                               stroke=fill, width=max(0.9, size * 0.055)))

            boxes.append(Box(w, asc, desc, draw))
        elif t == "sqrt":
            rad = layout(nd["rad"], size, fill, italic)
            idx = layout(nd["idx"], size * 0.6, fill, italic) if nd["idx"] else None
            hook = size * 0.58
            # A little left bearing: the radical's tail starts hard at its box
            # edge, so without this it butts straight into a preceding ± or =.
            lead = hook + size * 0.12 + (idx.w * 0.7 if idx else 0.0)
            top = rad.asc + size * 0.22
            w = lead + rad.w + size * 0.22

            def draw(x, y, rad=rad, idx=idx, hook=hook, lead=lead, top=top,
                     w=w, size=size, fill=fill):
                x0 = x + lead - hook
                d = (f"M{x0:.2f} {y - top * 0.42:.2f}"
                     f"L{x0 + hook * 0.30:.2f} {y - top * 0.20:.2f}"
                     f"L{x0 + hook * 0.60:.2f} {y + size * 0.16:.2f}"
                     f"L{x0 + hook:.2f} {y - top:.2f}"
                     f"H{x + w:.2f}")
                out = path(d, stroke=fill, width=max(1.0, size * 0.062), cap="round")
                if idx:
                    out += idx.draw(x0 + hook * 0.16, y - top * 0.52)
                return out + rad.draw(x + lead + size * 0.10, y)

            boxes.append(Box(w, top + size * 0.10, rad.desc, draw))

    if not boxes:
        return Box(0.0, 0.0, 0.0, lambda x, y: "")
    total = sum(b.w for b in boxes)
    asc = max(b.asc for b in boxes)
    desc = max(b.desc for b in boxes)

    def draw(x, y, boxes=boxes):
        out, cx = [], x
        for b in boxes:
            out.append(b.draw(cx, y))
            cx += b.w
        return "".join(out)

    return Box(total, asc, desc, draw)


def math_box(expr: str, size: float, fill: str = TXT2) -> Box:
    return layout(parse_math(expr), size, fill)


def math_block(expr: str, size: float, fill: str = TXT2) -> tuple[str, float, float]:
    """Typeset `expr`; return (svg, w, h) with the origin at the top-left."""
    box = math_box(expr, size, fill)
    return box.draw(0, box.asc), box.w, box.asc + box.desc


# ── Art primitives ───────────────────────────────────────────────────────────

def _samples(f, x0, x1, n=180):
    """Sample f across [x0, x1]; a point the function cannot produce is None,
    which breaks the polyline rather than aborting the panel."""
    out = []
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        try:
            out.append((x, float(f(x))))
        except Exception:
            out.append((x, None))
    return out


def build_graph(el: dict) -> tuple[str, float, float]:
    """A coordinate grid panel carrying one or more plotted curves."""
    w, h = el.get("w", 250), el.get("h", 190)
    x0, x1 = el.get("xr", (-4, 4))
    y0, y1 = el.get("yr", (-4, 4))
    sx, sy = w / (x1 - x0), h / (y1 - y0)

    def X(x):
        return (x - x0) * sx

    def Y(y):
        return h - (y - y0) * sy

    g = []
    d = []
    k = math.ceil(x0)
    while k <= x1 + 1e-9:
        d.append(f"M{X(k):.1f} 0V{h:.1f}")
        k += 1
    k = math.ceil(y0)
    while k <= y1 + 1e-9:
        d.append(f"M0 {Y(k):.1f}H{w:.1f}")
        k += 1
    g.append(path("".join(d), stroke=GRID, width=0.7))

    ax, ay = X(0), Y(0)
    g.append(arrow(0, ay, w, ay))
    g.append(arrow(ax, h, ax, 0))
    for k in range(math.ceil(x0), int(x1) + 1):
        if k == 0 or not (2 < X(k) < w - 2):
            continue
        g.append(path(f"M{X(k):.1f} {ay - 3.5}V{ay + 3.5}", stroke=AXIS, width=1))
        if k % el.get("xtick", 2) == 0:
            g.append(label(X(k), ay + 13, f"\u2212{-k}" if k < 0 else str(k), 10))
    for k in range(math.ceil(y0), int(y1) + 1):
        if k == 0 or not (2 < Y(k) < h - 2):
            continue
        g.append(path(f"M{ax - 3.5} {Y(k):.1f}H{ax + 3.5}", stroke=AXIS, width=1))
        if k % el.get("ytick", 2) == 0:
            g.append(label(ax - 6, Y(k) + 3.5,
                           f"\u2212{-k}" if k < 0 else str(k), 10, anchor="end"))

    for spec in el.get("curves", []):
        if callable(spec):
            spec = {"f": spec}
        pts, run = [], []
        for x, y in _samples(spec["f"], x0, x1, spec.get("n", 200)):
            py = None if y is None else Y(y)
            if py is None or not (-2 <= py <= h + 2):
                if len(run) > 1:
                    pts.append(run)
                run = []
                continue
            run.append((X(x), min(max(py, 0.0), h)))
        if len(run) > 1:
            pts.append(run)
        for seg in pts:
            g.append(polyline(seg, stroke=spec.get("stroke", CURVE),
                              width=spec.get("width", 2.0),
                              dash=spec.get("dash")))
    for xv in el.get("vlines", []):
        g.append(path(f"M{X(xv):.1f} 0V{h:.1f}", stroke=CURVE, width=2.0))

    g.append(label(w - 7, ay - 6, "x", 12, italic=True, anchor="end"))
    g.append(label(ax + 7, 13, "y", 12, italic=True, anchor="start"))
    return "".join(g), w, h


def build_numberline(el: dict) -> tuple[str, float, float]:
    """A number line with shaded solution rays and open/closed endpoints."""
    w = el.get("w", 240)
    lo, hi = el.get("lo", -6), el.get("hi", 6)
    step = w / (hi - lo)
    pad, base = 14, 26

    def X(v):
        return (v - lo) * step

    g = [arrow(-pad, base, w + pad, base, stroke=AXIS, width=1.2)]
    g.insert(0, arrow(w + pad, base, -pad, base, stroke=AXIS, width=1.2))
    for i in range(hi - lo + 1):
        v = lo + i
        g.append(path(f"M{X(v):.1f} {base - 4}V{base + 4}", stroke=AXIS, width=1))
        if v % el.get("tick", 2) == 0:
            g.append(label(X(v), base + 16, f"\u2212{-v}" if v < 0 else str(v), 11))
    for a, b in el.get("shade", []):
        xa = -pad + 4 if a is None else X(a)
        xb = w + pad - 4 if b is None else X(b)
        g.append(path(f"M{xa:.1f} {base}H{xb:.1f}", stroke=CURVE, width=3.2))
    for v, kind in el.get("marks", []):
        g.append(f'<circle cx="{X(v):.1f}" cy="{base}" r="4.6" '
                 f'fill="{"#ffffff" if kind == "open" else CURVE}" '
                 f'stroke="{CURVE}" stroke-width="1.8"/>')
    h = base + 24
    if el.get("expr"):
        # Caption the line with the inequality it graphs, and drop the axis below it.
        svg, ew, eh = math_block(el["expr"], el.get("size", 18))
        g = [f'<g transform="translate({max(0.0, (w - ew) / 2):.1f},0)">{svg}</g>',
             f'<g transform="translate(0,{eh + 6:.1f})">' + "".join(g) + "</g>"]
        h += eh + 6
    return "".join(g), w + 2 * pad, h


def build_slab(el: dict) -> tuple[str, float, float]:
    """An extruded slab — front face, top face, right face — holding math."""
    size = el.get("size", 17)
    # Stack on measured ascent/descent, not a fixed multiple of the point size —
    # a line holding a fraction or a radical is much taller than a plain one and
    # would otherwise collide with its neighbour.
    boxes = [math_box(s, size) for s in el["lines"]]
    gap = size * 0.52
    inner_h = sum(b.asc + b.desc for b in boxes) + gap * (len(boxes) - 1)
    w = el.get("w", max(b.w for b in boxes) + size * 2.6)
    h = el.get("h", inner_h + size * 1.4)
    dx, dy = el.get("dx", 17), el.get("dy", -12)

    g = [f'<path d="M0 0L{dx} {dy}L{w + dx} {dy}L{w} 0Z" fill="#ffffff" '
         f'stroke="{EDGE}" stroke-width="1"/>',
         f'<path d="M{w} 0L{w + dx} {dy}L{w + dx} {h + dy}L{w} {h}Z" fill="#ffffff" '
         f'stroke="{EDGE}" stroke-width="1"/>',
         f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff" '
         f'stroke="{EDGE}" stroke-width="1.2"/>']
    y = (h - inner_h) / 2
    for b in boxes:
        y += b.asc
        g.append(b.draw((w - b.w) / 2, y))
        y += b.desc + gap
    return "".join(g), w + dx, h - dy


def build_equation(el: dict) -> tuple[str, float, float]:
    return math_block(el["expr"], el.get("size", 19), el.get("fill", TXT2))


def build_sets(el: dict) -> tuple[str, float, float]:
    """Nested number-system rings: R > Q > Z > W > N, irrationals outside Q."""
    w, h = el.get("w", 250), el.get("h", 176)
    names = el.get("names", ["\u211d", "\u211a", "\u2124", "W", "\u2115"])
    outside = el.get("outside", [])
    # The rings nest toward the lower-left rather than concentrically, which
    # opens a band down the right-hand side wide enough to hold the numbers
    # that live in R but not in Q.
    band = 84 if outside else 20
    g = []
    for i, nm in enumerate(names):
        ix, iy = 10 + i * 15, 10 + i * 13
        rx2, ry2 = w - band + 10 - i * 5, h - 10 - i * 11
        if rx2 - ix <= 12 or ry2 - iy <= 12:
            break
        g.append(f'<rect x="{ix}" y="{iy}" width="{rx2 - ix}" height="{ry2 - iy}" '
                 f'rx="11" fill="none" stroke="{EDGE if i == 0 else GRID}" '
                 f'stroke-width="{1.2 if i == 0 else 0.9}"/>')
        fam, _, _ = FONTS[font_runs(nm, False)[0][1]]
        g.append(f'<text x="{ix + 6}" y="{iy + 14}" font-family="{fam}" '
                 f'font-size="12" fill="{AXIS}">{esc(nm)}</text>')

    if outside:
        boxes = [math_box(s, 14, AXIS) for s in outside]
        gap = 9.0
        total = sum(b.asc + b.desc for b in boxes) + gap * (len(boxes) - 1)
        cx, y = w - band / 2 + 4, (h - total) / 2
        for b in boxes:
            y += b.asc
            g.append(b.draw(cx - b.w / 2, y))
            y += b.desc + gap
    return "".join(g), w, h


def build_cone(el: dict) -> tuple[str, float, float]:
    w, h = el.get("w", 104), el.get("h", 150)
    cx, cy, rx, ry = w / 2, h - 22, w / 2 - 4, 13
    g = [path(f"M{cx} 0L{cx - rx} {cy}", stroke=EDGE, width=1.3),
         path(f"M{cx} 0L{cx + rx} {cy}", stroke=EDGE, width=1.3),
         path(f"M{cx - rx} {cy}A{rx} {ry} 0 0 0 {cx + rx} {cy}", stroke=EDGE, width=1.3),
         path(f"M{cx - rx} {cy}A{rx} {ry} 0 0 1 {cx + rx} {cy}", stroke=DASH,
              width=1, dash="4 3"),
         path(f"M{cx} 0V{cy}", stroke=DASH, width=1, dash="4 3"),
         path(f"M{cx} {cy}L{cx + rx} {cy}", stroke=DASH, width=1, dash="4 3"),
         label(cx - 8, cy - h * 0.4, "h", 14, italic=True, anchor="end"),
         label(cx + rx / 2, cy + 16, "r", 14, italic=True)]
    return "".join(g), w, h


def build_cube(el: dict) -> tuple[str, float, float]:
    s = el.get("s", 102)
    dx, dy = el.get("dx", 32), el.get("dy", 25)
    g = [f'<rect x="0" y="{dy}" width="{s}" height="{s}" fill="#ffffff" '
         f'stroke="{EDGE}" stroke-width="1.3"/>',
         f'<path d="M0 {dy}L{dx} 0L{s + dx} 0L{s} {dy}Z" fill="#ffffff" '
         f'stroke="{EDGE}" stroke-width="1.3"/>',
         f'<path d="M{s} {dy}L{s + dx} 0L{s + dx} {s}L{s} {s + dy}Z" fill="#ffffff" '
         f'stroke="{EDGE}" stroke-width="1.3"/>',
         path(f"M{dx} {s}V{s}L{s + dx} {s}", stroke=DASH, width=0.9, dash="4 3"),
         path(f"M{dx} {dy}V{s + dy}", stroke=DASH, width=0.9, dash="4 3")]
    return "".join(g), s + dx, s + dy


# ── Statistics panels ────────────────────────────────────────────────────────
# The displays this course actually teaches. Each is driven by a dataset — the
# same numbers the lesson works with — never by a shape invented here.
#
# Ink budget applies as everywhere else: bars and boxes are outlined, never
# filled; the only solid ink is a dotplot's dots, which are glyph-sized.

def _num(v: float) -> str:
    """A tick label with a real minus sign and no trailing zeros."""
    return f"{v:g}".replace("-", "−")


def _nice_step(span: float, target: int) -> float:
    """A 1/2/2.5/5 x 10^k step giving roughly `target` ticks across `span`."""
    if span <= 0:
        return 1.0
    raw = span / max(1, target)
    mag = 10.0 ** math.floor(math.log10(raw))
    for m in (1, 2, 2.5, 5, 10):
        if raw <= m * mag:
            return m * mag
    return 10 * mag


def _window(data, lo, hi, step, pad=0.12) -> tuple[float, float, float]:
    """Frame `data` on a tick grid: pad it, then snap out to whole steps so the
    axis labels land on round numbers instead of wherever the data stopped."""
    span = (max(data) - min(data)) or (abs(data[0]) or 1.0)
    if lo is None:
        lo = min(data) - span * pad
    if hi is None:
        hi = max(data) + span * pad
    step = step or _nice_step(hi - lo, 6)
    return math.floor(lo / step) * step, math.ceil(hi / step) * step, step


def _axis_x(w, y, lo, hi, step, size=10) -> list[str]:
    g = [path(f"M0 {y:.1f}H{w:.1f}", stroke=AXIS, width=1.2)]
    k = math.ceil(lo / step - 1e-9) * step
    while k <= hi + 1e-9:
        x = (k - lo) / (hi - lo) * w
        g.append(path(f"M{x:.1f} {y - 3.5:.1f}V{y + 3.5:.1f}", stroke=AXIS, width=1))
        g.append(label(x, y + 15, _num(round(k, 6)), size))
        k += step
    return g


def _caption(g: list[str], w: float, h: float, el: dict) -> tuple[str, float, float]:
    """Hang the variable name under a panel, centred, if the element names one."""
    text = el.get("caption")
    if not text:
        return "".join(g), w, h
    b = math_box(text, el.get("csize", 13), AXIS)
    g.append(b.draw((w - b.w) / 2, h + b.asc + 4))
    return "".join(g), w, h + b.asc + b.desc + 4


def _five(data: list[float]) -> tuple[float, float, float, float, float]:
    """Min, Q1, median, Q3, max by the AP convention: the quartiles are the
    medians of the halves, with the overall median excluded from both when n
    is odd."""
    d = sorted(data)
    n = len(d)

    def med(a):
        m = len(a)
        return a[m // 2] if m % 2 else (a[m // 2 - 1] + a[m // 2]) / 2

    half = n // 2
    return d[0], med(d[:half]), med(d), med(d[half + n % 2:]), d[-1]


def build_dotplot(el: dict) -> tuple[str, float, float]:
    """One dot per observation, stacked at its own value."""
    data = sorted(float(v) for v in el["data"])
    w = el.get("w", 250)
    lo, hi, step = _window(data, el.get("lo"), el.get("hi"), el.get("step"))
    r = el.get("r", 3.8)
    # Leave air between stacked dots. Tangent circles merge into a bar once the
    # page skew compresses the column, and the count stops being readable.
    dy = 2 * r + 1.4

    def X(v):
        return (v - lo) / (hi - lo) * w

    # Stack by pixel column rather than by value: two readings a hundredth
    # apart are distinct numbers but the same dot, and would overprint.
    cols: dict[int, list[float]] = {}
    for v in data:
        cols.setdefault(round(X(v) / dy), []).append(v)
    tallest = max(len(c) for c in cols.values())
    base = 8 + tallest * dy

    g = []
    for vals in cols.values():
        cx = sum(X(v) for v in vals) / len(vals)
        for i in range(len(vals)):
            g.append(f'<circle cx="{cx:.1f}" cy="{base - r - i * dy:.1f}" '
                     f'r="{r}" fill="{CURVE}"/>')
    g += _axis_x(w, base, lo, hi, step)
    return _caption(g, w, base + 22, el)


def build_boxplot(el: dict) -> tuple[str, float, float]:
    """Five-number summary as a box and whiskers, with the 1.5 IQR rule
    applied: whiskers reach the most extreme value that is not an outlier and
    the outliers are plotted individually."""
    data = sorted(float(v) for v in el["data"])
    mn, q1, med, q3, mx = _five(data)
    iqr = q3 - q1
    if el.get("fences", True) and iqr > 0:
        lof, hif = q1 - 1.5 * iqr, q3 + 1.5 * iqr
        out = [v for v in data if v < lof or v > hif]
        inl = [v for v in data if lof <= v <= hif] or [mn, mx]
        wlo, whi = min(inl), max(inl)
    else:
        out, wlo, whi = [], mn, mx

    w = el.get("w", 250)
    lo, hi, step = _window(data, el.get("lo"), el.get("hi"), el.get("step"))
    bh = el.get("bh", 44)
    top, mid, bot = 6, 6 + bh / 2, 6 + bh

    def X(v):
        return (v - lo) / (hi - lo) * w

    g = [f'<rect x="{X(q1):.1f}" y="{top}" width="{max(1.0, X(q3) - X(q1)):.1f}" '
         f'height="{bh}" fill="none" stroke="{EDGE}" stroke-width="1.3"/>',
         path(f"M{X(med):.1f} {top}V{bot}", stroke=CURVE, width=2.2),
         path(f"M{X(wlo):.1f} {mid:.1f}H{X(q1):.1f}", stroke=EDGE, width=1.2),
         path(f"M{X(q3):.1f} {mid:.1f}H{X(whi):.1f}", stroke=EDGE, width=1.2),
         path(f"M{X(wlo):.1f} {top + 8:.1f}V{bot - 8:.1f}", stroke=EDGE, width=1.2),
         path(f"M{X(whi):.1f} {top + 8:.1f}V{bot - 8:.1f}", stroke=EDGE, width=1.2)]
    for v in out:
        g.append(f'<circle cx="{X(v):.1f}" cy="{mid:.1f}" r="3.2" fill="#ffffff" '
                 f'stroke="{CURVE}" stroke-width="1.4"/>')
    g += _axis_x(w, bot + 14, lo, hi, step)
    return _caption(g, w, bot + 36, el)


def build_histogram(el: dict) -> tuple[str, float, float]:
    """Equal-width bins, outlined and sharing edges, over a frequency axis."""
    data = sorted(float(v) for v in el["data"])
    w, h = el.get("w", 250), el.get("h", 150)
    nb = el.get("bins", min(8, max(4, round(math.sqrt(len(data))))))
    lo, hi, step = _window(data, el.get("lo"), el.get("hi"), el.get("step"), pad=0.0)
    bw = (hi - lo) / nb
    counts = [0] * nb
    for v in data:
        k = int((v - lo) / bw) if bw else 0
        counts[min(max(k, 0), nb - 1)] += 1
    top = max(counts) or 1
    ystep = 1 if top <= 6 else _nice_step(top, 5)

    def Y(c):
        return h - c / top * (h - 10)

    g = []
    k = 0.0
    while k <= top + 1e-9:
        g.append(path(f"M0 {Y(k):.1f}H{w:.1f}", stroke=GRID, width=0.7))
        g.append(label(-6, Y(k) + 3.5, _num(k), 10, anchor="end"))
        k += ystep
    for i, c in enumerate(counts):
        if not c:
            continue
        x0, x1 = i / nb * w, (i + 1) / nb * w
        g.append(f'<rect x="{x0:.1f}" y="{Y(c):.1f}" width="{x1 - x0:.1f}" '
                 f'height="{h - Y(c):.1f}" fill="#ffffff" stroke="{EDGE}" '
                 f'stroke-width="1.2"/>')
    g.append(path(f"M0 0V{h:.1f}", stroke=AXIS, width=1.2))
    g += _axis_x(w, h, lo, hi, step)
    return _caption(g, w, h + 22, el)


def build_scatter(el: dict) -> tuple[str, float, float]:
    """A scatterplot, with the least-squares line drawn through it. The line is
    fitted here from the same points — it is never passed in, so it cannot
    disagree with the cloud it sits on."""
    xs = [float(v) for v in el["x"]]
    ys = [float(v) for v in el["y"]]
    n = min(len(xs), len(ys))
    xs, ys = xs[:n], ys[:n]
    w, h = el.get("w", 250), el.get("h", 178)
    x0, x1, xstep = _window(xs, el.get("xlo"), el.get("xhi"), el.get("xstep"))
    y0, y1, ystep = _window(ys, el.get("ylo"), el.get("yhi"), el.get("ystep"))

    def X(v):
        return (v - x0) / (x1 - x0) * w

    def Y(v):
        return h - (v - y0) / (y1 - y0) * h

    g = []
    k = math.ceil(y0 / ystep - 1e-9) * ystep
    while k <= y1 + 1e-9:
        g.append(path(f"M0 {Y(k):.1f}H{w:.1f}", stroke=GRID, width=0.7))
        g.append(label(-6, Y(k) + 3.5, _num(round(k, 6)), 10, anchor="end"))
        k += ystep

    if el.get("lsrl", True) and n >= 3:
        mx, my = sum(xs) / n, sum(ys) / n
        sxx = sum((v - mx) ** 2 for v in xs)
        if sxx > 0:
            b = sum((xs[i] - mx) * (ys[i] - my) for i in range(n)) / sxx
            a = my - b * mx
            # Clip the line to the panel: an unclipped fit on a steep slope
            # runs off the top and reads as a stray rule across the page.
            pts = []
            for v in (x0, x1):
                yv = a + b * v
                if y0 <= yv <= y1:
                    pts.append((X(v), Y(yv)))
            for yv in (y0, y1):
                if b:
                    xv = (yv - a) / b
                    if x0 <= xv <= x1:
                        pts.append((X(xv), Y(yv)))
            if len(pts) >= 2:
                pts.sort()
                g.append(polyline([pts[0], pts[-1]], stroke=CURVE, width=1.8))

    for i in range(n):
        g.append(f'<circle cx="{X(xs[i]):.1f}" cy="{Y(ys[i]):.1f}" r="3.1" '
                 f'fill="#ffffff" stroke="{CURVE}" stroke-width="1.4"/>')
    g.append(path(f"M0 0V{h:.1f}H{w:.1f}", stroke=AXIS, width=1.2))
    g += _axis_x(w, h, x0, x1, xstep)
    return _caption(g, w, h + 22, el)


def build_normal(el: dict) -> tuple[str, float, float]:
    """A normal curve on a z axis, optionally with a region shaded — by hatch
    rather than by fill, which would blacken the sheet."""
    w, h = el.get("w", 250), el.get("h", 132)
    zlo, zhi = el.get("zr", (-3.4, 3.4))
    base = h - 20

    def X(z):
        return (z - zlo) / (zhi - zlo) * w

    def Y(z):
        return base - math.exp(-z * z / 2) * (base - 8)

    g = []
    lo, hi = el.get("shade", (None, None))
    if lo is not None or hi is not None:
        a = zlo if lo is None else max(lo, zlo)
        b = zhi if hi is None else min(hi, zhi)
        z = a
        while z <= b + 1e-9:
            g.append(path(f"M{X(z):.1f} {base:.1f}V{Y(z):.1f}", stroke=GRID, width=0.8))
            z += (zhi - zlo) / 90
        for zv in (a, b):
            g.append(path(f"M{X(zv):.1f} {base:.1f}V{Y(zv):.1f}", stroke=AXIS, width=1))

    g.append(polyline([(X(zlo + (zhi - zlo) * i / 160),
                        Y(zlo + (zhi - zlo) * i / 160)) for i in range(161)],
                      stroke=CURVE, width=2.0))
    g.append(path(f"M0 {base:.1f}H{w:.1f}", stroke=AXIS, width=1.2))
    for z in range(math.ceil(zlo), int(zhi) + 1):
        g.append(path(f"M{X(z):.1f} {base - 3.5:.1f}V{base + 3.5:.1f}",
                      stroke=AXIS, width=1))
    # Label in sigmas when the element names a parameter, in z otherwise.
    mu, sd = el.get("mu"), el.get("sd")
    for z in range(math.ceil(zlo), int(zhi) + 1):
        txt = _num(round(mu + z * sd, 6)) if mu is not None and sd else _num(z)
        g.append(label(X(z), base + 15, txt, 10))
    g.append(path(f"M{X(0):.1f} {base:.1f}V{Y(0):.1f}", stroke=DASH,
                  width=1, dash="4 3"))
    return _caption(g, w, base + 22, el)


BUILDERS = {
    "equation": build_equation,
    "slab": build_slab,
    "graph": build_graph,
    "numberline": build_numberline,
    "sets": build_sets,
    "cone": build_cone,
    "cube": build_cube,
    "dotplot": build_dotplot,
    "boxplot": build_boxplot,
    "histogram": build_histogram,
    "scatter": build_scatter,
    "normal": build_normal,
}


# ── Placement ────────────────────────────────────────────────────────────────

def place(el: dict) -> tuple[str, tuple[float, float, float, float]]:
    """Render one element and wrap it in its placement transform.

    `tilt` rotates and `skew` applies a 2x2 matrix, both about the element's
    own centre so the anchor point still means what it says.
    """
    body, w, h = BUILDERS[el["type"]](el)
    x, y = el.get("at", (0, 0))
    tf = f"translate({x:.1f},{y:.1f})"
    inner = ""
    if el.get("tilt"):
        inner = (f"translate({w / 2:.1f},{h / 2:.1f}) rotate({el['tilt']}) "
                 f"translate({-w / 2:.1f},{-h / 2:.1f})")
    elif el.get("skew"):
        a, b, c, d = el["skew"]
        inner = (f"translate({w / 2:.1f},{h / 2:.1f}) matrix({a},{b},{c},{d},0,0) "
                 f"translate({-w / 2:.1f},{-h / 2:.1f})")
    return f'<g transform="{tf} {inner}">{body}</g>', (x, y, w, h)


def _overlaps(r, s, pad=14):
    return not (r[0] + r[2] + pad < s[0] or s[0] + s[2] + pad < r[0] or
                r[1] + r[3] + pad < s[1] or s[1] + s[3] + pad < r[1])


SKEWS = [(1, 0.05, -0.10, 0.99), (0.97, 0.16, -0.30, 0.94),
         (0.98, -0.13, 0.26, 0.95), (0.99, 0.08, 0.18, 0.97),
         (0.96, -0.10, -0.22, 0.96)]
TILTS = [-3, 2, -2, 3, -4, 2, 4, -2]


def auto_place(elements: list[dict], seed: int = 7) -> list[dict]:
    """Scatter elements that carry no explicit `at`, keeping them off the title
    block and off each other, and varying the 3-D treatment so the page never
    looks like one uniform tilt was applied to everything."""
    rng = random.Random(seed)
    taken = [(TITLE_BAND[0], TITLE_BAND[1],
              TITLE_BAND[2] - TITLE_BAND[0], TITLE_BAND[3] - TITLE_BAND[1])]
    out = []
    for i, el in enumerate(elements):
        el = dict(el)
        if "tilt" not in el and "skew" not in el:
            if el["type"] in ("graph", "slab", "sets", "dotplot", "boxplot",
                              "histogram", "scatter", "normal"):
                el["skew"] = SKEWS[i % len(SKEWS)]
            else:
                el["tilt"] = TILTS[i % len(TILTS)]
        if el.get("at"):
            out.append(el)
            taken.append((*el["at"], *BUILDERS[el["type"]](el)[1:]))
            continue
        _, w, h = BUILDERS[el["type"]](el)
        best = None
        for _ in range(400):
            x = rng.uniform(40, max(41, W - 40 - w))
            y = rng.uniform(46, max(47, H - 46 - h))
            r = (x, y, w, h)
            if any(_overlaps(r, s) for s in taken):
                continue
            best = r
            break
        if best is None:
            best = (rng.uniform(40, max(41, W - 40 - w)),
                    rng.uniform(46, max(47, H - 46 - h)), w, h)
        el["at"] = (round(best[0], 1), round(best[1], 1))
        taken.append(best)
        out.append(el)
    return out


# ── Title block ──────────────────────────────────────────────────────────────

def fit_size(text: str, role: str, start: float, max_w: float) -> float:
    size = start
    while size > 12 and measure(text, role, size) > max_w:
        size -= 1
    return size


def title_block(unit_no: int, unit_title: str, teacher: str = "Shepherd") -> str:
    def haloed(svg: str) -> str:
        halo = svg.replace("<text ", '<text stroke="#ffffff" stroke-width="7" '
                                     'stroke-linejoin="round" ', 1)
        return halo + svg

    def line(text, role, size, y, fill):
        fam, style, _ = FONTS[role]
        return (f'<text x="{W / 2}" y="{y}" font-family="{fam}" font-style="{style}" '
                f'font-size="{size:.1f}" fill="{fill}" text-anchor="middle">'
                f'{esc(text)}</text>')

    unit_line = f"Unit {unit_no}:  {unit_title}"
    s_course = fit_size(COURSE, "serif", 94, W - 260)
    s_unit = fit_size(unit_line, "serif", 42, W - 210)
    s_name = fit_size(teacher, "script", 58, W - 340)

    rule_w = max(measure(COURSE, "serif", s_course),
                 measure(unit_line, "serif", s_unit)) + 46
    rule_w = min(rule_w, W - 180)
    ra, rb = (W - rule_w) / 2, (W + rule_w) / 2

    g = ['<g id="title">', haloed(line(COURSE, "serif", s_course, 516, TXT))]
    for y in (540, 606):
        g.append(path(f"M{ra:.0f} {y}H{rb:.0f}", stroke="#ffffff", width=7))
        g.append(path(f"M{ra:.0f} {y}H{rb:.0f}", stroke=EDGE, width=1.4))
    g.append(haloed(line(unit_line, "serif", s_unit, 588, TXT2)))
    g.append(haloed(line(teacher, "script", s_name, 672, TXT)))
    sw = measure(teacher, "script", s_name) * 0.92
    sa, sb = W / 2 - sw / 2, W / 2 + sw / 2
    swoosh = f"M{sa:.0f} 692Q{W / 2:.0f} 682 {sb:.0f} 692"
    g.append(path(swoosh, stroke="#ffffff", width=8))
    g.append(path(swoosh, stroke=EDGE, width=2, cap="round"))
    g.append("</g>")
    return "".join(g)


# ── Page assembly ────────────────────────────────────────────────────────────

def page(elements: list[dict], unit_no: int, unit_title: str,
         teacher: str) -> str:
    art = "".join(place(el)[0] for el in elements)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="8.5in" height="11in" '
            f'viewBox="0 0 {W} {H}">'
            f'<rect width="{W}" height="{H}" fill="#ffffff"/>'
            f'<rect x="18" y="18" width="{W - 36}" height="{H - 36}" fill="none" '
            f'stroke="{FRAME}" stroke-width="1.2"/>'
            f'<g id="art">{art}</g>'
            f'{title_block(unit_no, unit_title, teacher)}'
            f'</svg>')


# ── Unit metadata ────────────────────────────────────────────────────────────

# Both definition forms are live in this course: units 02–09 use \newcommand,
# unit01's ten lesson plans use \def. Matching only the first would silently
# title unit01's cover "unit01" via the fallback in unit_metadata.
_UNIT_NAME_RE = re.compile(
    r"\\(?:newcommand\{\\UnitNumberName\}|def\\UnitNumberName)\{(.+?)\}\s*$", re.M)


def unit_metadata(unit_dir: Path) -> tuple[int, str]:
    """Unit number from the directory name, title from \\UnitNumberName."""
    m = re.search(r"(\d+)$", unit_dir.name)
    number = int(m.group(1)) if m else 0
    title = ""
    for tex in sorted(unit_dir.glob("lesson*/main.tex")):
        mm = _UNIT_NAME_RE.search(tex.read_text(errors="ignore"))
        if not mm:
            continue
        raw = mm.group(1)
        raw = re.sub(r"\\(quad|qquad|,|;|!)", " ", raw)
        raw = raw.replace("---", "\u2014").replace("--", "\u2013")
        raw = re.sub(r"\s+", " ", raw).strip()
        title = re.sub(r"^Unit\s*\d+\s*[:.]?\s*", "", raw).strip()
        break
    return number, title or unit_dir.name


# ── Auto-discovery ───────────────────────────────────────────────────────────
# Used when a unit has no hand-tuned spec. Everything it emits is lifted from
# the unit's own sources — nothing is invented.

_SAFE = {"x": 0, "abs": abs, "sqrt": math.sqrt, "exp": math.exp,
         "log": math.log, "pow": pow, "sin": math.sin, "cos": math.cos,
         "pi": math.pi, "e": math.e, "max": max, "min": min}


# An expression that held one of these was a fill-in-the-blank prompt, not a
# statement. Stripping the macro would leave "y - 1 = (x - )" on the cover, so
# reject the whole expression instead.
_HOLE = re.compile(r"\\(?:blank|writeline|ans|underline|rule|hspace|dotfill)\b")

# A statistics source is full of prompts and scenario settings that scrape as
# valid equations but say nothing on a cover.
#
#   "= Q_3 + 1.5(IQR)"   the answer half of a prompt whose left side was prose
#   "P(D > 0.20) ="      the prompt half, with the answer left blank
#   "p_1 = 0.72"         a parameter being set up, not a result worth printing
#   "r^2 = 0.94"         likewise — and a unit states a dozen of them
#   "t^* = 2.048"        a critical value read off a table, once per lesson
_FRAGMENT = re.compile(r"^\s*=|=\s*$")
_SETTING = re.compile(
    r"^\s*[A-Za-z]\w*(?:[_^]\{?[\w*]+\}?)*\s*=\s*-?[\d.]+\s*$")


def _clean_tex(s: str) -> str:
    s = re.sub(r"\\(?:emph|textbf|text|mathbf|mathrm)\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\\(?:displaystyle|left|right|,|;|!)", " ", s)
    s = s.replace("\\dfrac", "\\frac").replace("\\tfrac", "\\frac")
    return re.sub(r"\s+", " ", s).strip()


def _space_ops(s: str) -> str:
    """Put air around relations and binary operators the source ran together,
    so a scraped `3|x+1|-2=10` still sets like mathematics."""
    s = re.sub(r"\s*(=|\\le\b|\\ge\b|\\ne\b|<|>)\s*", r" \1 ", s)
    s = re.sub(r"\s*\+\s*", " + ", s)
    s = re.sub(r"(?<=[\w)\}\|])\s*-\s*(?=[\w(\\|])", " - ", s)
    return re.sub(r"\s+", " ", s).strip()


_DEFN = re.compile(r"^\s*(?:[a-zA-Z]\s*\(\s*[a-z]\s*\)|y)\s*=\s*(.+?)\s*$")


def _tex_to_py(rhs: str) -> str | None:
    """Turn a TeX right-hand side into a Python expression in x, or None."""
    s = rhs
    s = re.sub(r"\\frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", s)
    s = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", s)
    s = re.sub(r"\|([^|]+)\|", r"abs(\1)", s)
    s = s.replace("\\cdot", "*").replace("\u2212", "-")
    s = re.sub(r"\^\{([^{}]+)\}", r"**(\1)", s)
    s = re.sub(r"\^(-?\w)", r"**(\1)", s)
    if "\\" in s or "{" in s or "}" in s:
        return None
    # Hide function names behind control characters so the implicit-product
    # rules below cannot chew through "abs(" and turn it into "ab*s*(".
    funcs = ("abs", "sqrt", "exp", "log", "pow", "min", "max")
    for i, fn in enumerate(funcs):
        s = s.replace(fn + "(", chr(1 + i) + "(")
    s = re.sub(r"(\d)\s*(?=[\x01-\x07])", r"\1*", s)    # 3abs(..) -> 3*abs(..)
    s = re.sub(r"(\d)\s*([a-zA-Z(])", r"\1*\2", s)      # 2x -> 2*x, 3( -> 3*(
    s = re.sub(r"\)\s*\(", r")*(", s)
    s = re.sub(r"([a-zA-Z])\s*\(", r"\1*(", s)          # x(x+1) -> x*(x+1)
    for i, fn in enumerate(funcs):
        s = s.replace(chr(1 + i) + "(", fn + "(")
    if any(nm not in _SAFE for nm in re.findall(r"[A-Za-z_]\w*", s)):
        return None
    return s


def _compile_rhs(rhs: str):
    s = _tex_to_py(rhs)
    if s is None:
        return None
    try:
        fn = eval(f"lambda x: ({s})", {"__builtins__": {}}, dict(_SAFE))
        vals = [fn(p) for p in (-2.5, -1.0, 0.0, 1.0, 2.5)]
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in vals):
            return None
        if max(vals) - min(vals) < 1e-9:            # a constant is not a graph
            return None
        return fn
    except Exception:
        return None


def _auto_range(fn, x0=-5.0, x1=5.0) -> tuple[int, int]:
    """Pick a y-window that actually frames the curve."""
    vals = []
    for i in range(81):
        try:
            v = float(fn(x0 + (x1 - x0) * i / 80))
            if math.isfinite(v):
                vals.append(v)
        except Exception:
            pass
    if not vals:
        return (-6, 6)
    lo, hi = max(min(vals), -24.0), min(max(vals), 24.0)
    if hi - lo < 8:
        mid = (hi + lo) / 2
        lo, hi = mid - 5, mid + 5
    pad = (hi - lo) * 0.12
    return (int(math.floor(lo - pad)), int(math.ceil(hi + pad)))


# ── Datasets ─────────────────────────────────────────────────────────────────
# The unit of discoverable content in a statistics course is the dataset, not
# the equation. Algebra writes its content down as a rule — f(x) = x^2 - 3 —
# and a cover can plot it directly. This course writes its content down as
# numbers in a table, and the display is what the lesson builds from them, so
# the scanner reads the numbers and the builders draw the display.

_CELL_JUNK = re.compile(r"\\[a-zA-Z]+\s*|[$\\{}~]|\\%|%")
_NUMBER_RE = re.compile(r"-?\d+(?:\.\d+)?")


def _cells_to_numbers(cells: list[str]) -> list[float]:
    """The trailing run of purely numeric cells in a row. Tables here lead with
    a label column — "Height & 55 & 60 & ..." — so a row is read from the right
    and stops at the first cell that is not a bare number."""
    vals: list[float] = []
    for c in reversed(cells):
        c = _CELL_JUNK.sub("", c).strip()
        if not _NUMBER_RE.fullmatch(c):
            break
        vals.append(float(c))
    vals.reverse()
    return vals


def _is_scale(v: list[float]) -> bool:
    """An arithmetic run is an axis scale or a set of bin edges, not data."""
    if len(v) < 3:
        return False
    d = {round(v[i + 1] - v[i], 6) for i in range(len(v) - 1)}
    return len(d) == 1 and 0 not in d


def _usable(v: list[float], lo=5, hi=40) -> bool:
    return lo <= len(v) <= hi and max(v) > min(v) and not _is_scale(v)


def _datasets(src: str) -> tuple[list[list[float]], list[tuple[list, list]]]:
    """Univariate datasets and bivariate pairs, in document order.

    A tabular that yields exactly two equal-length numeric rows is bivariate —
    that is how this course lays out paired data, one variable per row — and
    becomes a scatterplot. Everything else is univariate.
    """
    uni: list[list[float]] = []
    pairs: list[tuple[list, list]] = []
    seen: set[tuple] = set()

    def take(v):
        key = tuple(v)
        if key in seen or not _usable(v):
            return False
        seen.add(key)
        return True

    # tabularx is the workhorse here; plain tabular is the exception.
    for m in re.finditer(r"\\begin\{tabular[xy]?\}(.+?)\\end\{tabular[xy]?\}",
                         src, re.S):
        rows = []
        for row in m.group(1).split(r"\\"):
            row = re.sub(r"\\(?:hline|toprule|midrule|bottomrule)", " ", row)
            if "&" not in row:
                continue
            v = _cells_to_numbers(row.split("&"))
            if _usable(v):
                rows.append(v)
        if len(rows) == 2 and len(rows[0]) == len(rows[1]) and \
                tuple(rows[0]) not in seen and tuple(rows[1]) not in seen:
            seen.add(tuple(rows[0]))
            seen.add(tuple(rows[1]))
            pairs.append((rows[0], rows[1]))
        else:
            for v in rows:
                if take(v):
                    uni.append(v)

    # Loose comma-separated lists, the other way this course states a dataset.
    for m in re.finditer(r"(?:\d+(?:\.\d+)?\s*,\s*){4,}\d+(?:\.\d+)?", src):
        v = [float(t) for t in _NUMBER_RE.findall(m.group(0))]
        if take(v):
            uni.append(v)
    return uni, pairs


def _admits(v: list[float]) -> list[str]:
    """Which displays this dataset can honestly carry. A single dataset usually
    admits several — the course itself shows one small dataset as a dotplot, a
    boxplot and a histogram in the same lesson — so the page picks for variety
    rather than pinning each dataset to one best fit."""
    n = len(v)
    ok = []
    if n <= 20:                       # beyond this the dots stop being countable
        ok.append("dotplot")
    if n >= 8:                        # a five-number summary needs some data
        ok.append("boxplot")
    if n >= 10:                       # and bins need more still
        ok.append("histogram")
    return ok


def _build_display(kind: str, v: list[float]) -> dict:
    if kind == "histogram":
        return {"type": "histogram", "data": v, "w": 244, "h": 148}
    return {"type": kind, "data": v, "w": 244}


def discover(unit_dir: Path, want: int = 13) -> list[dict]:
    tex = sorted(unit_dir.glob("lesson*/notes/main.tex")) + \
          sorted(unit_dir.glob("lesson*/activity/main.tex")) + \
          sorted(unit_dir.glob("lesson*/homework/main.tex")) + \
          sorted(unit_dir.glob("lesson*/warmup/main.tex"))
    blobs = [p.read_text(errors="ignore") for p in tex]
    src = "\n".join(blobs)

    # ── Equations: every inline $...$ that states something ──────────────────
    eqs, seen_e = [], set()
    for m in re.finditer(r"\$([^$]{5,60})\$", src):
        raw = m.group(1)
        if _HOLE.search(raw) or "\\begin" in raw or "&" in raw:
            continue
        s = _space_ops(_clean_tex(raw))
        if "=" not in s or len(s) > 42:
            continue
        if re.search(r"\\(?!frac|sqrt|pm|ne|le|ge|cdot|pi|times|to|mp|div)", s):
            continue
        if _FRAGMENT.search(s) or _SETTING.match(s):
            continue
        key = re.sub(r"\s+", "", s)
        if key in seen_e or len(key) < 7:
            continue
        # Also reject a statement whose shape has already been used: a unit
        # states H_0: p = 0.30, then 0.40, then 0.45, and printing all four
        # fills the page with one sentence said four ways.
        shape = re.sub(r"-?\d+(?:\.\d+)?", "#", key)
        if shape in seen_e:
            continue
        seen_e.add(key)
        seen_e.add(shape)
        eqs.append(s)

    # ── Data displays: the unit's own datasets, drawn the way it draws them ──
    elements: list[dict] = []
    uni, pairs = _datasets(src)
    # Take the two scatters from opposite ends of the unit. Adjacent pairs are
    # usually the notes' worked example and the homework's echo of it —
    # different numbers, but they draw as the same picture.
    picks = [pairs[0], pairs[len(pairs) // 2]] if len(pairs) >= 2 else pairs[:1]
    for xs, ys in picks:
        elements.append({"type": "scatter", "x": xs, "y": ys,
                         "w": 244, "h": 174})
    # Deal the datasets out across the display types, one type at a time, so a
    # unit whose tables are all the same size still gets a varied page instead
    # of five identical strips.
    spare = list(uni)
    while len(elements) < 5 and spare:
        progress = False
        for kind in ("dotplot", "boxplot", "histogram"):
            pick = next((v for v in spare if kind in _admits(v)), None)
            if pick is None or len(elements) >= 5:
                continue
            spare.remove(pick)
            elements.append(_build_display(kind, pick))
            progress = True
        if not progress:
            break

    # ── A normal curve, if the unit works with one ──────────────────────────
    # \b before the z matters: without it "quiz scores" reads as "z score" and
    # a unit that never mentions the normal model gets a normal curve.
    if re.search(r"[Nn]ormal (?:distribution|curve|model)|\bz\s*-?\s*scores?\b|"
                 r"[Ee]mpirical [Rr]ule", src):
        elements.append({"type": "normal", "w": 236,
                         "shade": (-1, 1) if "Empirical" in src else (1, None)})

    # ── Graphs: from explicit function definitions, f(x) = ... or y = ... ────
    # Read the definitions rather than the TikZ, because units draw their
    # curves half a dozen different ways but always write the rule down.
    used, seen_f = set(), set()
    for s in eqs:
        if seen_f and len(seen_f) >= 3:
            break
        m = _DEFN.match(s)
        if not m:
            continue
        fn = _compile_rhs(m.group(1))
        if fn is None:
            continue
        key = re.sub(r"\s+", "", m.group(1))
        if key in seen_f:
            continue
        seen_f.add(key)
        used.add(s)
        y0, y1 = _auto_range(fn)
        elements.append({"type": "graph", "w": 236, "h": 176,
                         "xr": (-5, 5), "yr": (y0, y1),
                         "ytick": max(2, round((y1 - y0) / 6)),
                         "curves": [{"f": fn}]})
    eqs = [s for s in eqs if s not in used]

    # ── Slabs: worked solves where the unit has them, single identities where
    # it does not. Never stack unrelated lines into a fake "solve". ──────────
    slabs = []
    for m in re.finditer(r"\\begin\{work\}(.+?)\\end\{work\}", src, re.S):
        if _HOLE.search(m.group(1)):
            continue
        lines = []
        for ln in m.group(1).split("\\\\"):
            ln = _space_ops(_clean_tex(ln).replace("&", ""))
            ln = re.sub(r"\\text\{[^{}]*\}", "", ln).strip()
            if ln and 3 < len(ln) < 30 and "\\" not in re.sub(
                    r"\\(frac|sqrt|pm|ne|le|ge|cdot|pi|times|div)", "", ln):
                lines.append(ln)
        if len(lines) >= 2:
            slabs.append(lines[:3])
    for lines in slabs[:2]:
        elements.append({"type": "slab", "lines": lines, "size": 16})
    for s in [e for e in eqs if 12 <= len(e) <= 30][:2 - len(slabs[:2])]:
        elements.append({"type": "slab", "lines": [s], "size": 17})
        used.add(s)
    eqs = [s for s in eqs if s not in used]

    # ── A number line, if the unit graphs solution sets ──────────────────────
    if re.search(r"\\numline|\\begin\{tikzpicture\}[^\\]*\\draw\[<->", src):
        elements.append({"type": "numberline", "w": 226, "lo": -5, "hi": 5,
                         "shade": [(None, -2)], "marks": [(-2, "closed")]})

    # ── The rest of the page is loose equations ─────────────────────────────
    for s in eqs[:max(0, want - len(elements))]:
        elements.append({"type": "equation", "expr": s, "size": 19})
    return elements[:want]


# ── Spec loading ─────────────────────────────────────────────────────────────

def load_spec(path: Path):
    # No .pyc: the spec lives in the source tree beside the PDF it describes,
    # and a __pycache__ has no business appearing in a unit directory.
    prev, sys.dont_write_bytecode = sys.dont_write_bytecode, True
    try:
        spec = importlib.util.spec_from_file_location("cover_spec", path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    finally:
        sys.dont_write_bytecode = prev


# ── Main ─────────────────────────────────────────────────────────────────────

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("unit", nargs="?", help="unit directory, e.g. unit01")
    ap.add_argument("-o", "--out", help="output PDF (default UNIT/binder_cover/main.pdf)")
    ap.add_argument("--spec", help="content spec (default UNIT/binder_cover/spec.py)")
    ap.add_argument("--svg-out", help="also write cover_front.svg / cover_back.svg here")
    ap.add_argument("--teacher", default="Shepherd")
    ap.add_argument("--seed", type=int, default=7, help="auto-layout jitter seed")
    ap.add_argument("--check-fonts", action="store_true",
                    help="preflight the fonts and cairosvg, then exit")
    args = ap.parse_args(argv)

    missing = check_fonts()
    if args.check_fonts:
        for m in missing:
            print("missing font:", m, file=sys.stderr)
        if missing:
            print("install the OTFs above where the OS font service can see "
                  "them — see the README", file=sys.stderr)
        else:
            print("all cover fonts present")
        try:
            import cairosvg                                   # noqa: F401
            print("cairosvg present")
        except ImportError as e:
            print(f"missing cairosvg: {e} — python3 -m pip install --user "
                  "cairosvg", file=sys.stderr)
            return 1
        return 1 if missing else 0
    if missing:
        print("!  cover.py: missing fonts — output will fall back to system faces:",
              file=sys.stderr)
        for m in missing:
            print("   ", m, file=sys.stderr)
    if not args.unit:
        ap.error("the unit directory is required")

    unit_dir = Path(args.unit).resolve()
    if not unit_dir.is_dir():
        print(f"!  no such unit directory: {unit_dir}", file=sys.stderr)
        return 1

    number, title = unit_metadata(unit_dir)
    spec_path = Path(args.spec) if args.spec else unit_dir / "binder_cover" / "spec.py"
    teacher = args.teacher

    if spec_path.exists():
        mod = load_spec(spec_path)
        elements = list(getattr(mod, "ELEMENTS", []))
        title = getattr(mod, "TITLE", title)
        teacher = getattr(mod, "TEACHER", teacher)
        source = f"spec {spec_path.name}"
    else:
        elements = discover(unit_dir)
        source = "auto-discovery"
    # A unit with no mathematics in it — Unit 3, Collecting Data, is entirely
    # study design — is not a failure. Set the title on a clean sheet and say
    # so, rather than breaking the build or inventing statistics it never
    # taught. Hand-tune binder_cover/spec.py to give such a unit its own art.
    if not elements:
        print(f"!  {unit_dir.name}: no cover content discovered — setting the "
              f"title block alone. Add {unit_dir.name}/binder_cover/spec.py to "
              f"give it art.", file=sys.stderr)
    elements = auto_place(elements, seed=args.seed)

    svg = page(elements, number, title, teacher)

    if args.svg_out:
        d = Path(args.svg_out)
        d.mkdir(parents=True, exist_ok=True)
        (d / "cover.svg").write_text(svg)

    out = Path(args.out) if args.out else unit_dir / "binder_cover" / "main.pdf"
    out.parent.mkdir(parents=True, exist_ok=True)

    # Front and back are the same sheet, so the one rendered page is simply
    # duplicated rather than laid out twice.
    import cairosvg
    with tempfile.TemporaryDirectory() as td:
        one = Path(td) / "page.pdf"
        cairosvg.svg2pdf(bytestring=svg.encode(), write_to=str(one))
        subprocess.run(["pdfunite", str(one), str(one), str(out)], check=True)

    print(f"\u2713  Binder cover   \u2192 {out}  "
          f"(Unit {number}: {title}; {len(elements)} elements from {source})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
