---
name: lesson-planning
description: >-
  Author complete, build-ready lessons for a LaTeX-based curriculum project (one with a
  shared/ style package and a Makefile hierarchy that compiles components with latexmk
  and merges them with pdfunite). Use this whenever the user wants to create, draft, or
  build a lesson, a lesson plan, a unit, or any lesson component — warm-up, guided notes,
  activity, exit ticket, homework, cover sheet, or their answer keys — for a course like
  Algebra 2 or AP Statistics. If the course has College Board AP CED documents (files
  named ap-*), use them to drive objectives, skills, and standards; otherwise generate
  from a lesson title, description, and a list of standards. Trigger this even when the
  user just says "make lesson 2.3" or "I need a warm-up and key for tomorrow," and even
  if they don't say the words "skill" or "LaTeX."
  Also use it to RETROFIT an already-authored lesson to a named convention — boxguard,
  namestrip, vocabpar, the work rule, teachernotes — as in "apply boxguard namestrip
  retrofit to 1.1 and 1.3." See the Retrofit section.
---

# Lesson Planning

This skill authors lessons for an existing LaTeX curriculum project and produces print-ready
PDFs through the project's own build system. **It builds around the project's conventions —
it does not invent its own.** The two reference courses (`algebra2`, `apstats`) are
structurally identical: only the style-package prefix differs.

## What a lesson is

A lesson lives in `unitXX/lessonYY/` and consists of:

- **`main.tex`** — the teacher-facing **lesson plan** (the root document of the lesson dir).
- A set of **student components**, each its own subdirectory containing **either** a `main.tex`
  (authored, compiled to a PDF) **or** a `main.pdf` (a prefab PDF, used as-is):
  `cover`, `warmup`, `notes`, `activity`, `exit_ticket`, `homework`, and optional `slides`.
- An **answer key** for each keyed component, as a *separate* sibling directory:
  `warmup_key`, `notes_key`, `activity_key`, `exit_ticket_key`, `homework_key`.
  (`cover` has no key.)

`shared/lesson.mk` discovers a component if it has a `main.tex` **or** a `main.pdf`, compiles
the `main.tex` ones with `latexmk -xelatex`, and builds **five work products**:
`lessonYY_plan.pdf` (the lesson plan), `lessonYY_slides.pdf` (the deck printed 3-up with a note
column) and `lessonYY_slides.pptx` (the same deck full-page, for projecting),
`lessonYY_student.pdf` (cover + blank components), and `lessonYY_key.pdf` (the same packet
answered, page for page with the student one). There is no `full` packet — the plan and the deck
stand on their own. A prefab `main.pdf` is fed straight to `pdfunite` from the source tree with no
compile step — so dropping in a ready-made PDF is all that's needed (Step 4).

## Multi-lesson dispatch — REQUIRED when generating more than one lesson

**When the request covers two or more lessons, do NOT author them sequentially.**
Spawn one subagent per lesson in a single message using the `Agent` tool, each briefed
with the lesson number, CED topic content, and a pointer to this skill. The coordinator
(this agent) gathers CED content first (Step 0–1 below, once), then fans out.

Pattern for a two-lesson request:

```
# Coordinator does once:
- detect prefix, read one model lesson, extract CED topics for L7.4 and L7.5

# Coordinator scaffolds ALL lesson directories before spawning subagents:
python3 .claude/skills/lesson-planning/scripts/new_lesson.py --project . --unit 07 --lesson 04 --components cover,warmup,notes,activity,exit_ticket,homework
python3 .claude/skills/lesson-planning/scripts/new_lesson.py --project . --unit 07 --lesson 05 --components cover,warmup,notes,activity,exit_ticket,homework

# Then in ONE message, spawn two agents in parallel:
Agent(lesson=7.4, ced_content=..., model_lesson_path=...)
Agent(lesson=7.5, ced_content=..., model_lesson_path=...)

# Each subagent uses the Write tool only to fill in content (no Bash needed).
# Coordinator then runs: make -C unit07/lesson04 all && make -C unit07/lesson05 all
# and verifies warmup/exit_ticket page counts before opening the PR.
```

**Why the coordinator must scaffold:** Subagents run in a fresh permission context and
may not have auto-approved Bash access. Scaffolding requires running `python3 new_lesson.py`
(Bash). The coordinator always has this permission; subagents often do not. Scaffolding
first means subagents only need the Write tool to fill in content.

