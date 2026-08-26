---
name: lesson-planning
description: >-
  Author complete, build-ready lessons for the AP Statistics LaTeX curriculum (a project with a
  shared/ style package — prefix apstats — and a Makefile hierarchy that compiles components with
  latexmk and merges them with pdfunite).
  Use this whenever the user wants to create, draft, or build a lesson, a lesson plan, a unit, or
  any lesson component — warm-up, Experience & Formalize (the experience component: activity +
  QuickNotes + application + check your understanding), homework, cover sheet, unit test, or their
  answer keys. Lessons follow the Math Medic "experience first, formalize later" (EFFL) model.
  Structure comes from the College Board AP Statistics CED in spec/ (files named ap-*): one CED
  Topic maps to one lesson. Trigger this even when the user just says "make lesson 2.3" or "I need
  a warm-up and key for tomorrow," and even if they don't say the words "skill" or "LaTeX."
  Also use it to RETROFIT an already-authored lesson to a named convention — boxguard, namestrip,
  vocabpar, the work rule, teachernotes, deck — or to REGENERATE a pre-EFFL lesson in the EFFL
  shape, as in "apply boxguard namestrip retrofit to 1.1 and 1.3" or "regenerate unit 1 as EFFL."
  See the Retrofit section.
---

# Lesson Planning — AP Statistics

This skill authors lessons for the **AP Statistics** course and produces print-ready PDFs through
the project's own build system. **It builds around the project's conventions — it does not invent
its own.**

**Every new lesson follows the Math Medic "experience first, formalize later" (EFFL) model**
(mathmedic.com/how-it-works): students work an activity in small groups using only prior
knowledge; the teacher circulates with *questions, cues, and prompts — not answers*; a debrief
attaches the formal vocabulary to what the groups already found (QuickNotes); an application uses
it once together; then a practice set applies it to new contexts. There is **no separate
direct-instruction block, no guided-notes component, no exit ticket, and no tiered instruction.**
The 55-minute period runs **5 warm-up / 20 activity / 12 debrief / 6 application / 8 check your
understanding / 4 close & assign**.

**Naming rule — the component is called "Experience & Formalize."** That is the label on the
cover's packet table, the component's `\pageheader`, the deck's activity frame, the lesson plan's
activity box, and its teacher note — in LaTeX, `Experience \& Formalize`. The **directory keeps
the short name `experience/`** (with `experience_key/`): it is a build identifier hard-coded in
`shared/lesson.mk`'s `STUDENT_ORDER`/`KEYED_PAIRS`, and renaming it would mean editing the build
system, which this skill never does. **Directory `experience`, label *Experience & Formalize*.**

## What is different about this course

This course runs EFFL like Algebra 2, with three deliberate differences:

1. **Homework is retained.** AP Statistics needs AP-style multiple-choice and free-response reps.
   Check Your Understanding is *unscored in-class practice*; **homework is the graded practice**
   and is where AP-format items live. (Algebra 2 dropped homework entirely — do not copy that.)
2. **Structure comes from the AP CED**, not a course-plan document. One CED **Topic** maps to one
   lesson. See `references/ap-workflow.md`.
3. **There is no `fixedskillbox` and there are no tier boxes.** Every lesson-plan box is
   `skillbox` (breakable) preceded by `\boxguard`. The palette has no `forest` family.

## The course at a glance

- **Structure** comes from the **College Board CED** in `spec/` (`ap-statistics-course-and-exam-
  description.pdf` and the course-at-a-glance files): 9 units, 80 lessons. `COURSE_OUTLINE.md` at
  the project root is the current unit → lesson index.
- **Style prefix is `apstats`** — `shared/apstats-{colors,article,boxes,key}.sty`, plus
  `shared/apstats-beamer.sty` for the `slides` deck. Course macros (`\CourseName`, `\SchoolYear`,
  `\MeetingLength`) are defined **in the style package**, so a lesson plan sets only
  `\UnitNumberName` and `\LessonNumberName`. The printed title is **just `Statistics`** — no
  teacher name, no school year, anywhere a title renders.
