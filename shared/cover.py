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

COURSE = "Statistics"

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
    "mu": "\u03bc", "sigma": "\u03c3",
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
    size = el.get("csize", 13)
    # "Sleep (hr)" is prose and sets upright; "\bar{x}" is mathematics and goes
    # through the math typesetter, which would otherwise italicise every word.
    if not re.search(r"[\\^_$]", text):
        g.append(label(w / 2, h + size + 3, text, size, AXIS))
        return "".join(g), w, h + size + 6
    b = math_box(text, size, AXIS)
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


def build_tally(el: dict) -> tuple[str, float, float]:
    """A frequency table mid-count: category labels down the left, tally marks
    in groups of five on the right — the four uprights and the diagonal that
    closes the gate. This is Topic 1.3's table exactly as the notes draw it."""
    rows = el["rows"]                       # [(label, count), ...]
    w = el.get("w", 215)
    col = el.get("col", 72)                 # label column width
    rh = el.get("rh", 29)
    hh = 26                                 # header band
    h = hh + rh * len(rows)

    g = [f'<rect x="0" y="0" width="{w}" height="{h}" fill="#ffffff" '
         f'stroke="{EDGE}" stroke-width="1.3"/>',
         path(f"M0 {hh}H{w}", stroke=EDGE, width=1.1),
         path(f"M{col} 0V{h}", stroke=EDGE, width=1.1),
         label(col / 2, 17, el.get("h1", "Pet"), 12),
         label(col + (w - col) / 2, 17, el.get("h2", "Tally"), 12)]

    y = hh
    for name, count in rows:
        cy = y + rh / 2
        g.append(label(col / 2, cy + 4, name, 12, fill=TXT2))
        x = col + 12
        left = count
        while left > 0:
            k = min(5, left)
            left -= k
            n_up = 4 if k == 5 else k
            for i in range(n_up):
                g.append(path(f"M{x + i * 5.5:.1f} {cy - 7:.1f}V{cy + 7:.1f}",
                              stroke=CURVE, width=1.5, cap="round"))
            if k == 5:
                g.append(path(f"M{x - 3:.1f} {cy + 6:.1f}"
                              f"L{x + 3 * 5.5 + 3:.1f} {cy - 6:.1f}",
                              stroke=CURVE, width=1.5, cap="round"))
            x += n_up * 5.5 + 10
        y += rh
        if y < h - 1:
            g.append(path(f"M0 {y}H{w}", stroke=GRID, width=0.8))
    return _caption(g, w, h, el)


def build_split(el: dict) -> tuple[str, float, float]:
    """Discrete vs. continuous, side by side: a lollipop plot against a smooth
    curve — Topic 1.2's distinction drawn rather than defined."""
    w, h = el.get("w", 300), el.get("h", 116)
    half = (w - 26) / 2
    base = h - 22
    amp = base - 12
    g = []

    # Left: discrete — stems with dots, a roughly mound-shaped count.
    heights = el.get("bars", [0.14, 0.34, 0.62, 0.86, 1.0, 0.78, 0.52, 0.28, 0.12])
    g.append(path(f"M0 {base}H{half:.1f}", stroke=AXIS, width=1.2))
    for i, f in enumerate(heights):
        x = half * (i + 0.5) / len(heights)
        top = base - amp * f
        g.append(path(f"M{x:.1f} {base}V{top:.1f}", stroke=CURVE, width=1.6))
        g.append(f'<circle cx="{x:.1f}" cy="{top:.1f}" r="2.6" fill="{CURVE}"/>')
    g.append(label(half / 2, base + 15, "discrete", 12))

    # Right: continuous — the same mound with the gaps closed.
    x1 = half + 26
    g.append(path(f"M{x1:.1f} {base}H{w:.1f}", stroke=AXIS, width=1.2))
    pts = []
    for i in range(97):
        z = -2.9 + 5.8 * i / 96
        pts.append((x1 + half * i / 96, base - amp * math.exp(-z * z / 2)))
    g.append(polyline(pts, stroke=CURVE, width=2.0))
    g.append(label(x1 + half / 2, base + 15, "continuous", 12))
    return _caption(g, w, h, el)