Each subagent receives: (a) the extracted CED content for its single lesson,
(b) the path of one model lesson to mirror, (c) the known-errors checklist below,
and (d) instructions to use Write tool only (coordinator handles build/verify). The
coordinator collects results, builds all lessons, verifies page counts, and opens one PR.

## Hard constraints — read before authoring a single line

These rules are non-negotiable. They recur every lesson if not followed.

### 1. One page: warmup and exit ticket

The warmup and exit ticket (blank AND key) must each fit on **exactly one printed page**.
Design to fit one page from the start — do not draft long and trim later.
Budget: `\pageheader` + `\namedateperiod` + content ≈ 3–4 questions max.

After building, verify before moving on:
```bash
pdftoppm -r 72 target/unitXX/lessonYY/warmup/main.pdf /tmp/wm \
  && ls /tmp/wm*.ppm | wc -l     # must print 1
pdftoppm -r 72 target/unitXX/lessonYY/exit_ticket/main.pdf /tmp/et \
  && ls /tmp/et*.ppm | wc -l     # must print 1
```
If either prints > 1: cut a question, rebuild, re-check. Do not continue until both return 1.
Same check for their keys.

### 1b. Page-for-page: a component is the same length blank and keyed

Every component must come out the **same number of pages** as its `_key`. The student packet and
the key packet are paginated against each other, so a key that runs one page long costs the
student packet a blank page.

The pagination pass **pads the mismatch rather than reporting it** — it gives the component a
slot of `max(blank, key)` pages in both packets and fills the short one with a blank verso. The
packets stay aligned either way, which means a violation is silent. Check the component page
counts; don't wait for a build to complain.

Two mechanisms enforce it — use them while authoring, not as a cleanup pass:

- **`work` blocks** for every multi-step solution, authored **byte-identically in the blank and
  the key**. The blank reserves the block's exact height and prints nothing; the key prints it in
  `keyred`. They cannot drift.
- **Teacher notes in the lesson plan, never in a `_key`** — a note is the one block in a key with
  no counterpart in the blank.

Verify after building:
```bash
for c in warmup notes activity exit_ticket homework; do
  b=$(pdfinfo target/unitXX/lessonYY/$c/main.pdf      | awk '/^Pages/{print $2}')
  k=$(pdfinfo target/unitXX/lessonYY/${c}_key/main.pdf | awk '/^Pages/{print $2}')
  [ "$b" = "$k" ] && echo "OK   $c $b" || echo "DRIFT $c blank=$b key=$k"
done
```
Full spec — `work`, `steptable`, the `\ansline`/`\writelines` trap — in `references/conventions.md`.

### 1c. `\boxguard` before every breakable box

Never let a box break leaving a ~1in sliver — a title plus a line or two — at a page edge. Put
`\boxguard` on its own line immediately before the `\begin{...}`, in the blank **and** the key:

```latex
\boxguard                 % 16 lines must remain, else the box starts a new page
\begin{notesbox}{2. Checking the conditions}

\boxguard[30]             % raise it when the box opens with an unbreakable TikZ figure or table
```

Prefer it to a hard `\newpage` — it self-adjusts when content above it changes.

### 2. No "sketch the…" questions

Never ask students to draw, sketch, or construct a graph freehand anywhere (warmup,
exit ticket, notes, activity, homework). Replace with: (a) a pre-drawn figure to
read/interpret, (b) a table to fill in, or (c) a computation question.

### 3. `\ans{}` is a TEXT-MODE macro — two hard rules

`\ans{text}` expands to `\textcolor{keyred}{\textbf{#1}}`. Its argument is text mode.

**Rule A — `\ans{}` must NEVER appear inside `$...$` or `\[...\]`.**
Close math first, call `\ans{}`, reopen math if needed.

```latex
% WRONG — causes compile error every time:
$SE = \dfrac{\ans{0.8}}{\sqrt{\ans{25}}}$

% RIGHT — close math, then \ans, then reopen:
$SE = \dfrac{s}{\sqrt{n}} = $ \ans{$0.8 / \sqrt{25} \approx 0.16$}

% ALSO RIGHT — in-formula filled slots use {\color{keyred}\mathbf{...}}:
$SE = \dfrac{{\color{keyred}\mathbf{0.8}}}{\sqrt{{\color{keyred}\mathbf{25}}}} \approx $ \ans{0.16}
```