- **Palette:** the course was recolored to an earthy-yellow scheme, so the color *names* no longer
  describe their hues — `navy` is a dark olive, `sky` is a pale cream. Use the names, not the hues,
  and only names defined in `shared/apstats-colors.sty`.

## What a lesson is

A lesson lives in `unitXX/lessonYY/` and consists of:

- **`main.tex`** — the teacher-facing **lesson plan** (the root document of the lesson dir).
- A set of **student components**, each its own subdirectory containing **either** a `main.tex`
  (authored, compiled to a PDF) **or** a `main.pdf` (a prefab PDF, used as-is):
  `cover`, `warmup`, **`experience`** (displayed as **Experience & Formalize**), `homework`,
  and `slides`.
- An **answer key** for each keyed component, as a *separate* sibling directory:
  `warmup_key`, `experience_key`, `homework_key`. (`cover` and `slides` have no key.)
- **`experience` — *Experience & Formalize* — is the heart of the lesson.** One document in
  **four** parts on a page budget: the group **Activity** (two scenarios worked from prior
  knowledge, **≤2pp**), a **QuickNotes** box the debrief fills (**½pp**), an **Application** worked
  together (**½–1pp**), and **Check Your Understanding** (**1–2pp**, in-class practice — **not
  scored**). See `references/components.md`.
- *Legacy shape:* the ~78 lessons authored before the 2026-08 EFFL redesign carry `notes`,
  `activity`, and `exit_ticket` dirs; the build accepts them and they keep working untouched. When
  asked to touch a legacy lesson, **ask whether to regenerate it in the EFFL shape** rather than
  patching the old components — see Retrofit.

### The five work products

Every lesson builds **exactly five files** into `target/compiled/unitXX/`:

| File | What it is |
| --- | --- |
| `lessonYY_plan.pdf` | the lesson plan — the lesson-root `main.tex`, compiled |
| `lessonYY_slides.pdf` | the deck from `slides/main.tex`, **printed** — 3 slides per page with a ruled notes column |
| `lessonYY_slides.pptx` | that same deck wrapped for PowerPoint, **full-page**, one page image per slide |
| `lessonYY_student.pdf` | cover + blank components, merged and paginated packet-wide |
| `lessonYY_key.pdf` | the same packet answered, **page for page** with the student one |

**There is no `full` packet** — `make full` fails loudly and says what replaced it. Because
`slides` feeds two of the five products, **every lesson owes a deck**; it is a default component,
not an optional one.

## What a unit is

A unit (`unitXX/`) holds its lessons plus **unit-level summative assessments**, scaffolded
automatically when the unit is first created (Step 2):

- **`tests/`** — the blank tests: **`practice_test/`** (a study copy students keep) and
  **`actual_test/`** (the real test, given in a testing setting). Its `Makefile`
  (`include ../../shared/tests.mk`) compiles both, and its `drop` target publishes the *practice*
  test to `sample_test/main.pdf`.
- **`test_keys/`** — **`practice_test_key/`** and **`actual_test_key/`**; its `drop` publishes the
  *practice* key to `sample_test_key/main.pdf`.
- **`sample_test/`** and **`sample_test_key/`** — prefab drop-in dirs that receive those PDFs (or a
  hand-dropped one). `shared/unit.mk` merges `sample_test` into the unit **student** packet and
  `sample_test_key` into the **key** packet. The **actual** test and its key are never merged into
  any packet — they stay out of student hands.
- **`unit_cover/`** and **`binder_cover/`** — the unit title page and the generated binder cover,
  merged at the front of the unit packet.

A unit aggregates **only the student and key packets** (`unitXX_{student,key}.pdf`); the plan, the
slide PDF, and the PPTX stay per-lesson.

## Hard constraints — read before authoring a single line

These rules are non-negotiable. They recur every lesson if not followed.

### 1. One page: the warm-up