def build_meme(el: dict) -> tuple[str, float, float]:
    """The normal/paranormal distribution joke: a normal curve with a ghost
    haunting the right half. Drawn in the sheet's own line weight, white-filled
    only where the ghost occludes the curve."""
    w = el.get("w", 250)
    bh = el.get("h", 104)                   # curve area height
    amp = bh - 12
    g = []

    # The curve, on a ticked base line.
    pts = []
    for i in range(121):
        z = -3.2 + 6.4 * i / 120
        pts.append((w * i / 120, bh - amp * math.exp(-z * z / 2)))
    g.append(polyline(pts, stroke=CURVE, width=2.0))
    g.append(path(f"M0 {bh}H{w}", stroke=AXIS, width=1.2))
    for i in range(1, 12):
        x = w * i / 12
        g.append(path(f"M{x:.1f} {bh - 3:.1f}V{bh + 3:.1f}", stroke=AXIS, width=1))

    # The ghost, centred under the peak, looking to its half of the page.
    # Small enough that the curve's peak clears its dome — white-filled, it
    # would otherwise swallow the very shape it is haunting.
    gx, r = w / 2, 17
    yt = bh - amp + 34                      # top of the dome, under the curve
    yb = bh - 4
    scallop = 2 * r / 3
    d = (f"M{gx - r:.1f} {yt + r:.1f}"
         f"A{r} {r} 0 0 1 {gx + r:.1f} {yt + r:.1f}"
         f"L{gx + r:.1f} {yb:.1f}")
    for i in range(3):                      # wavy hem, right to left
        x0 = gx + r - scallop * i
        d += (f"Q{x0 - scallop / 2:.1f} {yb - 9:.1f} "
              f"{x0 - scallop:.1f} {yb:.1f}")
    d += "Z"
    g.append(path(d, stroke=CURVE, width=2.0, fill="#ffffff"))
    # A hand on the curve, as if peeking over it.
    g.append(path(f"M{gx + r - 2:.1f} {yt + r + 8:.1f}"
                  f"Q{gx + r + 10:.1f} {yt + r + 3:.1f} "
                  f"{gx + r + 8:.1f} {yt + r + 13:.1f}",
                  stroke=CURVE, width=1.8, cap="round"))
    # Side-eye to the right, and a small worried mouth.
    for ex in (gx - 3, gx + 6):
        g.append(f'<ellipse cx="{ex:.1f}" cy="{yt + r * 0.75:.1f}" rx="2.1" '
                 f'ry="3.3" fill="{CURVE}"/>')
    g.append(f'<ellipse cx="{gx + 2.5:.1f}" cy="{yt + r * 1.35:.1f}" rx="2.8" '
             f'ry="3.8" fill="none" stroke="{CURVE}" stroke-width="1.5"/>')

    # The caption halves, then the punchline.
    g.append(label(w * 0.25, bh + 16, "normal", 12, fill=TXT2))
    g.append(label(w * 0.75, bh + 16, "paranormal", 12, fill=TXT2))
    fam, _, _ = FONTS["serif"]
    g.append(f'<text x="{w / 2:.1f}" y="{bh + 44:.1f}" font-family="{fam}" '
             f'font-size="23" letter-spacing="3" fill="{TXT}" '
             f'text-anchor="middle">DISTRIBUTION</text>')
    return "".join(g), w, bh + 52


# ── Contexts ─────────────────────────────────────────────────────────────────
# A statistics dataset is always about something. The numbers on this cover are
# sleep hours, commute times, rainfall, free throws — and a cover that draws the
# thing beside the numbers says what the unit is about far faster than a caption
# does. Each scene is line art in a 100x100 box, scaled and dropped behind its
# display like a watermark, on graph paper.
#
# These are drawn heavier than the rest of the sheet on purpose: the ink budget
# is suspended for them (Layne, 2026-07-30).

PAPER_BG   = "#f4f7fb"   # graph paper stock
PAPER_RULE = "#cfdcea"   # its printed grid
PAPER_EDGE = "#9fb3c8"   # the sheet's own edge
SCENE_INK  = "#8fa3b8"   # the watermark drawing


def _sp(d, width=2.4, stroke=None, fill="none") -> str:
    return path(d, stroke=stroke or SCENE_INK, width=width, fill=fill,
                cap="round")


