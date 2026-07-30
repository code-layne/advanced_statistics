#!/usr/bin/env python3
"""Namestrip a lesson: keep the name/date/period row on the cover only.

The student packet is stapled behind its cover sheet, so a name/date/period row
on every component is redundant -- it costs vertical space at the top of each
page for something the student already wrote on page 1. This script removes
\\namedateperiod and \\namepartnerperiod from every component of a lesson except
the cover, keeping each blank and its _key in lockstep.

It matters more once unit packets are built from a unitXX_student.tex wrapper:
the whole unit is then one continuously-paginated document, so the cover row is
even further from "once per handout."

Deliberately NOT touched:
  * cover/              -- this is the one place the row belongs.
  * unitXX/sample_test/ -- a prefab PDF; nothing to strip.

See references/conventions.md ("Namestrip") for the convention this enforces.

Examples:
    # report what would change, touch nothing
    python3 namestrip.py --project . --unit 02 --lesson 03 --check

    # apply it
    python3 namestrip.py --project . --unit 02 --lesson 03

    # or point straight at a lesson directory
    python3 namestrip.py unit02/lesson03
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Matches a line consisting solely of the macro (optionally with trailing % comment).
NAME_ROW_RE = re.compile(r"^[ \t]*\\name(?:dateperiod|partnerperiod)\b[ \t]*(?:%.*)?$")

SKIP_DIRS = {"cover"}


def fail(msg: str) -> "NoReturn":  # type: ignore[name-defined]
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(1)


def strip_file(path: Path, check: bool) -> list[tuple[int, str]]:
    """Remove name-row lines from one file. Returns [(lineno, text), ...] removed."""
    lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
    removed = [(i + 1, ln.strip()) for i, ln in enumerate(lines) if NAME_ROW_RE.match(ln.rstrip("\n"))]
    if removed and not check:
        kept = [ln for ln in lines if not NAME_ROW_RE.match(ln.rstrip("\n"))]
        path.write_text("".join(kept), encoding="utf-8")
    return removed


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Strip name/date/period rows from every lesson component except the cover.")
    ap.add_argument("lesson_dir", nargs="?", help="path to unitXX/lessonYY (alternative to --unit/--lesson)")
    ap.add_argument("--project", default=".", help="project root (default: .)")
    ap.add_argument("--unit", help="unit number, e.g. 02")
    ap.add_argument("--lesson", help="lesson number, e.g. 03")
    ap.add_argument("--check", action="store_true",
                    help="report what would be removed; change nothing (exit 1 if any found)")
    args = ap.parse_args()

    if args.lesson_dir:
        lesson = Path(args.lesson_dir)
    elif args.unit and args.lesson:
        lesson = Path(args.project) / f"unit{args.unit}" / f"lesson{args.lesson}"
    else:
        fail("give a lesson directory, or both --unit and --lesson")

    if not lesson.is_dir():
        fail(f"{lesson} is not a directory")

    total = 0
    touched = 0
    for tex in sorted(lesson.glob("*/main.tex")):
        if tex.parent.name in SKIP_DIRS:
            continue
        removed = strip_file(tex, args.check)
        if removed:
            touched += 1
            total += len(removed)
            verb = "would remove" if args.check else "removed"
            for lineno, text in removed:
                print(f"  {verb} {tex.parent.name}/main.tex:{lineno}  {text}")

    if total == 0:
        print(f"{lesson}: already namestripped (nothing to remove)")
        return

    print(f"\n{lesson}: {total} line(s) across {touched} component(s)")
    if args.check:
        sys.exit(1)
    print(f"next: make -C {lesson} all   # then re-check warm-up and exit ticket are still 1 page")


if __name__ == "__main__":
    main()