The warm-up (blank **and** key) must fit **exactly one printed page**. Design to fit from the
start — do not draft long and trim later. Budget: `\pageheader` + content ≈ 3–4 questions max.

```bash
pdftoppm -r 72 target/unitXX/lessonYY/warmup/main.pdf /tmp/wm && ls /tmp/wm*.ppm | wc -l  # must be 1
```

*(There is no exit ticket in an EFFL lesson — the formative check is an item inside Check Your
Understanding. Legacy lessons still have `exit_ticket/`, which is also one page.)*

### 1b. Page-for-page: a component is the same length blank and keyed

Every component must come out the **same number of pages** as its `_key`. The student and key
packets are paginated against each other, so a key that runs one page long costs the student
packet a blank page.

The pagination pass **pads the mismatch rather than reporting it** — it gives the component a slot
of `max(blank, key)` pages in both packets and fills the short one with a blank verso. The packets
stay aligned either way, which means **a violation is silent**. Check the component page counts;
don't wait for a build to complain.

Three mechanisms enforce it — use them while authoring, not as a cleanup pass:

- **`\answerspace{H}{}`** in `experience/` — the blank reserves exactly `H`, the key prints the
  answer in the identical height. Authored byte-identically in both files.
- **`work` blocks** for every multi-step solution, authored **byte-identically in the blank and the
  key**. The blank reserves the block's exact height and prints nothing; the key prints it in
  `keyred`. They cannot drift.
- **Teacher notes in the lesson plan, never in a `_key`** — a note is the one block in a key with
  no counterpart in the blank.

Verify after building:
```bash
for c in warmup experience homework; do
  b=$(pdfinfo target/unitXX/lessonYY/$c/main.pdf       | awk '/^Pages/{print $2}')
  k=$(pdfinfo target/unitXX/lessonYY/${c}_key/main.pdf | awk '/^Pages/{print $2}')
  [ "$b" = "$k" ] && echo "OK    $c $b" || echo "DRIFT $c blank=$b key=$k"
done
```

### 1c. `\boxguard` before every breakable box

Never let a box break leaving a ~1in sliver — a title plus a line or two — at a page edge. Put
`\boxguard` on its own line immediately before the `\begin{...}`, in the blank **and** the key:

```latex
\boxguard                 % 16 lines must remain, else the box starts a new page
\begin{notesbox}{2. Checking the conditions}

\boxguard[30]             % raise it when the box opens with an unbreakable TikZ figure or tabularx
```

Prefer it to a hard `\newpage` — it self-adjusts when content above it changes. **Counts are
baseline-relative:** a value tuned at 10pt is ~40% oversized at 12pt, so in `experience/` use
**~14–16**, not 24–30.

### 2. No "sketch the…" questions

Never ask students to draw, sketch, or construct a graph freehand anywhere. Replace with: (a) a
pre-drawn display to read/interpret/annotate, (b) a table to fill in, or (c) a computation
question. Dotplots, histograms, boxplots, scatterplots, and computer output are always **given**.

### 3. `\ans{}` is a TEXT-MODE macro — two hard rules

`\ans{text}` expands to `\textcolor{keyred}{\textbf{#1}}`. Its argument is text mode.

**Rule A — `\ans{}` must NEVER appear inside `$...$` or `\[...\]`.**
Close math first, call `\ans{}`, reopen math if needed.

```latex
% WRONG — causes a compile error every time:
$SE = \dfrac{\ans{0.8}}{\sqrt{\ans{25}}}$

% RIGHT — close math, then \ans, then reopen:
$SE = \dfrac{s}{\sqrt{n}} = $ \ans{$0.8 / \sqrt{25} \approx 0.16$}

% ALSO RIGHT — in-formula filled slots use {\color{keyred}\mathbf{...}}:
$SE = \dfrac{{\color{keyred}\mathbf{0.8}}}{\sqrt{{\color{keyred}\mathbf{25}}}} \approx $ \ans{0.16}
```

**Rule B — Never put math-only commands bare inside `\ans{}`.**
`\sqrt`, `\dfrac`, `\hat`, `\overline`, `\ne`, `_`, `^` fail in text mode. Wrap them in `$...$`:

