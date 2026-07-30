# Unit Packet Refactor Notes — SUPERSEDED

**Status: retired 2026-07-30 by Part 2 of `ALGEBRA2_PARITY_NOTES.md`.**

This file recorded the `unitXX_student.tex` / `unitXX_full.tex` wrapper approach: a per-unit
`.tex` that source-included every component with `docmute` + `import`, so the merged unit packet
carried one continuous page-number sequence. It is kept for the history, not as instructions —
**do not implement anything below.**

## What replaced it

Pagination is now an overlay pass owned by one layer, applied at the lesson level and re-applied
at the unit level:

- `shared/paginate.tex` — places each merged page at full size on a same-size sheet, covers the
  component-local page number with a white band inside the bottom margin, and prints the
  packet-wide number in its place. Also forces recto starts and numbers inserted blank versos.
- `shared/paginate.sh` — computes the page slots and drives that pass. A component's slot is
  `ceil_even(max(blank pages, key pages))`, so the student and key packets come out page for
  page.

The pass is idempotent — the band covers whatever number is already there — which is what lets
`shared/unit.mk` re-run it over a unit packet merged from already-paginated lesson packets.

## Why the wrappers went

- They achieved continuous numbering for the **one** unit that had them (unit01). Units 02–09
  silently fell back to `pdfunite`, so the course numbered its packets two different ways.
- Each wrapper hard-coded every lesson's slide page count by hand.
- Source-inclusion is fragile: lesson plans needed per-file adjustments (metadata after
  `\begin{document}`, no preamble-only code) before they would source-include at all.
- They could not align the student and key packets against each other, which is now the defining
  property of the key product.

The overlay needs no per-unit or per-lesson file, works identically for prefab PDFs, and gets
slide page counts from `pdfinfo`.

## What carried over unchanged

- `unitXX/lessonYY/slides/main.pdf` stays **one slide per page** and remains the source of truth
  for the deck. It is no longer a work product itself; two products derive from it.
- The 3-up printed slide handout survives as `shared/handout.tex`, now the `lessonYY_slides.pdf`
  product instead of being inlined in the teacher packet. Its page count comes from `pdfinfo`,
  not from a hand-written number.
- Still true: no slides in the student packet, and no lesson plan inserted into a packet.

## Rescinded: the PowerPoint prohibition

This file used to say "**Do not add a Node or PowerPoint generation step for this workflow.**"
**Layne explicitly rescinded the PowerPoint half on 2026-07-30.** Current project policy:

> **Every lesson ships its deck in both forms — `lessonYY_slides.pptx` (projected) and
> `lessonYY_slides.pdf` (3 slides per page with a note column, printed).**

`lessonYY_slides.pptx` is built by `shared/pdf2pptx.py`, which uses only the Python standard
library and the poppler tools the build already requires — no LibreOffice, no `python-pptx`, no
install step. Google Slides imports `.pptx` natively, so it also covers the import path the raw
one-slide-per-page PDF used to serve.

**The ban on a Node step still stands.**

Every lesson therefore owes a deck. 57 of 80 do not have one yet; those get authored during the
lesson review pass, not in a bulk sweep.

## Deleted by the refactor

```
unit01/unit01_student.tex
unit01/unit01_full.tex
unit01/lesson01/lesson01_student.tex   # bare \input lists, no preamble, unreferenced
unit01/lesson01/lesson01_full.tex
```

Current build documentation lives in `.claude/skills/lesson-planning/references/build.md`.
