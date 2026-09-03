---
name: lesson-planning
description: >-
  Author complete, build-ready lessons for the AP Statistics LaTeX curriculum (a project with a
  shared/ style package — prefix apstats — and a Makefile hierarchy that compiles components with
  latexmk and merges them with pdfunite). Use this whenever the user wants to create, draft, or
  build a lesson, a lesson plan, a unit, or any lesson component — warm-up, guided notes & practice,
  AP practice, homework, cover sheet, unit test, or their answer keys. Lessons
  follow a traditional gradual-release model: warm-up, guided notes and practice (I do / we do / you
  do) that carries the entire release, a whole-class debrief, then close and assign. There is no
  group activity. Structure comes from the
  College Board AP Statistics CED in spec/ (files named ap-*): one CED Topic maps to one lesson.
  Trigger this even when the user just says "make lesson 2.3" or "I need a warm-up and key for
  tomorrow," and even if they don't say the words "skill" or "LaTeX." Also use it to RETROFIT an
  already-authored lesson to a named convention — boxguard, namestrip, vocabpar, the work rule,
  teachernotes, deck — or to REGENERATE a lesson in the current gradual-release shape, as in "apply
  boxguard namestrip retrofit to 1.1 and 1.3" or "regenerate unit 1 in the gradual release shape."
  See the Retrofit section.
---

# Lesson Planning — AP Statistics

This skill authors lessons for the **AP Statistics** course and produces print-ready PDFs through
the project's own build system. **It builds around the project's conventions — it does not invent
its own.**

**Every new lesson follows a traditional gradual-release model: I do → we do → you do.** The
teacher delivers the vocabulary and the core idea directly in guided notes, in **two longer
sections**; a guided practice problem is worked together with students holding the pen; a
whole-class debrief closes the loop; and **the period ends with students starting the homework in
class, alone** — the homework *is* the individual practice. The 55-minute period runs
**5 warm-up / 34 guided notes & practice / 8 debrief / 8 close & start the homework**.

**There is no independent practice set in the notes**, and no *Putting It Together* transfer set.
Both were folded out: the notes end at Guided Practice, and the last eight minutes of the period
buy the individual work back as a supervised homework start. Do not re-add either.

**There is no group activity component.** Do not scaffold, author, or restore `activity/` —
the notes absorbed it. `unit01/lesson01` is the reference for the current shape.

**There is no exit ticket.** The teacher's formative read comes twice — circulating during Guided
Practice, and again during the supervised homework start — and the lesson plan tells the teacher
what to do with each of three piles of what they see. **There is no tiered
instruction**: one document, one version, for the entire class. Differentiation happens in how
the teacher circulates, not on the page.

## Homework and AP Practice

Every lesson carries **two** back-of-packet components, and the distinction is load-bearing:

- **`ap_practice` — assigned but NOT scored.** AP-format reps: four multiple-choice items (five
  options, in context) plus one multi-part free-response set. The cover's score column prints
  **`\textbf{NA}`** for it. Students keep it and bring it to review.
- **`homework` — the lesson's GRADED practice**, and the last component in the packet.
  **Paper homework is the default for this course** and is **generated for every lesson**.
  DeltaMath is an *occasional* override the teacher may choose on a given day — never the
  default, and never assumed by the author. When it is used, it replaces the page, the cover's
  score cell is struck, and the page stays in the packet as extra practice. **Author the
  homework every time** — the teacher decides at assign time, not the author.

The homework is the lesson's individual practice: students start it in class in the last eight
minutes, alone and silent, while the teacher circulates for a second formative read, and finish
it at home.

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
  `cover`, `warmup`, `notes`, `ap_practice`, `homework`, and `slides`.
- An **answer key** for each keyed component, as a *separate* sibling directory:
  `warmup_key`, `notes_key`, `ap_practice_key`, `homework_key`.
  (`cover` and `slides` have no key.)

**The packet order is fixed by the build** (`shared/lesson.mk` `STUDENT_ORDER`):
`cover → warmup → notes → ap_practice → homework`. Never rename a component
directory — each name is a build identifier.

### The in-class centrepiece

