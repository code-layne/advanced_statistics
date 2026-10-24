#!/usr/bin/env python3
"""Fail if a graded document carries a name line.

A document is graded when it loads grading.sty (math-shared). Its pages are
scanned and the scans go to an outside API, so they carry only the tracking id
in the strip; the student's name goes on the separate cover sheet that
`make roster-packets` prints. A name line on a graded page invites a student to
write her name where the scan will pick it up.

    python3 shared/check_namelines.py unit02/tests/actual_test unit02/test_keys/actual_test_key
    python3 shared/check_namelines.py unit01 unit02 ...      # every main.tex below

Each argument is a main.tex, or a directory searched for main.tex files; a path
that does not exist is skipped (a component with no key). For every graded
document, comments stripped, it reports each use of \\namedateperiod or
\\namepartnerperiod and each hand-written "Name:", "Date:" or "Period:" field.
Documents that do not load grading are not checked: they keep their name line.
Exits 1 on any hit.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

LOADS_GRADING = re.compile(r"\\usepackage\s*(\[[^\]]*\])?\s*\{[^}]*\bgrading\b[^}]*\}")
NAME_LINE = re.compile(r"\\name(dateperiod|partnerperiod)\b|\b(Name|Date|Period)\s*(\\[;:,]|\\ )?\s*:")
COMMENT = re.compile(r"(?<!\\)%.*")


def documents(args: list[str]) -> list[Path]:
    found: list[Path] = []
    for a in args:
        p = Path(a)
        if p.is_dir():
            found += sorted(q for q in p.rglob("main.tex") if "target" not in q.parts)
        elif p.is_file():
            found.append(p)
    return found


def main(argv: list[str]) -> int:
    hits = 0
    for doc in documents(argv):
        lines = [COMMENT.sub("", l) for l in doc.read_text(encoding="utf-8").splitlines()]
        if not LOADS_GRADING.search("\n".join(lines)):
            continue
        for n, line in enumerate(lines, 1):
            if NAME_LINE.search(line):
                print(f"{doc}:{n}: name line in a graded document: {line.strip()}", file=sys.stderr)
                hits += 1
    if hits:
        print(f"!  {hits} name line(s) on graded pages — remove them; the name goes on the "
              "roster cover sheet only", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
