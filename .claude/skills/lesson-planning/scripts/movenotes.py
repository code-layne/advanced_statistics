#!/usr/bin/env python3
"""Move teacher notes out of a lesson's _key files and into its lesson plan.

A teachernote is the one block in a key with no counterpart in the blank, so it
makes the key longer than the blank for no student-facing reason. The lesson
plan is teacher-facing already and sits outside the page-matched packet.

Each note is re-titled for the component it came from:
    \\begin{teachernote}[Warm-Up] ... \\end{teachernote}

Idempotent-ish: it errors rather than acting if the plan already has a migrated
"Teacher Notes" block, and skips keys with no note.

    python3 movenotes.py unit01/lesson02          # migrate
    python3 movenotes.py unit01/lesson02 --check   # report only
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

# component dir → the label used in the note title
COMPONENTS = [
    ("warmup_key",      "Warm-Up"),
    ("notes_key",       "Guided Notes"),
    ("activity_key",    "Group Activity"),
    ("exit_ticket_key", "Exit Ticket"),
    ("homework_key",    "Homework"),
]

NOTE_RE = re.compile(
    r"\n*\\begin\{teachernote\}(?:\[[^\]]*\])?\s*\n(?P<body>.*?)\n\\end\{teachernote\}\n",
    re.S)

MARKER = "% ── Teacher notes (migrated from the component keys) ──"

BANNER = (MARKER + "\n"
          "% One per component, titled for it. They live here rather than in the _key\n"
          "% files so that every component is the same length blank and keyed.\n")


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("lesson_dir")
    ap.add_argument("--check", action="store_true", help="report only")
    args = ap.parse_args()

    lesson = Path(args.lesson_dir)
    plan = lesson / "main.tex"
    if not plan.is_file():
        sys.exit(f"error: {plan} not found")

    plan_src = plan.read_text(encoding="utf-8")
    if MARKER in plan_src:
        sys.exit(f"error: {plan} already carries migrated teacher notes -- nothing done")

    moved: list[tuple[str, str, str]] = []   # (dir, label, body)
    for comp, label in COMPONENTS:
        f = lesson / comp / "main.tex"
        if not f.is_file():
            continue
        src = f.read_text(encoding="utf-8")
        m = NOTE_RE.search(src)
        if not m:
            print(f"  {comp}: no teacher note")
            continue
        moved.append((comp, label, m.group("body").rstrip()))
        if not args.check:
            f.write_text(NOTE_RE.sub("\n", src, count=1), encoding="utf-8")
        print(f"  {comp}: moved {len(m.group('body').splitlines())} lines → \"Teacher Note: {label}\"")

    if not moved:
        print("nothing to move")
        return
    if args.check:
        print(f"\n{lesson}: {len(moved)} note(s) would move into {plan}")
        sys.exit(1)

    block = [BANNER]
    for _comp, label, body in moved:
        block.append(f"\n\\begin{{teachernote}}[{label}]\n{body}\n\\end{{teachernote}}\n")
    plan.write_text(
        plan_src.replace("\\end{document}", "".join(block) + "\n\\end{document}"),
        encoding="utf-8")
    print(f"\n{lesson}: {len(moved)} note(s) → {plan}")
    print(f"next: make -C {lesson} all   # then confirm each component matches its key")


if __name__ == "__main__":
    main()