- **`notes` — *Guided Notes & Practice*, 34 min + an 8 min spoken debrief.** The whole in-class
  document:
  - an **objective box** and a **vocabulary box** filled *as each term is named*;
  - **exactly two numbered notes sections** (the **I do**, ~20 min). Each is *long* — it carries
    what used to be two sections, with the second half introduced by a bold run-in heading,
    `\textbf{\textcolor{navy}{Its Title.}}`, rather than a second box. **The crux — the item that
    surfaces the lesson's target misconception — lives in the second half of section 2**;
  - a **`practicebox`** worked together (the **we do**, ~14 min; `practicebox` takes no argument —
    its title is fixed as "Guided Practice"). **The notes end here.**

  There is no Independent Practice box, no *Putting It Together*, and no `reflectionbox` — the
  debrief is spoken, and the individual practice is the homework.

  Target **3–4 pages at 12pt**. **Every student component is 12pt**, the warm-up included; the
  teacher-facing lesson plan stays at 10pt.

*Legacy shapes:* lessons authored before this redesign carry `activity/` (the 2026-08
gradual-release-with-group-work shape, `unit01/lesson00`), `experience/` (the EFFL experiment,
`unit01/lesson02`–`lesson07`), or `notes/ + activity/ + exit_ticket/` with tiered activity boxes
(units 02–09). The build accepts all of them and they keep working untouched. When asked to touch
one, **ask whether to regenerate it in the current shape** — see Retrofit.

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

### 1b. Page-for-page: a component is the same length blank and keyed

Every component must come out the **same number of pages** as its `_key`. The student and key
packets are paginated against each other, so a key that runs one page long costs the student
packet a blank page.

The pagination pass **pads the mismatch rather than reporting it** — it gives the component a slot
of `max(blank, key)` pages in both packets and fills the short one with a blank verso. The packets
stay aligned either way, which means **a violation is silent**. Check the component page counts;
don't wait for a build to complain.

Three mechanisms enforce it — use them while authoring, not as a cleanup pass:

- **`\answerspace{H}{}`** in `notes/` and `homework/` — the blank reserves exactly `H`, the key
  prints the answer in the identical height. Authored byte-identically in both files. Sizing at
  12pt: **1.2cm ≈ 2 handwritten lines, 1.8cm ≈ 3, 2.4cm ≈ 4**; a key answer runs roughly
  **2.0 rendered lines per centimetre** at `\small`, so keep it inside the height it is given.
- **`\termblank{Term}` / `\termans{Term}{def}`** — one vocabulary row each, a *fixed*
  `\termrowheight` tall, so a definition that wraps to a second line still costs exactly what the
  blank reserved. The vocabulary box cannot drift. Keep definitions to two lines.
- **`work` blocks** for every multi-step solution, authored **byte-identically in the blank and the
  key**. The blank reserves the block's exact height and prints nothing; the key prints it in
  `keyred`. They cannot drift.
- **Teacher notes in the lesson plan, never in a `_key`** — a note is the one block in a key with
  no counterpart in the blank.

Verify after building:
```bash
for c in warmup notes ap_practice homework; do
  b=$(pdfinfo target/unitXX/lessonYY/$c/main.pdf       | awk '/^Pages/{print $2}')
  k=$(pdfinfo target/unitXX/lessonYY/${c}_key/main.pdf | awk '/^Pages/{print $2}')
  [ "$b" = "$k" ] && echo "OK    $c $b" || echo "DRIFT $c blank=$b key=$k"
done
```

### 1c. Size every `\blank{}` close to the answer that replaces it

This is the quiet cause of most page drift. `notes/` uses inline `\blank{W}` fills; the key
replaces each with `\ans{answer}`. **If the blank is much wider than the answer, the key's
paragraph rewraps shorter and the two files fall out of lockstep** — with nothing in the log to
tell you. Write the answer first, then size the blank to it plus a little writing room. Same for
`\writelines{n}` ↔ *n* `\ansline{}`: keep each key line short enough not to wrap.

### 1d. `\boxguard` before every breakable box

Never let a box break leaving a ~1in sliver — a title plus a line or two — at a page edge. Put
`\boxguard` on its own line immediately before the `\begin{...}`, in the blank **and** the key:

```latex
\boxguard                 % 16 lines must remain, else the box starts a new page
\begin{notesbox}{2. Checking the conditions}

\boxguard[30]             % raise it when the box opens with an unbreakable TikZ figure or tabularx
```

Prefer it to a hard `\newpage` — it self-adjusts when content above it changes.

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

### 5. `\termblank` in a key needs `\termans`, not a second write-line

A key that mirrors `\termblank{Term}` with `\termblanklong{Term}` *plus* an `\ansline{}` runs a
line longer than the blank every single time. Define this in the key file instead — it reproduces
`\termblank`'s exact two-line geometry:

```latex
\newcommand{\termans}[3]{%
  \noindent\textbf{\textcolor{navy}{#1:}}\quad\ans{#2}\\[1pt]%
  \ansline{#3}\\[2pt]}
```

