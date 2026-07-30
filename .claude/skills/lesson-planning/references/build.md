# Build System

The project compiles with **XeLaTeX** (via `latexmk`) and merges PDFs with **`pdfunite`**
(poppler). The skill authors `.tex`; the project's own Makefiles do the building. **Never edit
`shared/` or the Makefiles to make a lesson build — fix the lesson's `.tex` instead.**

## The five work products

A lesson builds **five** products into `target/compiled/unitXX/`:

| Product | What it is |
| --- | --- |
| `lessonYY_plan.pdf` | the lesson plan — the lesson-root `main.tex`, compiled |
| `lessonYY_slides.pdf` | the deck **printed**: 3 slides per page, ruled note column beside each |
| `lessonYY_slides.pptx` | the deck **projected**: one full-bleed page image per slide |
| `lessonYY_student.pdf` | cover + blank components, paginated packet-wide |
| `lessonYY_key.pdf` | the same packet answered, **page for page** with the student one |

The two slide products are the deck's two forms — print the PDF, project the PPTX (Google Slides
imports `.pptx` natively). Both derive from the one Beamer deck at
`target/unitXX/lessonYY/slides/main.pdf`, which is the source of truth. **Never edit a product**;
edit `slides/main.tex` and rebuild. `make slides` builds both.

There is no `full` packet. The plan and the deck are standalone deliverables rather than being
buried in a combined teacher packet; `make full` now fails loudly at every level and tells you
what replaced it.

## The three-level Make hierarchy

- **Root `Makefile`** — discovers `unit*/Makefile`, delegates, and merges unit PDFs into
  `target/compiled/curriculum_{student,key}.pdf`. Only these two aggregate to the root; the
  per-lesson plan and deck stay in `target/compiled/unitXX/`.
- **`shared/unit.mk`** (included by each `unitXX/Makefile`) — discovers `lesson*/Makefile`,
  delegates, and produces `target/compiled/unitXX_{student,key}.pdf` by merging the lesson
  packets and re-running the pagination pass unit-wide. It also picks up the optional unit
  bookends `unit_cover/main.tex`, `sample_test/main.pdf`, and `sample_test_key/main.pdf` (the
  sample-test key goes into the **key** packet only).
- **`shared/lesson.mk`** (included by each `lessonYY/Makefile`, which is just
  `include ../../shared/lesson.mk`) — the engine. It:
  - **Discovers a component if it has `main.tex` or `main.pdf`.** Authored components
    (`main.tex`) are compiled; prefab components (`main.pdf`) are used as-is from the source
    tree. A directory with neither is skipped.
  - Compiles each `<comp>/main.tex` with
    `latexmk -xelatex -interaction=nonstopmode -halt-on-error -file-line-error`,
    sending output to `target/UNIT/LESSON/<comp>/` and a stamp to `.stamps/`.
  - Builds two merged packets:
    - **student** = `cover warmup notes activity exit_ticket homework` (blank versions present),
      in that pedagogical order → `lessonYY_student.pdf`.
    - **key** = the *same list*, with each component swapped for its `_key` sibling where one
      exists (the cover has none, so it appears unchanged in both) → `lessonYY_key.pdf`.
      Deriving the key list from the student list is what makes the two packets pair up 1:1.

## Commands

```bash
make -C unitXX/lessonYY all       # all five products
make -C unitXX/lessonYY plan      # lessonYY_plan.pdf
make -C unitXX/lessonYY slides    # lessonYY_slides.pdf AND lessonYY_slides.pptx
make -C unitXX/lessonYY pptx      # just the .pptx
make -C unitXX/lessonYY student   # lessonYY_student.pdf
make -C unitXX/lessonYY key       # lessonYY_key.pdf
make -C unitXX/lessonYY clean     # remove this lesson's target/ and stamps

PPTX_DPI=150 make -C unitXX/lessonYY pptx   # trade sharpness for file size (default 300)

make -C unitXX student|key        # merge a whole unit
make student|key                  # merge the whole curriculum (from project root)
make clean | distclean            # clean everything (distclean also removes target/ and .stamps)
```