def _sr(x, y, w, h, r=0, width=2.4, fill="none") -> str:
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{r}" '
            f'fill="{fill}" stroke="{SCENE_INK}" stroke-width="{width}"/>')


def _sc(cx, cy, r, width=2.4, fill="none") -> str:
    return (f'<circle cx="{cx}" cy="{cy}" r="{r}" fill="{fill}" '
            f'stroke="{SCENE_INK}" stroke-width="{width}"/>')


def _scene_bed():          # sleep, rest
    return [_sp("M8 74V40"), _sp("M8 46H30"), _sr(8, 56, 84, 18, 4),
            _sr(30, 46, 22, 10, 3), _sp("M14 74V84"), _sp("M86 74V84")]


def _scene_stopwatch():    # reaction time, wait time, commute
    return [_sc(50, 58, 30), _sp("M44 22H56"), _sp("M50 22V28"),
            _sp("M50 58V38"), _sp("M50 58L66 66"), _sp("M78 34L86 26")]


def _scene_book():         # study hours, reading
    return [_sp("M50 32C40 24 24 24 12 28V76C24 72 40 72 50 80"),
            _sp("M50 32C60 24 76 24 88 28V76C76 72 60 72 50 80"),
            _sp("M50 32V80", width=1.8)]


def _scene_hoop():         # basketball, free throws
    return [_sp("M78 14V72"), _sr(56, 20, 22, 18, 2),
            _sp("M60 38H74"), _sp("M61 38L64 48"), _sp("M73 38L70 48"),
            _sp("M64 48H70"), _sc(28, 58, 15)]


def _scene_target():       # archery, hitting a target
    return [_sc(44, 54, 28), _sc(44, 54, 17), _sc(44, 54, 7, fill=SCENE_INK),
            _sp("M62 36L90 12"), _sp("M84 12H90V18")]


def _scene_plant():        # plant growth, gardening
    return [_sp("M34 66H66L62 88H38Z"), _sp("M50 66V34"),
            _sp("M50 46C38 46 32 38 32 28C44 28 50 36 50 46"),
            _sp("M50 52C62 52 68 44 68 34C56 34 50 42 50 52")]


def _scene_car():          # commute, distance, mileage
    return [_sp("M12 62H88"), _sp("M20 62L28 42H72L80 62"),
            _sc(32, 66, 8), _sc(68, 66, 8), _sp("M48 42V62")]


def _scene_money():        # rent, price, ATM, salary
    return [_sr(10, 30, 80, 44, 4), _sc(50, 52, 13),
            _sp("M50 42V62"), _sp("M55 46C55 43 45 43 45 48C45 53 55 51 55 56"
                                  "C55 61 45 61 45 58")]


def _scene_battery():      # battery lifetime
    return [_sr(12, 36, 68, 32, 4), _sr(80, 46, 8, 12, 2),
            _sp("M22 44V60", width=5), _sp("M34 44V60", width=5),
            _sp("M46 44V60", width=5)]


def _scene_rain():         # rainfall
    return [_sp("M28 52C18 52 14 44 20 38C20 26 38 22 44 32"
                "C54 24 70 30 68 42C78 42 80 54 68 54H28Z"),
            _sp("M32 62L28 74"), _sp("M48 62L44 74"), _sp("M64 62L60 74")]


def _scene_scale():        # weights — packages, babies, granola bars
    return [_sp("M50 24V64"), _sp("M22 32H78"), _sp("M38 76H62"),
            _sp("M50 64V76"), _sp("M10 32L22 52H38Z"), _sp("M62 32L78 52H90Z"),
            _sc(50, 22, 5)]


def _scene_orange():       # vitamin C, oranges, fruit
    return [_sc(48, 56, 28), _sp("M48 28C52 18 62 14 70 16C68 24 60 30 48 30"),
            _sp("M48 56L30 40"), _sp("M48 56L66 40"), _sp("M48 56V32")]


def _scene_fish():         # salmon length
    return [_sp("M18 56C34 34 66 34 80 56C66 78 34 78 18 56Z"),
            _sp("M80 56L92 44V68Z"), _sc(32, 50, 3, fill=SCENE_INK),
            _sp("M52 40V72", width=1.8)]