`\par` still brackets each `\termblank`/`\termans` inside a `vocabbox` (the vocabpar fix) —
without it the intro sentence collides with the first term.

### 6. Other known-bad patterns (do not use)

- `\ding{55}` — `pifont` not loaded; use `\textbf{$\times$}` instead
- bare `gold` color — use `goldacc` / `goldbg`
- `forest`, `forestbg`, `forestmid`, `forestlight` — **Algebra 2 colors, undefined here.** Map
  `forest`→`navy`, `forestbg`→`sky`, `forestmid`→`skymid`, `forestlight`→`navylight`
- `\forestheader` in a deck — this course's beamer macro is `\navyheader`
- `\usepackage{apstats-boxes}` in a key file — keys use `apstats-key` only (it includes boxes)
- `fixedskillbox` anywhere (see rule 4)
- `tierbox` — does not exist, and **there is no tiered instruction**; one set of notes for the
  whole class. Drop the concept, don't reimplement it with a `tcolorbox`
- `\begin{practicebox}{Title}` — `practicebox` takes **no argument** (its title is fixed as
  "Guided Practice"); a titled box is `notesbox{Title}`
- `\begin{work}{2cm}` — `work` takes **no argument**, and its body is math (an amsmath `aligned`)
- `[resume]` on an `enumerate` split across separate `tcolorbox`es — it does not carry, so items
  restart at 1. Either accept per-box numbering and reference items as A1/B2/C1, or keep the
  enumerate inside one box.

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
- read one model lesson, extract CED topics for L7.4 and L7.5

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
model lesson to mirror, (c) the hard constraints above, and (d) instructions to use the Write
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
3. **Find the insertion point.** List `unit*/lesson*` to find the target lesson, whether it
   already exists, and which shape it is in: **current** (`notes/` + `ap_practice/`, **no
   `activity/`**), **group-activity legacy** (`notes/` + `activity/`, no `exit_ticket/`),
   **EFFL** (`experience/`), or **pre-EFFL legacy** (`notes/` + `activity/` + `exit_ticket/`).
4. **Open the reference implementation.** `unit01/lesson01` is the model — mirror its preamble,
   box usage, pacing, and tone. The live project overrides the reference docs.

### Step 1 — Map the CED topic to the lesson

Locate the CED in `spec/`, extract the unit → topic → Learning Objective → Essential Knowledge
content for this lesson, plus the governing Big Idea and AP Skill. One CED **Topic** maps to one
lesson. **Confirm the topic mapping with the user before authoring.** Then decide, from the EK,
**what the two notes sections must teach and what the homework must make students carry** —
section 2's second half is designed backward from the target misconception, and the homework is
designed backward from what should survive the night. See `references/ap-workflow.md`.

### Step 2 — Scaffold the lesson directory

```bash
python3 .claude/skills/lesson-planning/scripts/new_lesson.py --project . --unit 02 --lesson 03 \
  --title "Representing a Categorical Variable with Graphs" \
  --unit-title "Exploring One-Variable Data"
```

`--components` should be passed explicitly as
`cover,warmup,notes,ap_practice,homework,slides` — the installed script still defaults to
including `activity`, and any `activity/` it scaffolds must be deleted. Otherwise it can be
omitted. The script auto-detects the prefix, writes the one-line `Makefile`, the lesson plan, and
each component + `_key` skeleton. Pass `--prefab warmup` to create a drop-in directory instead
(Step 4).

**Unit assessments scaffold automatically** when the run creates a *new* unit (`tests/`,
`test_keys/`, `sample_test/`, `sample_test_key/`). `--tests` (re)scaffolds them for an existing
unit (idempotent — it never clobbers authored tests); `--no-tests` skips them.

### Step 3 — Author the lesson plan and components

**Before writing any component, do a full `Read` on each scaffolded `main.tex` skeleton you are
about to replace.** Use the `Read` tool on the actual file — a `cat`/`bash` dump does **not**
register the file with the editor and the first write will fail ("file has not been read yet").
Read every skeleton you intend to author (each component and its `_key`) up front, then write them.

Author each file following `references/components.md`. Hold to these invariants:

- **Every student component** preambles with `\documentclass[12pt]{article}` +
  `\usepackage{apstats-article}` + `\usepackage{apstats-boxes}` — cover, warm-up, notes,
  AP practice, and homework alike. Only the teacher-facing lesson plan is 10pt.
- **The timebox rules.** Guided notes: **exactly two** long notes sections + one guided-practice
  problem — **3–4pp total at 12pt**, every display pre-drawn. The notes end at Guided Practice.
  A part that runs over gets cut, not carried; the period must still end with eight minutes for
  the homework start.