```latex
% WRONG:  \ans{\sqrt{n}}   \ans{s/\sqrt{n}}   \ans{\hat p}
% RIGHT:  \ans{$\sqrt{n}$} \ans{$s/\sqrt{n}$} \ans{$\hat p$}
```

After writing each key file, grep for `\\ans{` and confirm every hit is in text mode.

### 4. `fixedskillbox` does not exist — use `skillbox`

The only lesson-plan box environment is `skillbox`. `fixedskillbox` is not defined here (it exists
in Algebra 2 — do not copy it across) and causes "Environment fixedskillbox undefined" every time.
Where a phase table must stay intact, use `skillbox` preceded by `\boxguard[30]`: a `tabularx`
never splits on its own, so the guard is what protects it.

```latex
% WRONG:  \begin{fixedskillbox}[...]{sky}
% RIGHT:  \boxguard[30]
%         \begin{skillbox}[...]{sky}
```

After writing each lesson plan, grep for `fixedskillbox` and confirm zero hits.

### 5. The spoiler rule (EFFL)

Nothing the student sees *before* the activity — the cover, the warm-up, the deck's
learning-targets frame — may pre-name the vocabulary the debrief will attach. Write targets in
plain language ("how spread out the values are", not "standard deviation"; "how unusual this
result would be", not "p-value"), and keep the cover's Keep-in-Mind box to describing the EFFL
process itself. The **teacher-facing plan keeps the formal AP vocabulary** — the rule does not
apply there.

### 6. Other known-bad patterns (do not use)

- `\ding{55}` — `pifont` not loaded; use `\textbf{$\times$}` instead
- bare `gold` color — use `goldacc` / `goldbg`
- `forest`, `forestbg`, `forestmid`, `forestlight` — **Algebra 2 colors, undefined here.** Map
  `forest`→`navy`, `forestbg`→`sky`, `forestmid`→`skymid`, `forestlight`→`navylight`
- `\forestheader` in a deck — this course's beamer macro is `\navyheader`
- `\usepackage{apstats-boxes}` in a key file — keys use `apstats-key` only (it includes boxes)
- `fixedskillbox` anywhere (see rule 4)
- `tierbox` — does not exist, and **EFFL has no tiered instruction**; drop the concept, don't
  reimplement it with a `tcolorbox`
- `\begin{practicebox}{Title}` — `practicebox` takes **no argument** (its title is fixed as
  "Guided Practice"); a titled box is `notesbox{Title}`
- `\begin{work}{2cm}` — `work` takes **no argument**, and its body is math (an amsmath `aligned`)

### 7. Only use colors defined in `shared/apstats-colors.sty`

Before using any color name, verify it is defined there. Never invent color names. Defined:

```
navy  navylight  sky  skymid  goldacc  goldbg  hookbg
greenbg  greenacc  redbg  redacc  charcoal  slate  linegray  keyred
goldbox  greenbox  redbox
```

Any other name (e.g. `forest`, `bluebox`, `purplebox`, `gold`) is **undefined** and will cause a
compile error. When in doubt, `grep` the `.sty` file first.

## Multi-lesson dispatch — REQUIRED when generating more than one lesson

**When the request covers two or more lessons, do NOT author them sequentially.** Spawn one
subagent per lesson in a single message using the `Agent` tool, each briefed with the lesson
number, CED topic content, and a pointer to this skill. The coordinator gathers CED content first
(Steps 0–1, once), then fans out.

```
# Coordinator does once:
- read one model EFFL lesson, extract CED topics for L7.4 and L7.5

# Coordinator scaffolds ALL lesson directories before spawning subagents:
python3 .claude/skills/lesson-planning/scripts/new_lesson.py --project . --unit 07 --lesson 04 \
  --title "..." --unit-title "..."
python3 .claude/skills/lesson-planning/scripts/new_lesson.py --project . --unit 07 --lesson 05 \
  --title "..." --unit-title "..."

# Then in ONE message, spawn two agents in parallel:
Agent(lesson=7.4, ced_content=..., model_lesson_path=...)
Agent(lesson=7.5, ced_content=..., model_lesson_path=...)

# Each subagent uses the Write tool only to fill in content (no Bash needed).
# Coordinator then runs: make -C unit07/lesson04 all && make -C unit07/lesson05 all
# and verifies the page counts before opening the PR.
```

**Why the coordinator must scaffold:** subagents run in a fresh permission context and may not
have auto-approved Bash access. The coordinator always does. Scaffolding first means subagents
only need the Write tool.

Each subagent receives: (a) the extracted CED content for its single lesson, (b) the path of one
model EFFL lesson to mirror, (c) the hard constraints above, and (d) instructions to use the Write
tool only. The coordinator collects results, builds, verifies page counts, and opens one PR.

## Workflow

Follow these steps in order. Read the referenced files as you reach each step rather than all
upfront.

### Step 0 — Sync with upstream, then detect project context

**Sync the worktree first — before reading or writing anything.** This skill runs in a git
worktree; start *every* invocation by pulling the latest upstream changes so you author against
the current shared styles and lesson map:

```bash
git fetch origin
DEFAULT=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's@^origin/@@')
git merge --no-edit "origin/${DEFAULT:-main}"
```

If the working tree is dirty or the merge reports conflicts, **stop and surface it to the user** —
never force, reset, or discard changes to make the sync succeed. Then:

1. **Confirm the prefix.** `ls shared/*-colors.sty` → it is `apstats`.
2. **Course macros live in `shared/`.** `\CourseName`, `\SchoolYear`, and `\MeetingLength` are
   defined in `apstats-article.sty`, so a lesson plan sets only `\UnitNumberName` and
   `\LessonNumberName`. The title block prints `\CourseName` plus the unit/lesson line and
   **nothing else**.
3. **Find the insertion point.** List `unit*/lesson*` to find the target lesson and whether it
   already exists — and whether it is **legacy** (has `notes/`, `activity/`, `exit_ticket/`) or
   **EFFL** (has `experience/`).
4. **Open a model lesson.** Mirror a built EFFL lesson's preamble, box usage, and tone. The live
   project overrides the reference docs. If no EFFL lesson exists yet in this course, mirror the
   skeletons in `assets/skeletons/` and `~/Mathematics/algebra_2/unit01/lesson02/experience` for
   shape only — **recolor and re-scope it** per "What is different about this course."

### Step 1 — Map the CED topic to the lesson

Locate the CED in `spec/`, extract the unit → topic → Learning Objective → Essential Knowledge
content for this lesson, plus the governing Big Idea and AP Skill. One CED **Topic** maps to one
lesson. **Confirm the topic mapping with the user before authoring.** Then decide, from the EK,
**what the groups must discover** — the activity is designed backward from that. See
`references/ap-workflow.md` → "EFFL: where CED content lands in the lesson."

### Step 2 — Scaffold the lesson directory

```bash
python3 .claude/skills/lesson-planning/scripts/new_lesson.py --project . --unit 02 --lesson 03 \
  --title "Representing a Categorical Variable with Graphs" \
  --unit-title "Exploring One-Variable Data"
```

`--components` defaults to `cover,warmup,experience,homework,slides`, so it can be omitted. The
script auto-detects the prefix, writes the one-line `Makefile`, the lesson plan, and each
component + `_key` skeleton. Pass `--prefab warmup` to create a drop-in directory instead (Step 4).

**Unit assessments scaffold automatically** when the run creates a *new* unit (`tests/`,
`test_keys/`, `sample_test/`, `sample_test_key/`). `--tests` (re)scaffolds them for an existing
unit (idempotent — it never clobbers authored tests); `--no-tests` skips them.

### Step 3 — Author the lesson plan and components

**Before writing any component, do a full `Read` on each scaffolded `main.tex` skeleton you are
about to replace.** Use the `Read` tool on the actual file — a `cat`/`bash` dump does **not**
register the file with the editor and the first write will fail ("file has not been read yet").
Read every skeleton you intend to author (each component and its `_key`) up front, then write them.

Author each file following `references/components.md`. Hold to these invariants:

- **Student components** preamble with `\documentclass[10pt]{article}` +
  `\usepackage{apstats-article}` + `\usepackage{apstats-boxes}`. The **Experience & Formalize**
  component uses `\documentclass[12pt]{article}` (Math Medic sizing); warm-up, homework, and cover
  stay `[10pt]`.
- **EFFL scope (the timebox rule).** The activity must fit the 20-minute block: **two scenarios,
  ~10–13 sub-questions, ~2 pages at 12pt**, worked from prior knowledge with every display
  pre-drawn. Extra examples belong to the debrief, the Application, or Check Your Understanding —
  not the activity.
- **The Experience & Formalize page budget (non-negotiable).** Activity **≤2pp** · QuickNotes
  **½pp** · Application **½–1pp** · Check Your Understanding **1–2pp**. A part that runs over gets
  cut, not carried.
- **Check Your Understanding is not scored.** The cover's score column prints **`\textbf{NA}`** for
  it rather than a `\blank{}`, the plan tells the teacher to spot-check the formative item instead
  of collecting for a grade, and the deck says "practice, not a quiz." **The homework is the graded
  practice** and carries a score blank.
- **Homework carries the AP reps.** AP-style multiple choice (five options, in context) plus at
  least one multi-part free-response item, one spiral item, and the preview of the next lesson.
- **The spoiler rule** (Hard constraint 5).
- **Open answer space, not write-lines, in Experience & Formalize.** The component preamble defines
  `\answerspace{H}{answer}`: the blank passes an empty second argument, the key passes the red
  answer, so the two files paginate identically by construction. Size H for 2–4 handwritten lines
  (1.4–2.8cm). Short inline `\blank{}`s are still fine for table cells and one-word fills.
- **Answer keys** are *separate files* that swap `-boxes` for `\usepackage{apstats-key}` and wrap
  every answer in `\ans{...}` (inline) or `\ansline{...}` (fills a write-line). Mirror the blank
  exactly, then fill the blanks. There is **no** answer-key toggle — never try to build one.
- **Teacher notes go in the lesson plan, not in a key** — one `teachernote` per component, in
  packet order: `[Warm-Up]`, `[Experience \& Formalize]`, `[Homework]`.
- **The work rule** (Hard constraint 1b): every worked solution in a `work` block authored
  byte-identically in blank and key. Never cram steps into one line as `$a=b \Rightarrow c=d$`.
- **`\boxguard` before every breakable box**, in the blank and the key both.
- **Namestrip: `\namedateperiod` on the cover only** — plus the unit tests, which are taken in a
  testing setting. No name row on warmup, experience, or homework; the packet is stapled behind
  its cover.
- **`\par` around `\termblanklong`/`\ansline` inside a `vocabbox`** (the vocabpar fix) — without it
  the intro sentence collides with the first term, and key answers drag onto the wrong line.
- Use the project's box vocabulary and fill-in helpers rather than reinventing layout; the full
  catalog is in `references/conventions.md`.
- **AP habits of mind:** every context is real and plausible, every answer is phrased **in
  context**, and conclusions acknowledge uncertainty. That is what the AP exam scores.

### Step 4 — Handle prefab components

When the user supplies a ready-made PDF for a component, just drop it in — no wrapper needed:

1. Place the PDF as `<comp>/main.pdf` (e.g. `warmup/main.pdf`).
2. If the key is also a prefab PDF, place it as `<comp>_key/main.pdf`.

`shared/lesson.mk` discovers the component by its `main.pdf` and feeds it straight to `pdfunite`,
skipping compilation. Use `--prefab <comp>` when scaffolding to create the empty drop-in directory.

### Step 5 — Build

```bash
make -C unit02/lesson03 all       # all five products — the usual command
make -C unit02/lesson03 plan      # the lesson plan            → lessonYY_plan.pdf
make -C unit02/lesson03 slides    # the deck, both forms       → lessonYY_slides.pdf + .pptx
make -C unit02/lesson03 student   # cover + blank components   → lessonYY_student.pdf
make -C unit02/lesson03 key       # the same packet, answered  → lessonYY_key.pdf
```

`make -C unit02 student|key` merges a unit; `make student|key` at the root merges the whole
curriculum. Unit tests build separately: `make -C unit02/tests all && make -C unit02/test_keys all`.
Output lands in `target/`. The build needs XeLaTeX, `latexmk`, `pdfunite`, `pdftoppm`, and
`python3`; if a compile fails, surface the `.log` and fix the offending `.tex` rather than editing
the build system.

**Pagination is owned by one layer.** After `pdfunite` merges the components, `shared/paginate.sh`
renumbers the packet lesson-wide, forces every component onto a recto, and lays the student and key
packets against each other so page N of one is page N of the other. `shared/unit.mk` re-runs the
same pass over the merged unit packet; it is idempotent. **Never add a wrapper `.tex`**, never put
slides in the student packet, and never insert a lesson plan into a packet.

Because slots are sized against the counterpart, `student` and `key` each *compile* every component
of both packets but emit only their own. **Use `make all` when you want both PDFs.**

### Step 6 — Compile QA before any PR

`make` stops at the first error, so scan every document first. Compile **out of tree** — an
in-place `xelatex` overwrites tracked `main.pdf` files in the source directories:

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
build and report.

| Name | The rule | How to apply |
| --- | --- | --- |
| **boxguard** | No box stranded as a ~1in sliver across a page break | `\boxguard` (or `\boxguard[n]`) on its own line before the `\begin{...}` — blank **and** key |
| **namestrip** | Name/date/period row on the cover (and unit tests) only | `python3 .claude/skills/lesson-planning/scripts/namestrip.py --project . --unit NN --lesson MM` (`--check` to preview) |
| **vocabpar** | `\par` around `\termblanklong`/`\ansline` in a `vocabbox` | Hand fix per lesson |
| **work rule** | A component is the same length blank and keyed | `work` blocks authored identically in both files; `steptable`/`\step` for printed solutions; `\writelines{n}` to match a wrapped `\ansline` |
| **teachernotes** | Teacher prose in the lesson plan, one titled note per component | `python3 .claude/skills/lesson-planning/scripts/movenotes.py unitNN/lessonMM` (`--check` to preview) |
| **deck** | Every lesson has a `slides/` Beamer deck | If `slides/main.tex` is absent, author one from `assets/skeletons/slides.tex` |
| **effl** | The lesson uses the EFFL component shape | See "Regenerating a legacy lesson" below |

Full spec for each: `references/conventions.md`.

**A lesson with no deck is incomplete.** The deck feeds two of the five work products, so a lesson
without `slides/main.tex` builds only three. **When you review or retrofit a lesson that has no
deck, author one** — it is part of the review, not a separate request.

### Regenerating a legacy lesson in EFFL shape

A legacy lesson has `notes/`, `activity/`, and `exit_ticket/` and no `experience/`. Regenerating it:

1. Scaffold `experience` and `experience_key` into the existing lesson dir
   (`--components experience --force` is not needed; scaffold into a fresh dir if unsure).
2. Fold the old **activity** into the Activity part, the **guided notes** into QuickNotes, the
   worked examples into the Application, and the **exit ticket** into the CYU formative-check item.
3. Delete `notes`, `notes_key`, `activity`, `activity_key`, `exit_ticket`, `exit_ticket_key`.
4. **Keep `homework`** — re-point it at AP-style MC/FRQ practice if it isn't already.
5. Rewrite the cover's packet table (Warm-Up · Experience & Formalize · Check Your Understanding
   with `NA` · Homework) and de-spoiler its learning targets.