**Rule B — Never put math-only commands bare inside `\ans{}`.**
`\sqrt`, `\dfrac`, `\hat`, `\overline`, `\ne`, `_`, `^` fail in text mode.
Wrap them in `$...$` inside `\ans{}`:

```latex
% WRONG:  \ans{\sqrt{n}}   \ans{s/\sqrt{n}}   \ans{\hat p}
% RIGHT:  \ans{$\sqrt{n}$} \ans{$s/\sqrt{n}$} \ans{$\hat p$}
```

After writing each key file, grep for `\\ans{` and confirm every hit is in text mode.

### 4. `fixedskillbox` does not exist — use `skillbox`

The only lesson-plan box environment is `skillbox`. `fixedskillbox` is not defined and
causes "Environment fixedskillbox undefined" every time.

```latex
% WRONG:  \begin{fixedskillbox}[...]{sky}
% RIGHT:  \begin{skillbox}[...]{sky}
```

After writing each lesson plan, grep for `fixedskillbox` and confirm zero hits.

### 5. Other known-bad patterns (do not use)

- `\ding{55}` — `pifont` not loaded; use `\textbf{$\times$}` instead
- bare `gold` color — use `goldbg` / `goldacc`
- `\usepackage{apstats-boxes}` in a key file — keys use `apstats-key` only (it includes boxes)
- `fixedskillbox` anywhere (see rule 4)
- `tierbox` — does not exist; use `tcolorbox` with `[colback=white, colframe=black!40, title=\textbf{Tier R --- ...}, fonttitle=\bfseries, arc=2mm, left=3mm, right=3mm, top=2mm, bottom=2mm]`

### 6. Only use colors defined in `shared/*-colors.sty`

Before using any color name in a box or tcolorbox, verify it is defined in the project's
color file (`shared/<prefix>-colors.sty`). Never invent color names. Defined colors for
`apstats`:

```
navy  navylight  sky  skymid  goldacc  goldbg  hookbg
greenbg  greenacc  redbg  redacc  charcoal  slate  linegray  keyred
goldbox  greenbox  redbox
```

Any other name (e.g. `bluebox`, `purplebox`, `orangebox`, `gold`) is **undefined** and will
cause a compile error. When in doubt, `grep` the `.sty` file for the color name first.

## Workflow

Follow these steps in order. Read the referenced files as you reach each step rather than
all upfront.

### Step 0 — Detect project context (always do this first)

Never assume the prefix or conventions. Inspect the project:

1. **Find the prefix.** `ls shared/*-colors.sty` → the prefix is the part before `-colors.sty`
   (e.g. `algebra2`, `apstats`). All `\usepackage{<prefix>-article}` etc. must use it.
2. **Learn course-level macros.** Grep the shared styles and an existing lesson plan for
   `\CourseName`, `\SchoolYear`, `\MeetingLength`, `\UnitNumberName`, `\LessonNumberName`.
   Some courses define course-level macros inside the style package (apstats); others define
   them per lesson plan (algebra2). Define in the new files only what isn't already provided.
3. **Choose the input path.** Look for College Board CED files in a `spec/` directory, named
   `ap-*.pdf` (the detailed `...course-and-exam-description.pdf`, the `...course-at-a-glance.pdf`,
   and supporting overview/poster files). If present → **AP path** (`references/ap-workflow.md`).
   If absent → **standards path** (`references/standards-workflow.md`). In an AP course, one CED
   **Topic** (e.g. Topic 1.1) maps to one lesson (Lesson 1.1).
4. **Find the insertion point.** List `unit*/lesson*` to determine the next unit/lesson
   number and whether the target lesson already exists.
5. **Read one built lesson as a model.** Open an existing fully-built lesson in the same
   course (or, if none, the closest sibling course) and mirror its preamble lines, box usage,
   and tone. Conventions are summarized in `references/conventions.md`, but the live project
   is the source of truth.

### Step 1 — Gather inputs

- **AP path:** locate the CED, extract the unit → topic → Learning Objective → Essential
  Knowledge content relevant to this lesson, plus the governing Big Idea and AP Skill. See
  `references/ap-workflow.md`. Confirm the topic mapping with the user before authoring.