- **The notes teach and the homework carries it across.** Use a *different context* in the
  instruction than in Guided Practice, and a *third* in the homework. Recall is not the skill
  being built.
- **The crux lives in the second half of notes section 2** — the item that surfaces the lesson's
  target misconception. Name that misconception explicitly in the plan's Key Understandings cell
  and again in "Watch For."
- **The formative read happens twice** — while circulating during Guided Practice, and again
  during the supervised homework start — and the plan says what the teacher does with each of
  three possible piles of responses. There is no exit ticket and no independent practice set.
- **AP Practice carries `NA`** in the cover's score column; **homework carries a score blank** and
  the DeltaMath-override note. Both are authored for every lesson.
- **Answer keys** are *separate files* that swap `-boxes` for `\usepackage{apstats-key}` and wrap
  every answer in `\ans{...}` (inline), `\ansline{...}` (fills a write-line), `\termans{Term}{def}`
  (fills a `\termblank` — **two arguments**, defined in `apstats-key.sty`; never redefine it
  locally), or the second argument of `\answerspace{H}{}`. Mirror the blank exactly,
  then fill the blanks. There is **no** answer-key toggle — never try to build one.
- **Teacher notes go in the lesson plan, not in a key** — one `teachernote` per component, in
  packet order — **four of them**: `[Warm-Up]`, `[Guided Notes \& Practice]`, `[AP Practice]`,
  `[Homework]`.
- **The work rule** (Hard constraint 1b): every worked solution in a `work` block authored
  byte-identically in blank and key. Never cram steps into one line as `$a=b \Rightarrow c=d$`.
- **`\boxguard` before every breakable box**, in the blank and the key both.
- **Namestrip: `\namedateperiod` on the cover only** — plus the unit tests, which are taken in a
  testing setting. No name row on any other component; the packet is stapled behind its cover.
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
    && echo "OK: $f  $(pdfinfo "$o/main.pdf" | awk '/^Pages/{print $2}')pp" \
    || { echo "FAIL: $f"; grep -m3 "^!" "$o/scan.log"; }