Outputs land in `target/`: per-component PDFs under `target/UNIT/LESSON/<comp>/main.pdf`,
products and packets under `target/compiled/`.

**At the lesson level, `student` and `key` each compile every component of *both* packets** —
`ALIGN_STAMPS` — because each slot is sized against its counterpart. They still emit only their
own packet: `make student` on a clean tree gives you `lessonYY_student.pdf` and no
`lessonYY_key.pdf`. Use `make all` for both. The alignment does not depend on building them
together; the slots come out the same either way.

**At the unit level, `student` and `key` each build both packets of every lesson**, since the
unit pass needs the actual lesson PDFs on both sides.

**Always build with `make all`** when the lesson plan embeds a warm-up thumbnail: the thumbnail
uses the warm-up, and `key` alone (from a clean tree) would build only the `_key` versions —
except that `key` now builds the blanks too, so this is no longer a real hazard. Authored
warm-ups are text-only in the plan (no thumbnail); prefab warm-ups embed `warmup/main` (the PDF
in the source tree), which resolves regardless of order.

## Scaffolding a lesson

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/new_lesson.py --project . --unit 02 --lesson 03 \
  --title "..." --unit-title "..." \
  --components cover,warmup,notes,activity,exit_ticket,homework[,slides] \
  [--prefab warmup,warmup_key] [--course "Algebra 2: Shepherd"] [--lesson-id 2.3]