6. Rewrite the lesson plan in EFFL section order and re-cut its teacher notes to three.
7. Author the deck if it has none.
8. **Delete the stale stamps** — `rm -rf .stamps/unitXX/lessonYY target/unitXX/lessonYY` — or
   `make` will skip recompiling a sibling whose PDF was cleaned and `pdfunite` will fail on a
   missing file.

**Always finish a retrofit or regeneration with the evidence**, per lesson: `make -C unitXX/lessonYY
all` exits 0, and every component's page count equals its `_key`'s (Hard constraint 1b). Compare the
compiled components under `target/unitXX/lessonYY/<comp>/main.pdf` — comparing `lessonYY_student.pdf`
against `lessonYY_key.pdf` proves nothing, since the pagination pass pads them to equal length no
matter what. Report any component that still differs and why.

**Scope note for this course.** Conversion has started: **1 of 78 lessons are EFFL**, the rest are
pre-EFFL. `unit01/lesson00` is the **reference implementation** — open it before converting anything
else. Across the remaining legacy lessons, 131 `_key` files still carry teacher notes,
`\namedateperiod` appears on every component rather than the cover alone, and **57 of 78 lessons
have no deck**. Convert lesson by lesson (or unit by unit) as you review, authoring the missing deck
as you go, and rebuild the unit packet each time — do not attempt the whole course in one pass.