def _scene_syringe():      # vaccination, clinical trial, flu shot
    return [_sp("M24 72L44 52"), _sr(44, 30, 34, 22, 3),
            _sp("M52 26V38"), _sp("M62 26V38"), _sp("M78 34L90 22"),
            _sp("M20 76L28 68")]


def _scene_thermometer():  # temperature
    return [_sp("M42 20A8 8 0 0 1 58 20V58"), _sp("M42 20V58"),
            _sc(50, 68, 13), _sp("M50 62V40"), _sp("M62 32H70"),
            _sp("M62 42H70")]


def _scene_phone():        # social media, screen time
    return [_sr(30, 14, 40, 72, 6), _sp("M44 22H56"),
            _sp("M38 38H62"), _sp("M38 48H62"), _sp("M38 58H52"),
            _sc(50, 76, 3)]


def _scene_ballot():       # voter turnout, elections
    return [_sr(16, 44, 68, 40, 3), _sp("M38 44H62"),
            _sp("M40 44V22H72V40"), _sp("M48 30H64"), _sp("M48 36H60")]


def _scene_quiz():         # test scores, quizzes, guessing
    return [_sr(22, 14, 56, 72, 3), _sp("M32 32H56"), _sp("M32 46H60"),
            _sp("M32 60H50"), _sp("M60 56L66 64L80 46")]


def _scene_dice():         # probability, random chance
    return [_sr(16, 34, 44, 44, 6), _sc(28, 46, 3.4, fill=SCENE_INK),
            _sc(48, 66, 3.4, fill=SCENE_INK), _sc(38, 56, 3.4, fill=SCENE_INK),
            _sr(60, 20, 30, 30, 5), _sc(70, 30, 2.8, fill=SCENE_INK),
            _sc(80, 40, 2.8, fill=SCENE_INK)]


def _scene_coffee():       # caffeine, drinks
    return [_sp("M20 36H72V60A18 18 0 0 1 36 60V36Z"),
            _sp("M72 42H84A9 9 0 0 1 84 58H72"), _sp("M18 84H74"),
            _sp("M34 26C34 20 40 20 40 14"), _sp("M50 26C50 20 56 20 56 14")]


def _scene_factory():      # defective products, quality control
    return [_sp("M14 78V44L34 56V44L54 56V44L74 56V78Z"),
            _sp("M74 56V26H86V78"), _sp("M28 66H36"), _sp("M48 66H56"),
            _sp("M64 66H70")]


# Keyword → scene. First match in the unit's prose wins, so the order here is
# the order a tie is broken in: the more specific phrase must come first.
_CONTEXT_SCENES: list[tuple[str, str, str]] = [
    (r"reaction time|\bRT\b\s*\(ms\)", "stopwatch", "reaction time"),
    (r"\bcommut(?:e|es|ing)\b|\btraffic\b|\bmileage\b|\bdriv(?:e|es|ing|er)\b",
     "car", "commuting"),
    (r"wait(?:ing)? time|\bqueue\b|checkout", "stopwatch", "wait times"),
    (r"\bsleep", "bed", "sleep"),
    (r"stud(?:y|ying) (?:time|hours|hr)|homework hours|reading fluency",
     "book", "study time"),
    (r"free throw|basketball", "hoop", "free throws"),
    # \b on both sides, or this fires on every "researcher" in the course —
    # 211 of them, against 3 real bullseyes.
    (r"\barcher(?:s|y)?\b|bullseye|target practice", "target", "archery"),
    (r"plant growth|seedling|fertilizer|\bgarden", "plant", "plant growth"),
    (r"\brent\b|\bprices?\b|salary|withdrawal|\bATM\b|income|\bcosts?\b",
     "money", "prices"),
    (r"batter(?:y|ies) (?:life|lifetime)|charge lasts", "battery",
     "battery life"),
    (r"rainfall|precipitation|\brain\b", "rain", "rainfall"),
    (r"\bweights?\b|\bmass\b|granola|package weight|baby weight", "scale",
     "weights"),
    (r"vitamin c|\borange|fruit juice", "orange", "vitamin C"),
    (r"\bsalmon\b|\bfish\b|\btrout\b", "fish", "salmon length"),
    (r"\bvaccin|flu shot|clinical trial|placebo|treatment group", "syringe",
     "clinical trials"),
    # NOT "degrees": this course says "degrees of freedom" constantly, and it
    # has nothing to do with temperature.
    (r"temperature|\btemps?\b|thermometer|degrees F|°F", "thermometer",
     "temperature"),
    (r"social media|screen time|smartphone|\bapps?\b", "phone", "social media"),
    (r"voter turnout|\bvot(?:e|es|ing|ers?)\b|\belections?\b|"
     r"\bpoll(?:s|ed|ing|ster)?\b", "ballot", "voter turnout"),
    (r"\bquiz|test score|exam score|multiple choice|guess(?:es|ing)?\b",
     "quiz", "test scores"),
    (r"\bdice\b|\bdie\b|coin flip|rolling a|\bspinner\b", "dice", "chance"),
    (r"caffeine|coffee|\bsodas?\b|beverage", "coffee", "caffeine"),
    (r"\bdefect|quality control|assembly line|manufactur", "factory",
     "quality control"),
]