```

It detects the prefix from `shared/*-colors.sty`, detects whether `\CourseName` is defined in
`shared/` (omitting it from the plan if so, inlining it if not), writes the one-line `Makefile`,
the lesson plan, and each authored component + key skeleton. Pass `--prefab <dirs>` to create
empty drop-in directories instead (where you place each `main.pdf`). Then author the skeletons
(`references/components.md`).

## Pagination: how a packet gets its page numbers

Each component is compiled as its own document, so each numbers its pages from 1. A raw
`pdfunite` merge would read `1 / 1 / 1 2 3 / 1 2 …` instead of `1 … 16`. After the merge,
**`shared/paginate.sh`** rebuilds the packet through **`shared/paginate.tex`**, which does three
things at once:

1. **Packet-wide numbering.** Each source page is placed at full size on a same-size sheet; a
   white band inside the bottom margin covers the component-local number and the packet-wide
   number is printed in exactly its place. Nothing is rescaled.
2. **Recto starts.** Every component begins on an odd (right-hand) page; blank versos are
   inserted where needed, and they *are* numbered, so a student flipping through sees an
   unbroken run.
3. **Student/key alignment.** Each component occupies the same slot in both packets —
   `slot = ceil_even( max(blank pages, key pages) )` — and the shorter one is padded to fill it.
   Page 11 of the key is page 11 of the student packet. Both targets compute the same slots from
   the same two lists, so they stay aligned whether built together or separately.

The pass is **idempotent**: the band covers whatever number is already on the page. That is what
lets `shared/unit.mk` re-run it over a unit packet merged from already-paginated lesson packets,
giving continuous unit-wide numbering without the two schemes fighting. The unit pass pairs
`[unit_cover, lesson01_student, …, sample_test]` against
`[unit_cover, lesson01_key, …, sample_test_key]`, so unit packets are recto-correct and
page-for-page end to end.

This replaced the `unitXX_student.tex` / `unitXX_full.tex` `docmute` wrappers, which achieved
continuous numbering for the one unit that had them at the cost of a hand-maintained file per
unit (and hand-counted slide page numbers). **Don't reintroduce them** — there is no per-lesson
or per-unit wrapper `.tex` in this project any more, and pagination is owned by exactly one
layer.

Geometry note: `paginate.tex`'s band constants are matched to `apstats-article.sty` (bottom
margin 0.75in, footer baseline 24.2pt above the page edge, band spanning 10–42pt). If that
geometry changes, re-measure with `pdftotext -f <p> -l <p> -bbox packet.pdf out.html` and check
the footer digit's box.

**Slides.** `unitXX/lessonYY/slides/main.pdf` stays one slide per page and is never included in
the student packet. Two products come off it:

- `lessonYY_slides.pdf` — `shared/handout.tex` re-frames it 3-up with a note column. The deck's
  page count comes from `pdfinfo`, not a hand-written number.
- `lessonYY_slides.pptx` — `shared/pdf2pptx.py` rasterizes each page at `PPTX_DPI` (default 300)
  and writes the OOXML package with `zipfile`. **Stdlib + poppler only** — no LibreOffice, no
  `python-pptx`, nothing to install. Slides are page images, not editable text boxes, so TikZ and
  math render exactly as in the PDF. The deck is scaled to a standard 7.5in-tall canvas
  (16:9 → 13.333×7.5in), because Beamer's native 160×90mm reads as a non-standard canvas
  everywhere else.

Fed the **raw** deck, not the 3-up handout — a PowerPoint of handout pages would be useless to
project.

**Do not reintroduce:** unit or lesson wrapper `.tex` files; lesson plans inserted into a packet;
slides in the student packet; any Node-based or LibreOffice-based conversion step.

After changing a unit: delete stale stamps, run `make -C unitXX student`, then check
`pdfinfo target/compiled/unitXX_student.pdf` and `unitXX_key.pdf` — **the two page counts must
match**. Render the first and last page of `lessonYY_slides_3up.pdf` for a lesson with a
non-multiple-of-3 slide count to confirm thumbnails and notes areas don't overlap or clip.

## Prefab PDFs

To include a ready-made PDF as a component, drop it in as `<comp>/main.pdf` (and
`<comp>_key/main.pdf` for a prefab key). `lesson.mk` discovers it and feeds it straight to
`pdfunite` — no `main.tex`, no compile step. `make clean` removes only `target/` and stamps, so
your source PDFs are never deleted. (Requires the `lesson.mk` that discovers `main.pdf`; older
Makefiles that glob only `main.tex` will silently omit prefab-only components — update first.)

## Troubleshooting

`-file-line-error` makes errors report as `file:line: message`. Read the component's log at
`target/UNIT/LESSON/<comp>/main.log`. Common issues:

- **`File 'warmup/main' not found`** in the lesson plan → the plan embeds a thumbnail but the
  warm-up isn't built/present. Build `student` first, or (authored warm-ups) keep the spiral
  review text-only, or (prefab) ensure the PDF is present as `warmup/main.pdf` so the thumbnail
  (`\includegraphics{warmup/main}`) resolves.
- **`Undefined control sequence \CourseName`** → the course macros aren't defined. Either the
  style package defines them (apstats) or the lesson plan must (algebra2); the scaffolder picks
  the right one, but a hand-edited plan may have dropped them.
- **`\includegraphics` fails for a screenshot** → put images in `images/` (the plan sets
  `\graphicspath{{images/}}`) and load `graphicx` (the plan does; `-article` does not).
- **Key won't compile / option clash** → a key loads `-key` only; do **not** also load
  `-boxes` (it's pulled in). Mirror the blank, swapping that one package line.
- **Garbled glyphs or font errors** → the build is XeLaTeX-only (it uses `unicode-math` /
  `fontspec`-style features); don't compile with `pdflatex`. `latexmk -xelatex` is set in
  `lesson.mk`.
- **`pdfunite: command not found`** → install poppler-utils.
- **A new component didn't appear in the packet** → its directory has neither `main.tex` nor
  `main.pdf`, or its name isn't in `STUDENT_ORDER`/`KEY_ORDER`. Use the standard component names.

If a fix seems to require changing `shared/` or a Makefile, stop and raise it — that's a
project-level refactor, not a per-lesson change.