## Reference files

- `references/conventions.md` — the style packages, every box environment, the fill-in and
  answer-key macros, `\answerspace`, color palette, and per-document-type preambles. Read before
  authoring.
- `references/components.md` — section-by-section spec and a skeleton for the lesson plan, each
  component + key, the legacy components, and the unit tests.
- `references/ap-workflow.md` — reading the AP CED, mapping Big Idea / Skill / LO / EK into the
  lesson, and where each piece lands in the EFFL flow.
- `references/standards-workflow.md` — the title + description + standards path, for anything the
  CED does not cover.
- `references/build.md` — the Makefile hierarchy, scaffolding, prefab PDFs, unit tests, build
  commands, and troubleshooting.

## Scripts

- `scripts/new_lesson.py` — scaffold a lesson directory (Step 2), plus a unit's tests on first
  creation. Emits namestrip-compliant components and a lesson plan pre-stubbed with one
  `teachernote` per component.
- `scripts/namestrip.py` — retrofit: remove the name row from every component but `cover`.
- `scripts/movenotes.py` — retrofit: lift each `_key`'s teacher note into the lesson plan, titled
  for its component.

Both retrofit scripts take `--check` to preview without writing.

## Guardrails

- **Sync first** (Step 0). Never force or discard to make the merge succeed.
- **Full `Read` each skeleton before writing it** (Step 3). A `bash`/`cat` dump does not register
  the file with the editor, so the write fails.
