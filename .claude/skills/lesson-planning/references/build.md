# Build System

The project compiles with **XeLaTeX** (via `latexmk`) and merges PDFs with **`pdfunite`**
(poppler). The skill authors `.tex`; the project's own Makefiles do the building. **Never edit
`shared/` or the Makefiles to make a lesson build — fix the lesson's `.tex` instead.**

## The three-level Make hierarchy

- **Root `Makefile`** — discovers `unit*/Makefile`, delegates, and merges unit PDFs into
  `target/compiled/curriculum_{student,full}.pdf`.
- **`shared/unit.mk`** (included by each `unitXX/Makefile`) — discovers `lesson*/Makefile`,
  delegates, and produces `target/compiled/unitXX_{student,full}.pdf`. **Two modes:** if the unit
  provides `unitXX_student.tex` / `unitXX_full.tex`, it compiles that wrapper with `latexmk`;
  otherwise it falls back to a `pdfunite` merge of the lesson PDFs. It also picks up the optional
  unit bookends `unit_cover/main.tex`, `sample_test/main.pdf`, and `sample_test_key/main.pdf`
  (the sample-test key goes into the **full** packet only).
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
    - **full** = the lesson plan (`main.tex`) + `slides` + `cover` + the **`_key`** version of
      each keyed component (falling back to the blank if no key) → `lessonYY_full.pdf`.

## Commands

```bash
make -C unitXX/lessonYY student   # student packet for one lesson
make -C unitXX/lessonYY full      # teacher/full packet (plan + slides + keys)
make -C unitXX/lessonYY all       # both (runs student then full)
make -C unitXX/lessonYY clean     # remove this lesson's target/ and stamps

make -C unitXX student|full       # merge a whole unit
make student|full                 # merge the whole curriculum (from project root)
make clean | distclean            # clean everything (distclean also removes target/ and .stamps)
```

Outputs land in `target/`: per-component PDFs under `target/UNIT/LESSON/<comp>/main.pdf`,
merged packets under `target/compiled/`.

**Always build with `make all` (or `student` before `full`)** when the lesson plan embeds a
warm-up thumbnail: the thumbnail uses the warm-up, and `full` alone (from a clean tree) builds
only the `_key` versions. Authored warm-ups are text-only in the plan (no thumbnail); prefab
warm-ups embed `warmup/main` (the PDF in the source tree), which resolves regardless of order.

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

## Unit packets from a TeX wrapper (preferred)

A `pdfunite` merge restarts page numbers at every component. Building the unit packet from a
wrapper `.tex` instead gives the whole unit **one continuous page-number sequence**, and lets the
student and key packets be paginated page-for-page against each other. `shared/unit.mk` uses the
wrapper automatically when it exists.

**`unitXX_student.tex`** source-includes, in order:
1. `unit_cover`
2. each lesson's blank components: `cover`, `warmup`, `notes`, `activity`, `exit_ticket`, `homework`
3. `sample_test/main.pdf`, if present

**`unitXX_full.tex`** (teacher packet) source-includes:
1. `unit_cover`
2. each lesson plan **from source** — `\subimport{lessonYY/}{main.tex}`, never as an inserted PDF,
   so the plan participates in the packet's page numbering
3. a **3-up slide handout** — portrait letter, 3 slide thumbnails in a left column with a matching
   `Notes:` area in a right column. Full packet only.
4. each lesson's keyed components: `cover`, `warmup_key`, `notes_key`, `activity_key`,
   `exit_ticket_key`, `homework_key`
5. `sample_test/main.pdf` and `sample_test_key/main.pdf`, if present

Use `docmute` + `import` to pull in component `main.tex` files from source; use `pdfpages` only
for genuine prefab PDFs (sample tests, slide handouts). Wrap `\subimport` calls in a local group.

Lesson plans sometimes need small adjustments to be source-includable: put metadata definitions
such as `\UnitNumberName` / `\LessonNumberName` **after** `\begin{document}`, and avoid
preamble-only code that assumes the plan is always a root document.

**Slides.** `unitXX/lessonYY/slides/main.pdf` stays one slide per page — that is the display and
Google Slides import artifact, and it is never included in the student packet. The 3-up handout is
derived from it for the teacher packet only. The Unit 1 wrapper hard-codes each lesson's slide page
count; get the numbers for another unit from the compiled decks with `pdfinfo`.

**Do not reintroduce:** `pdfunite` for a unit that has wrappers; lesson plans inserted as PDFs;
slides in the student packet; any Node or PowerPoint generation step.

After adding wrappers for a unit: delete stale stamps, `make -C unitXX student`,
`make -C unitXX full`, then check `pdfinfo target/compiled/unitXX_full.pdf` for page count and
page size, and render the first and last slide-handout page for a lesson with a
non-multiple-of-3 slide count to confirm thumbnails and notes areas don't overlap or clip.
`UNIT_PACKET_REFACTOR_NOTES.md` at the project root has the Unit 1 reference numbers.

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