- **Standards path:** collect the lesson title, a short description, and the list of standards
  being addressed. See `references/standards-workflow.md`.

Either way, the lesson-plan *structure* is identical (`references/components.md` → "Lesson
plan"). Review units (e.g. Algebra 2 Unit 1) use the same skeleton; they simply fill the
Priority Ideas & Skills with review topics and usually carry no AP-framework tags.

### Step 2 — Scaffold the lesson directory

Run the scaffold script, which creates the directory, the one-line `Makefile`
(`include ../../shared/lesson.mk`), and the component subdirectories you request:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/new_lesson.py --project . --unit 02 --lesson 03 \
  --components cover,warmup,notes,activity,exit_ticket,homework,slides
```

The script is bundled with the skill, so it is invoked via `${CLAUDE_SKILL_DIR}` (the working
directory at runtime is the user's project, not the skill folder); `--project .` is the project
root you're working in.

It auto-detects the prefix and writes each authored component's `main.tex` as a correctly-
preambled skeleton (and the matching `_key` skeleton for keyed components). Pass `--prefab warmup`
to create that component as an empty drop-in directory instead, where you place the supplied
`main.pdf` (Step 4). Then fill in the skeletons.

### Step 3 — Author the lesson plan and components

**Before writing any component, do a full `Read` on each scaffolded `main.tex` skeleton you are
about to replace.** Use the `Read` tool on the actual file — a `cat`/`bash` dump does **not**
register the file with the editor and the first write will fail ("file has not been read yet").
Read every skeleton you intend to author (each component and its `_key`) up front, then write them.

Author each file following `references/components.md`, which gives the required section
structure and a worked skeleton for every component and its key. Hold to these invariants:

- **Student components** preamble with `\documentclass[10pt]{article}` +
  `\usepackage{<prefix>-article}` + `\usepackage{<prefix>-boxes}`.
- **Answer keys** are *separate files* that swap `-boxes` for `\usepackage{<prefix>-key}`
  and wrap every answer in `\ans{...}` (inline) or `\ansline{...}` (fills a write-line).
  Mirror the blank document exactly, then fill the blanks with `\ans`. There is **no**
  answer-key toggle — never try to build one.
- **Teacher notes go in the lesson plan, not in a key** — one `teachernote` per component, in
  packet order, titled for it: `\begin{teachernote}[Exit Ticket]` → "Teacher Note: Exit Ticket".
  A note in a key is the one block with no counterpart in the blank, so it makes the key run
  longer and costs the student packet a blank page.
- **The work rule: a component must be the same number of pages blank and keyed.** Put every
  worked solution in a `work` block — one statement per line, `&` before the relation so the whole
  block aligns on it — authored **byte-identically in the blank and the key**. The blank reserves
  the block's exact height and prints nothing; the key prints it. Never cram steps into one line
  as `$a=b \Rightarrow c=d$`. Full spec in `references/conventions.md`.
- **`\boxguard` before every breakable box**, in the blank and the key both (see Hard constraint 1c).
- **Namestrip: `\namedateperiod` on the cover only.** No name row on warmup, notes, activity,
  exit ticket, or homework — the packet is stapled behind its cover.
- Use the project's box vocabulary (`skillbox`, `objectivebox`, `learningtargetbox`,
  `vocabbox`, `hookbox`, `notesbox`, `practicebox`, `scenariobox`, `tocbox`, etc.) and
  fill-in helpers (`\blank`, `\writeline`, `\termblanklong`) rather than reinventing layout.
  The full catalog is in `references/conventions.md`.
- **`\par` around `\termblanklong`/`\ansline` inside a `vocabbox`** (the vocabpar fix) — without
  it the intro sentence collides with the first term, and key answers drag onto the wrong line.
- If the warm-up is a **prefab** PDF (`warmup/main.pdf` in the source tree), the lesson plan may
  embed its thumbnail via `\includegraphics[page=1]{warmup/main}`. **Authored** warm-ups compile
  to `target/` and have no source PDF to embed, so keep the spiral review text-only (as AP Stats
  does); the scaffolder picks the right form automatically.

### Step 4 — Handle prefab components

When the user supplies a ready-made PDF for a component (a pre-built warm-up, a publisher
worksheet), just drop it in — no wrapper needed:

1. Place the PDF as `<comp>/main.pdf` (e.g. `warmup/main.pdf`).
2. If the key is also a prefab PDF, place it as `<comp>_key/main.pdf`.

`shared/lesson.mk` discovers the component by its `main.pdf` and feeds it straight to `pdfunite`,
skipping compilation. Use `--prefab <comp>` when scaffolding to create the empty drop-in
directory. (This relies on the `lesson.mk` that supports prefab `main.pdf` discovery — if a
project's Makefile still only globs `main.tex`, update it first; see `references/build.md`.)

### Step 5 — Build

Build from the lesson directory (or the unit/root for wider packets):

```bash
make -C unit02/lesson03 all       # all five products
make -C unit02/lesson03 plan      # the lesson plan            → lessonYY_plan.pdf
make -C unit02/lesson03 slides    # the deck, both forms       → lessonYY_slides.pdf + .pptx
make -C unit02/lesson03 student   # cover + blank components   → lessonYY_student.pdf
make -C unit02/lesson03 key       # the same packet, answered  → lessonYY_key.pdf
```

`make -C unit02 student|key` merges a unit; `make student|key` at the root merges the whole
curriculum. Output lands in `target/`. The build needs XeLaTeX, `latexmk`, and `pdfunite`;
if a compile fails, surface the `.log` and fix the offending `.tex` rather than editing the
build system. Details and troubleshooting in `references/build.md`.

**There is no `make full`** — it fails loudly and tells you what replaced it. `key` is the
successor to the old `full` packet; the lesson plan and the deck it used to swallow are now
standalone products. The deck ships in two forms — `lessonYY_slides.pdf` (3-up, printable) and
`lessonYY_slides.pptx` (full-page, projectable) — both built by `make slides` from the one
Beamer deck. Never edit either; edit `slides/main.tex`.

**Pagination is owned by one layer.** After `pdfunite` merges the components,
`shared/paginate.sh` renumbers the packet lesson-wide, forces every component onto a recto, and
lays the student and key packets against each other so page N of one is page N of the other.
`shared/unit.mk` re-runs the same pass over the merged unit packet for unit-wide numbering — the
pass is idempotent, so nothing is numbered twice. **Never add a wrapper `.tex`** (the old
`unitXX_student.tex` / `unitXX_full.tex` pattern is retired), never put slides in the student
packet, and never insert a lesson plan into a packet. Full detail in `references/build.md`.

Because slots are sized against the counterpart, `student` and `key` each *compile* every
component of both packets — but each emits only its own packet. **Use `make all` when you want
both PDFs.** Building them separately is safe: the slots come out identical either way.

### Step 6 — Compile QA before any PR

`make` stops at the first error, so scan every document first. Compile **out of tree** —
an in-place `xelatex` overwrites tracked `main.pdf` files in the source directories:

```bash
ROOT=$(pwd); mkdir -p /tmp/scan
find unitXX -name main.tex | while read f; do
  d=$(dirname "$f"); o=/tmp/scan/$(echo "$d" | tr / _); mkdir -p "$o"
  (cd "$d" && TEXINPUTS="$ROOT/shared//:" xelatex -halt-on-error -interaction=nonstopmode \
     -output-directory="$o" main.tex > "$o/scan.log" 2>&1) \
    && echo "OK: $f" || { echo "FAIL: $f"; grep -m3 "^!" "$o/scan.log"; }
done
```

Collect ALL failures, fix them, re-scan to confirm zero, then delete stale stamps
(`find .stamps/unitXX -name '*.stamp' -delete`) and run `make`.

## Retrofit — apply a named convention to a lesson already authored

Conventions land after lessons are written, so an existing lesson can be behind on one. The user
invokes this by name:

> `/lesson-planning apply boxguard namestrip retrofit to 1.1 and 1.3`

Apply **only the conventions named** (all of them if none are named), to the lessons named, then
build and report. Each has a fix and, where it is mechanical, a script:

| Name | The rule | How to apply |
| --- | --- | --- |
| **boxguard** | No box stranded as a ~1in sliver across a page break | `\boxguard` (or `\boxguard[n]`) on its own line before the `\begin{...}` — blank **and** key |
| **namestrip** | Name/date/period row on the cover only | `python3 .claude/skills/lesson-planning/scripts/namestrip.py --project . --unit NN --lesson MM` (`--check` to preview) |
| **vocabpar** | `\par` around `\termblanklong`/`\ansline` in a `vocabbox` | Hand fix per lesson |
| **work rule** | A component is the same length blank and keyed | `work` blocks authored identically in both files; `steptable`/`\step` for printed solutions; `\writelines{n}` to match a wrapped `\ansline` |
| **teachernotes** | Teacher prose in the lesson plan, one titled note per component | `python3 .claude/skills/lesson-planning/scripts/movenotes.py unitNN/lessonMM` (`--check` to preview) |
| **deck** | Every lesson has a `slides/` Beamer deck | If `slides/main.tex` is absent, author one from `assets/skeletons/slides.tex` — see below |

Full spec for each: `references/conventions.md`.

**A lesson with no deck is incomplete.** The deck feeds two of the five work products
(`lessonYY_slides.pdf` and `lessonYY_slides.pptx`), so a lesson without `slides/main.tex` builds
only three. Most of this course's lessons predate that rule. **When you review or retrofit a
lesson that has no deck, author one** — it is part of the review, not a separate request. Build
it into the existing lesson (its own `slides/` subdirectory); `slides` has no `_key`.

**Always finish a retrofit with the evidence**, per lesson: `make -C unitXX/lessonYY all` exits 0,
and every component's page count equals its `_key`'s (Hard constraint 1b). Compare the compiled
components under `target/unitXX/lessonYY/<comp>/main.pdf` — comparing `lessonYY_student.pdf`
against `lessonYY_key.pdf` proves nothing, since the pagination pass pads them to equal length no
matter what. Report any component that still differs and why.

**Scope note for this course.** Nothing is retrofitted yet: ~136 `_key` files still carry teacher
notes, `\namedateperiod` appears on every component rather than the cover alone, and **57 of 80
lessons have no deck**. Retrofit lesson by lesson (or unit by unit) as you review, authoring the
missing deck as you go, and rebuild the unit packet each time — do not attempt the whole course
in one pass.

## Reference files

- `references/conventions.md` — the style packages, every box environment, the fill-in and
  answer-key macros, color palette, and per-document-type preambles. Read before authoring.
- `references/components.md` — section-by-section spec and a skeleton for the lesson plan and
  each component + key.
- `references/ap-workflow.md` — reading an AP CED and mapping Big Idea / Skill / LO / EK into
  the lesson.
- `references/standards-workflow.md` — the title + description + standards path.
- `references/build.md` — the Makefile hierarchy, unit packet wrappers, scaffolding, prefab PDFs,
  build commands, and troubleshooting.

## Scripts

- `scripts/new_lesson.py` — scaffold a lesson directory (Step 2). Emits namestrip-compliant
  components and a lesson plan pre-stubbed with one `teachernote` per component.
- `scripts/namestrip.py` — retrofit: remove the name row from every component but `cover`.
- `scripts/movenotes.py` — retrofit: lift each `_key`'s teacher note into the lesson plan, titled
  for its component.

Both retrofit scripts take `--check` to preview without writing.

## Guardrails

- Detect, don't assume: prefix, course macros, and the AP-vs-standards path all come from
  inspecting the project (Step 0).
- **Full `Read` each skeleton before writing it** (Step 3). A `bash`/`cat` dump does not register
  the file with the editor, so the write fails; always use the `Read` tool first.
- Mirror an existing built lesson for tone and preamble; the live project overrides this doc.
- Keep blank and key documents in lockstep — the key is the blank with answers filled in, and it
  must come out the **same number of pages**. Worked solutions live in shared `work` blocks (the
  work rule); teacher prose lives in the lesson plan; a key that runs long costs the student
  packet blank padding.
- Don't modify `shared/` or the Makefiles to make a lesson build; fix the lesson's `.tex`.
- **Multi-lesson requests → parallel subagents.** See "Multi-lesson dispatch" above.
- **One-page warmup and exit ticket** — verify with `pdftoppm` after every build. See "Hard constraints" above.
- **`\ans{}` in text mode only; `skillbox` not `fixedskillbox`** — grep-check every file before building. See "Hard constraints" above.
- **Compile QA out of tree** — `-output-directory` to a temp dir; an in-place `xelatex` clobbers
  tracked `main.pdf` files in the source directories.
- **Retrofit requests are a first-class mode**, not authoring — apply only the named conventions,
  then prove it with build + page-count evidence.
