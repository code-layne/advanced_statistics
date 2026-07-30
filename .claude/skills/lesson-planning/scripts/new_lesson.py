#!/usr/bin/env python3
"""Scaffold a new lesson directory for a LaTeX curriculum project.

Creates unitXX/lessonYY/ with a Makefile, the lesson-plan main.tex, and the
requested component subdirectories (each with a correctly-preambled main.tex,
and a matching _key for keyed components). Auto-detects the style-package
prefix and whether course-level macros are already defined in shared/.

Example:
    python new_lesson.py --project ../statistics --unit 03 --lesson 01 \
        --title "Sampling Methods" --components cover,warmup,notes,activity,exit_ticket,homework \
        --prefab warmup,warmup_key
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

SKEL_DIR = Path(__file__).resolve().parent.parent / "assets" / "skeletons"

KEYED = ["warmup", "notes", "activity", "exit_ticket", "homework"]
NO_KEY = ["cover", "slides"]
ALL_COMPONENTS = KEYED + NO_KEY
# `slides` is in the defaults because the deck now feeds a work product of its
# own (lessonYY_slides.pdf) — every lesson owes one. Drop it explicitly via
# --components if a particular lesson genuinely has no deck.
DEFAULT_COMPONENTS = ["cover", "warmup", "notes", "activity", "exit_ticket",
                      "homework", "slides"]

DOC_TITLE = {
    "warmup": "Warm-Up",
    "notes": "Guided Notes",
    "activity": "Group Activity",
    "exit_ticket": "Exit Ticket",
    "homework": "Homework",
}
# Namestrip: the name/date/period row belongs on the cover and nowhere else. The
# packet is stapled behind its cover, and unit packets are one continuously
# paginated document, so a row on every component costs a line at the top of
# each page for something the student wrote once on page 1. cover.tex carries
# the only \namedateperiod; every other component skeleton gets none.
NAME_ROW: dict[str, str] = {}


def fail(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def detect_prefix(shared: Path) -> str:
    matches = sorted(shared.glob("*-colors.sty"))
    if not matches:
        fail(f"no <prefix>-colors.sty in {shared} — is this a curriculum project root?")
    return matches[0].name[: -len("-colors.sty")]


def shared_defines_coursename(shared: Path) -> bool:
    pat = re.compile(r"\\(?:new|provide)command\{\\CourseName\}")
    return any(pat.search(sty.read_text(encoding="utf-8", errors="ignore")) for sty in shared.glob("*.sty"))


def detect_course_name(shared: Path) -> str | None:
    pat = re.compile(r"\\(?:new|provide)command\{\\CourseName\}\{([^}]*)\}")
    for sty in shared.glob("*.sty"):
        m = pat.search(sty.read_text(encoding="utf-8", errors="ignore"))
        if m:
            return m.group(1).strip()
    return None


def render(name: str, subs: dict[str, str]) -> str:
    text = (SKEL_DIR / name).read_text(encoding="utf-8")
    for token, value in subs.items():
        text = text.replace(f"@@{token}@@", value)
    return text


def write(path: Path, content: str, force: bool) -> None:
    if path.exists() and not force:
        fail(f"{path} already exists (use --force to overwrite)")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    print(f"  + {path}")


def prefab_dir(path: Path) -> None:
    """Create an empty component directory for a dropped-in prefab PDF.

    No main.tex is written; the user drops the PDF as <dir>/main.pdf and the
    refactored lesson.mk merges it directly. A .gitkeep keeps the empty dir tracked.
    """
    path.mkdir(parents=True, exist_ok=True)
    gitkeep = path / ".gitkeep"
    if not gitkeep.exists():
        gitkeep.write_text("", encoding="utf-8")
    print(f"  + {path}/  (drop the prefab PDF here as main.pdf)")


def main() -> None:
    p = argparse.ArgumentParser(description="Scaffold a new lesson directory.")
    p.add_argument("--project", default=".", help="path to the curriculum project root "
                                                  "(contains shared/); defaults to the current directory")
    p.add_argument("--unit", required=True, help="unit number, e.g. 03")
    p.add_argument("--lesson", required=True, help="lesson number, e.g. 01")
    p.add_argument("--lesson-id", help="human lesson id for headers, e.g. 3.1 (default: <unit>.<lesson>)")
    p.add_argument("--title", default="TODO: Lesson Title", help="lesson/topic title")
    p.add_argument("--unit-title", default="TODO: Unit Title", help="unit title for the lesson plan")
    p.add_argument("--components", default=",".join(DEFAULT_COMPONENTS),
                   help=f"comma list from {ALL_COMPONENTS}")
    p.add_argument("--prefab", default="", help="comma list of dirs that will hold a dropped-in "
                                                "prefab PDF (placed as <dir>/main.pdf), e.g. warmup,warmup_key")
    p.add_argument("--course", help="course name for cover/slides (default: detected or 'TODO Course')")
    p.add_argument("--year", default="2026--2027", help="school year (used only if not defined in shared/)")
    p.add_argument("--meeting-length", default="55 minutes", help="meeting length (used only if not in shared/)")
    p.add_argument("--no-plan", action="store_true", help="do not scaffold the lesson-plan main.tex")
    p.add_argument("--force", action="store_true", help="overwrite existing files")
    args = p.parse_args()

    project = Path(args.project).expanduser().resolve()
    shared = project / "shared"
    if not shared.is_dir():
        fail(f"{shared} not found")

    prefix = detect_prefix(shared)
    unit_dir = f"unit{int(args.unit):02d}"
    lesson_dir = f"lesson{int(args.lesson):02d}"
    unit_int = str(int(args.unit))
    lesson_id = args.lesson_id or f"{int(args.unit)}.{int(args.lesson)}"

    components = [c.strip() for c in args.components.split(",") if c.strip()]
    bad = [c for c in components if c not in ALL_COMPONENTS]
    if bad:
        fail(f"unknown component(s): {bad}. Allowed: {ALL_COMPONENTS}")
    prefab = {c.strip() for c in args.prefab.split(",") if c.strip()}

    course_name = args.course or detect_course_name(shared) or "TODO Course"
    if shared_defines_coursename(shared):
        course_macros = ""
    else:
        course_macros = (
            f"\\newcommand{{\\CourseName}}{{{course_name}}}\n"
            f"\\newcommand{{\\SchoolYear}}{{{args.year}}}\n"
            f"\\newcommand{{\\MeetingLength}}{{{args.meeting_length}}}\n"
        )

    base = {
        "PREFIX": prefix, "UNITINT": unit_int, "LESSONID": lesson_id,
        "TITLE": args.title, "COURSENAME": course_name,
    }

    dest = project / unit_dir / lesson_dir
    print(f"prefix={prefix}  ->  {dest.relative_to(project)}  (course: {course_name}, "
          f"macros {'in shared' if not course_macros else 'inlined in plan'})")

    write(dest / "Makefile", "include ../../shared/lesson.mk\n", args.force)
    (dest / "images").mkdir(parents=True, exist_ok=True)

    if not args.no_plan:
        if "warmup" in components and "warmup" in prefab:
            # Prefab warm-up lives at warmup/main.pdf in the source tree, so the thumbnail
            # resolves directly with no dependency on build order.
            spiral = r"            \includegraphics[width=\linewidth,page=1]{warmup/main}"
        else:
            # Authored (or no) warm-up: it compiles to target/, so there is no source PDF to
            # embed — keep the spiral review text-only (AP Stats style).
            spiral = ("            % TODO: spiral-review thumbnail. Authored warm-ups compile to\n"
                      "            % target/, so leave this text-only (as in AP Stats) unless you\n"
                      "            % keep a source PDF in the warmup/ directory to embed.")
        write(dest / "main.tex",
              render("lesson_plan.tex", {**base, "UNITTITLE": args.unit_title,
                                         "COURSEMACROS": course_macros, "SPIRALWARMUP": spiral}),
              args.force)

    for comp in components:
        name_row = NAME_ROW.get(comp, "")  # Namestrip: cover only
        if comp in prefab:
            prefab_dir(dest / comp)
        elif comp == "cover":
            write(dest / "cover" / "main.tex", render("cover.tex", base), args.force)
        elif comp == "slides":
            write(dest / "slides" / "main.tex", render("slides.tex", base), args.force)
        else:  # authored worksheet component
            subs = {**base, "DOCTITLE": DOC_TITLE[comp], "NAMEROW": name_row}
            write(dest / comp / "main.tex", render("worksheet.tex", subs), args.force)
        # answer key for keyed components
        if comp in KEYED:
            key = f"{comp}_key"
            if key in prefab:
                prefab_dir(dest / key)
            else:
                subs = {**base, "DOCTITLE": DOC_TITLE[comp], "NAMEROW": name_row}
                write(dest / key / "main.tex", render("worksheet_key.tex", subs), args.force)

    print("\nnext:")
    print(f"  1. Author the skeletons (see references/components.md).")
    if prefab:
        print(f"  2. Drop supplied PDFs as main.pdf in: {', '.join(sorted(prefab))}")
    print(f"  3. Build:  make -C {unit_dir}/{lesson_dir} all")


if __name__ == "__main__":
    main()