- Mirror a built lesson for tone and preamble; the live project overrides these docs.
- Structure comes from the AP CED; one Topic → one lesson; confirm the mapping before authoring.
- Keep blank and key documents in lockstep — the key is the blank with answers filled in, and it
  must come out the **same number of pages**. `\answerspace` and `work` blocks are what enforce it.
- **EFFL discipline:** the activity fits 20 minutes (two scenarios, ~10–13 sub-questions, ~2pp at
  12pt); vocabulary arrives in the debrief, never before it (the spoiler rule); no tiers, no
  guided-notes or exit-ticket components in new lessons.
- **Homework stays** — it is this course's graded AP practice. Do not copy Algebra 2's removal.
- **`\ans{}` in text mode only; `skillbox` not `fixedskillbox`; no `forest` colors** — grep-check
  every file before building.
- **One-page warm-up** — verify with `pdftoppm` after every build.
- **Compile QA out of tree** — `-output-directory` to a temp dir; an in-place `xelatex` clobbers
  tracked `main.pdf` files in the source directories.
- **Multi-lesson requests → parallel subagents.**
- Don't modify `shared/` or the Makefiles to make a lesson build; fix the lesson's `.tex`.
- **Retrofit and EFFL regeneration are first-class modes**, not authoring — apply only what was
  named, then prove it with build + page-count evidence.