done
```

The page counts printed here are also your Hard-constraint-1b check — compare each component
against its `_key` before running `make`. Collect ALL failures, fix them, re-scan to confirm zero,
then delete stale stamps (`find .stamps/unitXX -name '*.stamp' -delete`) and run `make`.

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
| **vocabpar** | `\par` around `\termblank`/`\termblanklong`/`\ansline` in a `vocabbox` | Hand fix per lesson; the key side uses `\termans` (Hard constraint 5) |
| **work rule** | A component is the same length blank and keyed | `work` blocks authored identically in both files; `\answerspace{H}{}` for prose answers; blank widths sized to their answers (Hard constraint 1c) |
| **teachernotes** | Teacher prose in the lesson plan, one titled note per component | `python3 .claude/skills/lesson-planning/scripts/movenotes.py unitNN/lessonMM` (`--check` to preview) |
| **deck** | Every lesson has a `slides/` Beamer deck | If `slides/main.tex` is absent, author one from `assets/skeletons/slides.tex` |
| **gradual release** | The lesson uses the current component shape (no `activity/`) | See "Regenerating a lesson" below |

Full spec for each: `references/conventions.md`.

**A lesson with no deck is incomplete.** The deck feeds two of the five work products, so a lesson
without `slides/main.tex` builds only three. **When you review or retrofit a lesson that has no
deck, author one** — it is part of the review, not a separate request.

### Regenerating a lesson in the current gradual-release shape

**From the group-activity shape** (has `notes/` + `activity/`, no `exit_ticket/`):

1. Fold the activity's crux scenario into the **second half of notes section 2**, re-voiced as
   direct instruction rather than group work. Its debrief becomes a *spoken* whole-class debrief
   in the plan — do not add a `reflectionbox` to the notes.
2. `git rm -r` the `activity` and `activity_key` directories.
3. Repace the plan to **5 / 34 / 8 / 8**, delete its Group Activity `skillbox`, and fold its
   teacher note into the Guided Notes one (four notes, not five).
4. Renumber the cover's packet table to four rows and re-voice its remind box: the third move is
   **starting the homework in class**, not a third practice set.
5. Re-title the deck's activity divider and launch frames as the supervised homework start.

**From the EFFL shape** (has `experience/`, no `exit_ticket/`):

1. Scaffold `notes`, `notes_key` into the existing lesson dir.
2. Fold the old **QuickNotes** into the **two** notes sections' fills, the old **Application**
   into the `practicebox`, and the old **Check Your Understanding** and **Activity** into the
   **homework** — re-voiced to *use* the vocabulary rather than discover it, and worked
   individually at home after a supervised start.
3. The debrief is **spoken** and lives in the plan; do not add a `reflectionbox` to the notes.
4. Delete `experience`, `experience_key`.
5. If the lesson has no `ap_practice/`, split the existing homework: AP-format items to
   `ap_practice/` (unscored), and author a **new scored homework** in a fresh context.
6. Rewrite the cover's packet table (Warm-Up · Guided Notes & Practice · AP Practice with `NA` ·
   Homework) and re-voice its learning targets with the formal vocabulary.
7. Rewrite the lesson plan in gradual-release order and re-cut its teacher notes to four.
8. Reorder the deck: targets → warm-up → I-do divider → two instruction frames → we-do →
   debrief → close & start the homework.

**From the pre-EFFL legacy shape** (has `exit_ticket/` and tiered activity boxes): the same, plus
**delete `exit_ticket` and `exit_ticket_key`** (fold its item into the homework) and **flatten the
tiered activity into instruction for the whole class**.

Either way: **delete the stale stamps** — `rm -rf .stamps/unitXX/lessonYY target/unitXX/lessonYY` —
or `make` will skip recompiling a sibling whose PDF was cleaned and `pdfunite` will fail on a
missing file.

**Always finish a retrofit or regeneration with the evidence**, per lesson: `make -C unitXX/lessonYY
all` exits 0, and every component's page count equals its `_key`'s (Hard constraint 1b). Compare the
compiled components under `target/unitXX/lessonYY/<comp>/main.pdf` — comparing `lessonYY_student.pdf`
against `lessonYY_key.pdf` proves nothing, since the pagination pass pads them to equal length no
matter what. Report any component that still differs and why.

**Scope note for this course.** Conversion has started:
**1 of 78 lessons is in the current no-activity shape** — `unit01/lesson01`, the **reference
implementation**; open it before converting anything else. **1 lesson is in the group-activity
shape** (`unit01/lesson00`). **6 lessons are in the EFFL shape** (`unit01/lesson02`–`lesson07`).
The remaining
**70 are pre-EFFL legacy**: they still carry `exit_ticket/` and tiered activity boxes, 96 `_key`
files still hold teacher notes, `\namedateperiod` appears on every component rather than the cover
alone, and **57 of 78 lessons have no deck**. Convert lesson by lesson (or unit by unit) as you
review, authoring the missing deck as you go, and rebuild the unit packet each time — do not
attempt the whole course in one pass.

## Reference files

- `references/conventions.md` — the style packages, every box environment, the fill-in and
  answer-key macros, `\answerspace`, color palette, and per-document-type preambles. Read before
  authoring.
- `references/components.md` — section-by-section spec and a skeleton for the lesson plan, each
  component + key, and the unit tests.
- `references/ap-workflow.md` — reading the AP CED, mapping Big Idea / Skill / LO / EK into the
  lesson, and where each piece lands in the gradual-release flow.
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
- Mirror `unit01/lesson00` for tone and preamble; the live project overrides these docs.
- Structure comes from the AP CED; one Topic → one lesson; confirm the mapping before authoring.
- Keep blank and key documents in lockstep — the key is the blank with answers filled in, and it
  must come out the **same number of pages**. `\answerspace`, `work` blocks, `\termans`, and
  answer-sized `\blank{}` widths are what enforce it.
- **Gradual-release discipline:** the notes carry instruction (**two** sections) and guided
  practice, and stop there; **no group activity**; no tiers; no exit ticket; no independent
  practice set and no transfer set. **The homework is the individual practice**, started in class
  in the last eight minutes, and that start is the second formative read.
- **Both back-of-packet components are authored every lesson** — `ap_practice` unscored,
  `homework` scored, with the DeltaMath-override note in the plan.
- **`\ans{}` in text mode only; `skillbox` not `fixedskillbox`; no `forest` colors** — grep-check
  every file before building.
- **One-page warm-up** — verify with `pdftoppm` after every build.
- **Compile QA out of tree** — `-output-directory` to a temp dir; an in-place `xelatex` clobbers
  tracked `main.pdf` files in the source directories.
- **Multi-lesson requests → parallel subagents.**
- Don't modify `shared/` or the Makefiles to make a lesson build; fix the lesson's `.tex`.
- **Retrofit and regeneration are first-class modes**, not authoring — apply only what was named,
  then prove it with build + page-count evidence.