_SCENES = {
    "bed": _scene_bed, "stopwatch": _scene_stopwatch, "book": _scene_book,
    "hoop": _scene_hoop, "target": _scene_target, "plant": _scene_plant,
    "car": _scene_car, "money": _scene_money, "battery": _scene_battery,
    "rain": _scene_rain, "scale": _scene_scale, "orange": _scene_orange,
    "fish": _scene_fish, "syringe": _scene_syringe,
    "thermometer": _scene_thermometer, "phone": _scene_phone,
    "ballot": _scene_ballot, "quiz": _scene_quiz, "dice": _scene_dice,
    "coffee": _scene_coffee, "factory": _scene_factory,
}


def build_scene(el: dict) -> tuple[str, float, float]:
    """A sheet of graph paper carrying the situation a dataset came from, with
    the display for that dataset drawn on top of it.

    `inner` is a complete element dict — any of the display builders — so a
    scene is a wrapper, not a new kind of plot. Without one the scene is just
    the situation, which is what a unit that names a context but tabulates no
    numbers for it gets.
    """
    pad = el.get("pad", 15)
    inner = el.get("inner")
    if inner:
        body, iw, ih = BUILDERS[inner["type"]](inner)
    else:
        body, iw, ih = "", el.get("w", 210), el.get("h", 150)
    w, h = iw + 2 * pad, ih + 2 * pad
    # A dotplot is a wide, short strip. Wrapped tightly it gives a letterbox of
    # a sheet, and the watermark — sized to the short side — shrinks to nothing.
    # Open the sheet out vertically instead, and centre the plot in it.
    top = pad
    if h < w * 0.5:
        grow = w * 0.5 - h
        top += grow / 2
        h += grow

    g = [f'<rect x="0" y="0" width="{w:.1f}" height="{h:.1f}" fill="{PAPER_BG}" '
         f'stroke="{PAPER_EDGE}" stroke-width="1.3"/>']
    step = el.get("grid", 12)
    d = []
    x = step
    while x < w:
        d.append(f"M{x:.1f} 0V{h:.1f}")
        x += step
    y = step
    while y < h:
        d.append(f"M0 {y:.1f}H{w:.1f}")
        y += step
    g.append(path("".join(d), stroke=PAPER_RULE, width=0.6))

    art = _SCENES.get(el.get("scene", ""))
    if art:
        # Centre the drawing on the sheet and size it to the smaller dimension,
        # so it reads as a watermark behind the plot rather than beside it.
        s = min(w, h) * el.get("art_scale", 0.82) / 100.0
        g.append(f'<g transform="translate({(w - 100 * s) / 2:.1f},'
                 f'{(h - 100 * s) / 2:.1f}) scale({s:.3f})">'
                 + "".join(art()) + "</g>")
    if body:
        g.append(f'<g transform="translate({pad},{top:.1f})">{body}</g>')
    return _caption(g, w, h, el)


BUILDERS = {
    "scene": build_scene,
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
    "tally": build_tally,
    "split": build_split,
    "meme": build_meme,
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
                              "histogram", "scatter", "normal", "scene",
                              "tally", "split"):
                el["skew"] = SKEWS[i % len(SKEWS)]
            else:
                el["tilt"] = TILTS[i % len(TILTS)]
        if el.get("at"):
            out.append(el)
            taken.append((*el["at"], *BUILDERS[el["type"]](el)[1:]))
            continue
        _, w, h = BUILDERS[el["type"]](el)
        # A tilt or skew rotates the box about its centre, so the footprint on
        # the page is larger than the box the builder reported. Reserve the
        # difference or neighbours collide at the corners.
        gw, gh = w * 1.08 + 6, h * 1.08 + 6
        best = None
        for _ in range(800):
            x = rng.uniform(40, max(41, W - 40 - gw))
            y = rng.uniform(46, max(47, H - 46 - gh))
            r = (x, y, gw, gh)
            if any(_overlaps(r, s) for s in taken):
                continue
            best = r
            break
        # Nowhere to put it: drop it. A cover that leaves one scene out reads
        # fine; one that stacks two panels on top of each other does not, and
        # the old fallback placed them at random precisely when the page was
        # already full.
        if best is None:
            continue
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


# The label cell that a data row leads with, once the column spec, the rules
# and the row colouring are out of the way. "\textbf{Sleep (hr)}" -> "Sleep (hr)".
_ROW_LABEL = re.compile(r"\\(?:textbf|textit|emph)\{([^{}]+)\}")
_SPEC_JUNK = re.compile(
    r"\\begin\{tabular[xy]?\}|\\(?:hline|toprule|midrule|bottomrule|rowcolor|"
    r"linewidth|arraystretch|multicolumn|small|footnotesize)\b|\{[^{}]*\}|[{}@*]")


def _row_label(head: str) -> str:
    """The variable this row is measuring, or "" when the row is unlabelled."""
    m = _ROW_LABEL.search(head)
    text = m.group(1) if m else _SPEC_JUNK.sub(" ", head)
    text = re.sub(r"\s+", " ", text).strip(" &:")
    # A label is a name, not a formula and not a leftover fragment of markup.
    if not re.fullmatch(r"[A-Za-z][A-Za-z /.'-]*(?:\([^()]{1,8}\))?", text or ""):
        return ""
    return text if 2 <= len(text) <= 26 else ""


def _datasets(src: str) -> tuple[list[dict], list[dict]]:
    """Univariate datasets and bivariate pairs, in document order.

    A tabular that yields exactly two equal-length numeric rows is bivariate —
    that is how this course lays out paired data, one variable per row — and
    becomes a scatterplot. Everything else is univariate.

    Each record carries the row's own label and the prose that introduced it,
    so a display can be captioned with the variable it measures and matched to
    the situation the problem is set in.
    """
    uni: list[dict] = []
    pairs: list[dict] = []
    seen: set[tuple] = set()

    # tabularx is the workhorse here; plain tabular is the exception.
    for m in re.finditer(r"\\begin\{tabular[xy]?\}(.+?)\\end\{tabular[xy]?\}",
                         src, re.S):
        block = m.group(1)
        # A contingency table's rows are category counts and a probability
        # distribution's are masses; neither is a sample to plot. Both announce
        # themselves — a Total margin, or a P(X = x) row.
        if re.search(r"\bTotals?\b|P\(X\s*=|\bProbability\b|\bExpected\b",
                     block):
            continue
        near = src[max(0, m.start() - 600):m.start()]
        rows = []
        for row in block.split(r"\\"):
            row = re.sub(r"\\(?:hline|toprule|midrule|bottomrule)", " ", row)
            if "&" not in row:
                continue
            cells = row.split("&")
            v = _cells_to_numbers(cells)
            if _usable(v):
                head = " ".join(cells[:len(cells) - len(v)])
                rows.append((v, _row_label(head)))
        if len(rows) == 2 and len(rows[0][0]) == len(rows[1][0]) and \
                tuple(rows[0][0]) not in seen and tuple(rows[1][0]) not in seen:
            seen.add(tuple(rows[0][0]))
            seen.add(tuple(rows[1][0]))
            pairs.append({"x": rows[0][0], "y": rows[1][0],
                          "xlabel": rows[0][1], "ylabel": rows[1][1],
                          "near": near})
        else:
            for v, lab in rows:
                if tuple(v) in seen:
                    continue
                seen.add(tuple(v))
                uni.append({"v": v, "label": lab, "near": near})

    # Loose comma-separated lists, the other way this course states a dataset.
    for m in re.finditer(r"(?:\d+(?:\.\d+)?\s*,\s*){4,}\d+(?:\.\d+)?", src):
        v = [float(t) for t in _NUMBER_RE.findall(m.group(0))]
        if tuple(v) in seen or not _usable(v):
            continue
        seen.add(tuple(v))
        uni.append({"v": v, "label": "",
                    "near": src[max(0, m.start() - 600):m.start()]})
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


@lru_cache(maxsize=None)
def _scene_patterns() -> tuple:
    return tuple((re.compile(pat, re.I), scene, name)
                 for pat, scene, name in _CONTEXT_SCENES)


def _context_of(text: str) -> tuple[str | None, str]:
    """The situation a passage is set in — the scene to draw and what to call
    it. Whichever context is named *latest* in the passage wins, because the
    passage runs up to the table and the sentence nearest it is the one that
    introduces the data."""
    best = (-1, None, "")
    for rx, scene, name in _scene_patterns():
        pos = max((m.start() for m in rx.finditer(text)), default=-1)
        if pos > best[0]:
            best = (pos, scene, name)
    return best[1], best[2]


def _contexts_in(src: str) -> list[tuple[str, str]]:
    """Every situation the unit names, in the order it first names them."""
    hits = []
    for rx, scene, name in _scene_patterns():
        m = rx.search(src)
        if m:
            hits.append((m.start(), scene, name))
    hits.sort()
    return [(scene, name) for _, scene, name in hits]


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
    used_scenes: set[str] = set()

    def dress(el: dict, rec: dict, caption: str) -> dict:
        """Caption a display with the variable it measures, and stand it on a
        sheet of graph paper drawn with the situation it came from."""
        if caption:
            el["caption"] = caption
        scene, name = _context_of(rec["near"])
        if scene is None or scene in used_scenes:
            return el
        used_scenes.add(scene)
        return {"type": "scene", "inner": el, "scene": scene,
                "caption": el.pop("caption", None) or name}

    # Take the two scatters from opposite ends of the unit. Adjacent pairs are
    # usually the notes' worked example and the homework's echo of it —
    # different numbers, but they draw as the same picture.
    picks = [pairs[0], pairs[len(pairs) // 2]] if len(pairs) >= 2 else pairs[:1]
    for rec in picks:
        cap = " vs. ".join(t for t in (rec["xlabel"], rec["ylabel"]) if t)
        elements.append(dress({"type": "scatter", "x": rec["x"], "y": rec["y"],
                               "w": 244, "h": 174}, rec, cap))
    # Deal the datasets out across the display types, one type at a time, so a
    # unit whose tables are all the same size still gets a varied page instead
    # of five identical strips.
    spare = list(uni)
    while len(elements) < 5 and spare:
        progress = False
        for kind in ("dotplot", "boxplot", "histogram"):
            rec = next((r for r in spare if kind in _admits(r["v"])), None)
            if rec is None or len(elements) >= 5:
                continue
            spare.remove(rec)
            elements.append(dress(_build_display(kind, rec["v"]), rec,
                                  rec["label"]))
            progress = True
        if not progress:
            break

    # ── Situations the unit names but tabulates no numbers for ──────────────
    # Drawn on their own sheet of graph paper. A unit talks about far more
    # contexts than it hands you data for, and they are the part of the course
    # a student actually recognises.
    # A unit that tabulates nothing — Unit 3 is entirely study design — leans on
    # its situations for the whole page, so it gets more of them.
    loose_cap = 6 if len(elements) <= 1 else 3
    loose = 0
    for scene, name in _contexts_in(src):
        if loose >= loose_cap or scene in used_scenes:
            continue
        used_scenes.add(scene)
        loose += 1
        elements.append({"type": "scene", "scene": scene, "caption": name,
                         "w": 150, "h": 118})

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
