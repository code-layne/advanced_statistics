# Components

The spec for authoring each file after scaffolding. The scaffolder (`scripts/new_lesson.py`)
gives you a correctly-preambled skeleton with TODO markers; this file says what fills them.
**Always also open a real built lesson in the same course as the gold reference** — these specs
summarize the pattern, but the live project is authoritative. For macros and boxes see
`references/conventions.md`.

Contents: [Lesson plan](#lesson-plan) · [Cover](#cover) · [Warm-up](#warm-up) ·
[**Guided notes & practice**](#guided-notes--practice) · [**Group activity**](#group-activity) ·
[AP practice](#ap-practice) · [Homework](#homework) · [Slides](#slides) ·
[Legacy components](#legacy-components) · [Answer-key discipline](#answer-key-discipline) ·
[Unit cover](#unit-cover) · [Unit tests](#unit-tests-summative-assessments) ·
[Sample test & key](#sample-test--key)

**A new lesson is `cover` + `warmup` + `notes` + `activity` + `ap_practice` + `homework` +
`slides`.** That is the gradual-release shape: the teacher delivers the vocabulary directly in the
notes (**I do**), works one problem with the class (**we do**), releases three for students to
work alone (**you do**), then one group activity for the whole class applies it to a new context
and a whole-class debrief closes the loop. `experience/` and `exit_ticket/` are legacy components
— the build still merges them so older lessons keep working, but do not author new ones. See
[Legacy components](#legacy-components).

**The packet order is fixed by `shared/lesson.mk`'s `STUDENT_ORDER`:**
`cover → warmup → notes → ap_practice → homework`. Never rename a component directory.

General rules:
- Student components preamble with `-article` + `-boxes`; keys with `-article` + `-key`.
  **Every student component is 12pt**; only the teacher-facing lesson plan is 10pt.
- Keep the **key structurally identical** to its blank — it is the blank with answers filled in,
  and it must come out the **same number of pages**.
- Paraphrase any AP CED language into teaching wording; keep LO/EK codes as the audit trail.
- Use the project's boxes and fill-in macros rather than hand-rolling layout.
- **The notes teach, the guided practice rehearses, the homework transfers.** Use a different
  data context in each of the three. Recall is not the skill being built.
- **There is no exit ticket and no independent practice set** — the homework is the individual
  practice, started in class, and the teacher's formative read happens while circulating during
  Guided Practice and again during that supervised start. **There is no tiered instruction** and
  **no group activity** — one document, one version, for the whole class.

## Lesson plan

`main.tex` at the lesson root — teacher-facing, never handed to students. Use the formal AP
vocabulary freely. Canonical section order:

1. **Title block** — `\CourseName` + `\UnitNumberName \LessonNumberName`. **Course name only:**
   never put the school year (`\SchoolYear`) or the meeting length (`\MeetingLength`) in the
   title, so a plan does not go stale when either changes.
2. **Primary Objective / CED alignment / Lesson model** — a `tcolorbox` (sky/navy) carrying three
   lines: the objective in student-outcome terms; the CED audit trail (Topic · Big Idea · AP Skill
   · LO · EK); and the standing gradual-release paragraph naming the model (**I do, we do, you
   do** — the notes deliver the vocabulary directly, the guided practice is worked together with
   students holding the pen, the independent practice and the group activity are where students
   carry it alone and then with peers, and the debrief closes the loop as a whole class).
3. **Learning Targets & Key Understandings** — `skillbox{goldbox}` with a two-column `tabularx`:
   "I can…" targets on the left (traceable to the LO), the "why" paraphrased from the EKs on the
   right — **including the lesson's target misconception, stated explicitly**.
   Fill the `\item` text only; do not re-nest the `tabularx`/`itemize` pair.
4. **Vocabulary, Concepts & Theorems — taught directly in the guided notes** —
   `skillbox{greenbox}`, two `\begin{minipage}[t]{0.48\linewidth}` columns of `itemize` separated
   by `\hfill` (use `\TallMath{...}` for tall formulas).
5. **Lesson at a Glance — `\MeetingLength`** — `skillbox{sky}` with a phase table
   (Phase | Min | Students | Teacher). The 55-minute split is
   **5 warm-up / 22 guided notes & practice / 16 group activity / 8 debrief / 4 close & assign**.
   Guard it with `\boxguard[30]`: a `tabularx` never splits.
6. **Warm-Up — Activate Prior Knowledge (5 min)** — `skillbox{sky}`: the ~3 items and the **seed**
   each plants (which part of the notes it sets up), what to debrief aloud, and what to leave on
   the board for the notes to point back at.
7. **Guided Notes & Practice — I do, we do, you do (22 min)** — `skillbox{sky}` in `multicols{2}`:
   the **I do** pacing and which section is must-land; the **we do** questions the teacher asks
   while students hold the pen and which part is the point of the box; the **you do** block naming
   the **formative check** item and the reteach trigger.
8. **Group Activity (16 min)** — `skillbox{sky}`: "**One activity for the whole class — there is
   no tiered version**", the 1-minute launch script and ground rule, then `multicols{2}` — *what
   students do* (what scenario 1 applies, what scenario 2 varies, and which item is the **crux**)
   beside *what the teacher does* (circulate and press for evidence; the probes; which student
   work to collect for the debrief, including one *almost*-right crux answer).
9. **Debrief — whole class (8 min)** — `skillbox{sky}`: the ordered report-out moves, opening on
   the *almost*-right crux answer, then the Debrief-box walkthrough and what to cut if time is
   short (item 1 is the one that cannot be cut).
10. **AP Practice — assigned, not scored** — `skillbox{goldbox}`: what each item targets, the
    spiral item, the part worth reading closely, and when to go over it. The cover reads **NA**.
11. **Homework — scored, due the first class after two study halls** — `skillbox{goldbox}`: the assignment, the scoring
    breakdown, the item that predicts next-lesson performance, and the **DeltaMath override**.
12. **Watch For** — `skillbox{redbox}`: misconceptions keyed to item numbers; cold-call prompts.
13. **Close & Assign (4 min)** — `skillbox{goldbox}`: hand the homework launch first, then close
    on what changed rather than on the assignment; preview the next lesson.
14. **Teacher notes** — set at the plan's body size: never open a note with `\scriptsize`,
    `\footnotesize`, or `\small`. One `\begin{teachernote}[Component]` per component, in packet
    order (`[Warm-Up]`, `[Guided Notes \& Practice]`, `[Group Activity]`, `[AP Practice]`,
    `[Homework]`), closing the plan. This is where *all* teacher-only prose lives; a `teachernote`
    never goes in a `_key`, because it is the one block with no counterpart in the blank and it
    makes the key run long.

**No `fixedskillbox`** — it does not exist in this course. Every box above is `skillbox`
(breakable) preceded by `\boxguard`. There are **no tier boxes** either. Differentiation happens
through the teacher's circulating prompts and the reteach trigger on the formative check.

*(Legacy plans use the old Hook / Explicit Instruction / Tiers / Exit Ticket order, or the EFFL
Activity / Debrief / Application / CYU order. Leave them alone unless regenerating the lesson.)*

## Cover

`cover/main.tex` — student-facing front page of the packet. No key. Structure:
- Full-bleed navy banner (tikz) with `\LARGE` course name, unit, and `Lesson <id>  <title>`.
- `\namedateperiod` — **the only component that carries it** (Namestrip).
- `learningtargetbox` — an "I can…" list. **Name the formal vocabulary** and bold it; the notes
  teach it today. The AP Learning Objective code still belongs in the lesson plan, not here.
- `tocbox` — a `tabularx` listing each packet component (#, Component, Description, Score) with a
  Total row: Warm-Up, Guided Notes & Practice, **AP Practice**, Homework — four rows; there is
  no group activity. Keep the rows aligned with the components you actually scaffolded.
  **AP Practice's score cell prints `\textbf{NA}`, never a `\blank{}`** — it is assigned but
  unscored. Homework carries a blank (the teacher strikes it through when DeltaMath is
  assigned instead).
- `remindbox` ("Keep in Mind") — **the notes that matter for this lesson**, in the student's
  language: the hook the notes open on, and the habit the lesson insists on ("when a single
  number and a picture disagree, believe the picture"). **Do not narrate the gradual-release
  structure here** — no "today runs in three moves, I show you, then we do one together." The
  students live the structure; the cover is for what they need to carry into the work. No
  answer previews.

## Warm-up

`warmup/` (+ `warmup_key/`) — short spiral review of *prerequisite* skills, sized to the
thumbnail shown on the lesson plan. Frequently a **prefab PDF**: if so, just drop it in as
`warmup/main.pdf` (and `warmup_key/main.pdf`) — `lesson.mk` merges it directly, and the lesson
plan can embed its thumbnail via `\includegraphics{warmup/main}`. If authored: 3–5 quick
problems with work space (`\vspace`), **no name row**, and the spiral review stays text-only
in the plan. Key mirrors with `\ans`; multi-step solutions go in `work` blocks.

## Guided notes & practice

`notes/` (+ `notes_key/`) — **the direct-instruction centrepiece, 34 minutes**, in two moves.
`\pageheader{Unit X, Lesson Y.Z}{Guided Notes \& Practice}` (no name row — Namestrip).
Target **3–4 pages** at 12pt.

**I do (~20 min)** — **exactly two** numbered notes sections. Each is long, carrying two moves:
the second is introduced by a bold run-in heading, `\textbf{\textcolor{navy}{Its Title.}}`, not by
a second box. **The crux lives in the second half of section 2.**
- `objectivebox` — three printed "By the end of these notes I will be able to…" targets, naming
  the formal terms. Print them; do not make students write them (a `\writeline` here is a
  page-drift risk for no pedagogical gain).
- `vocabbox` — one `\termblank{Term}` per key term (3–5 of them), each bracketed by `\par` (the
  vocabpar fix). The box says **"Fill in each term as we name it in the notes below"** — it is
  filled during instruction, never front-loaded. The key uses `\termans{Term}{line 1}{line 2}`,
  **not** `\termblanklong` plus an `\ansline` (that runs a line long every time).
- Three to four numbered `notesbox{N. Title}` sections. Each carries a short piece of exposition
  in a real context, a **pre-drawn** table or display, and `\blank{W}` fills at the points where
  students record the definition or the conclusion. Put the lesson's **target misconception** in a
  `\fcolorbox{redacc}{redbg}{\parbox{...}}` callout where it is broken, with the probe that
  breaks it. Any computation goes in a `work` block, authored byte-identically in the key.

**We do (~6 min)**
- One `practicebox` — **takes no argument**, its title is fixed as "Guided Practice". Open with
  "**TODO Title — we work this one together**". Three lettered parts: the setup/identification
  move, the computation or interpretation, and **the part that is the point of the box** — the one
  that tests the misconception on new ground. Students hold the pen; the questions the teacher
  asks belong in the plan, not on the page.

**The notes end at Guided Practice.** There is no `notesbox{Independent Practice --- You Try}`,
no *Putting It Together* transfer set, and no `reflectionbox`. The debrief is spoken and lives in
the plan; the individual practice is `homework/`, started in class in the last eight minutes.

**Page lockstep:** every `\blank{W}` becomes an `\ans{...}` in the key and every `\writelines{n}`
becomes exactly *n* `\ansline{}` calls. **Size each `\blank{}` close to its answer** — a 4.4cm
blank replaced by a 2cm answer rewraps the paragraph and silently costs a page.

## Group activity — LEGACY ONLY, never author one

**This course has no group activity component.** The section below documents `activity/` so that
lessons authored before the redesign can still be read and patched. **Do not scaffold or author
one into a new lesson** — the guided notes absorbed it.

`activity/` (+ `activity_key/`) — **16 minutes in groups of 3–4, then an 8-minute whole-class
debrief.** `\pageheader{Unit X, Lesson Y.Z}{Group Activity: TODO Title}` (no name row).
Target **≤2 pages**.

**One activity for the entire class.** There are no tiers, no differentiated versions, and no
`tierbox`. Differentiation happens in how the teacher circulates — shorter, more concrete probes
at tables that are stuck; "now find me another case that behaves the same way" at tables that are
not. That guidance lives in the plan.

- `headlinebox{sky}` — the launch: one motivating data context in 2–3 sentences, ending with the
  **ground rule** (what a group must be able to show before anyone writes an answer down).
- `scenariobox[1. Title]{navy}` — the clean case, so every group has something correct on the page
  before it hits the crux. A pre-drawn table, then 3–4 lettered sub-questions.
- `scenariobox[2. Title]{navy}` — the contrast case. **One of its items is the crux**: the single
  question that surfaces the lesson's target misconception, and the one the debrief opens on.
- `reflectionbox` — **the Debrief**, three short synthesis prompts filled in together as a whole
  class after the groups report out. Item 1 is the sentence you want on every desk.

Seven to nine sub-questions total. Every display is **given**; never ask a student to sketch one.
Prose answers use `\answerspace{H}{}` so the blank and the key paginate identically by
construction (1.0cm ≈ 2 handwritten lines, 1.5cm ≈ 3, 2.0cm ≈ 4).

## AP practice

`ap_practice/` (+ `ap_practice_key/`) — **assigned but NOT scored.** The cover's score column reads
`\textbf{NA}`. `\pageheader{...}{AP Practice}` (no name row).

Open with a `remindbox` stating plainly that the page is not required and not scored and that the
graded homework is the last section of the packet — authored **byte-identically** in the blank and
the key. Then shape it like the exam: a `headlinebox{goldbg}` "Section I — Multiple Choice" with
four items (five options each, in context), and a `headlinebox{goldbg}` "Section II — Free
Response" with one multi-part set whose last part is the **spiral** reaching back to an earlier
topic. Reuse the activity's data context on purpose — the context is already loaded, so the
thinking stays on the distinctions.

Page lockstep rests on `\writelines{n}` in the blank matching exactly *n* terse `\ansline{}` calls
in the key. The next-lesson preview does **not** live here; it closes the packet, in `homework/`.

## Homework

`homework/` (+ `homework_key/`) — **the lesson's GRADED practice and the last component in the
packet**, generated for every lesson. `\pageheader{...}{Homework}` (no name row).

Open with a `remindbox` — "This is your graded homework. It is scored and due the first class after two study halls." —
authored byte-identically in both files. Then 5–7 items in a **fresh context** the lesson has not
used, grouped into two or three titled `notesbox`es (Part A / Part B / Part C). Include at least
one AP-style multiple-choice item with a required one-sentence justification. Close the packet
with a `spiralbox` previewing the next lesson.

Prose answers use `\answerspace{H}{}`. Note that `[resume]` on an `enumerate` does **not** carry
across separate `tcolorbox`es — items restart at 1 in each part, so reference them as A1/B2/C1 in
the plan rather than as a single running sequence.

Scoring guidance, the item that predicts next-lesson performance, and the **DeltaMath override**
("when DeltaMath carries this topic, assign it instead, strike the score cell on the cover, and
leave this page as optional practice — do not assign both") all go in the lesson plan's
`\begin{teachernote}[Homework]`, **not** in the key.

## Legacy components

Two older shapes are still in the tree and still build:

- **EFFL** (`experience/` + `experience_key/`, `unit01/lesson02`–`lesson07`) — the 2026-08
  experience-first experiment: a 12pt document holding Activity + QuickNotes + Application +
  Check Your Understanding, with no separate notes block and a "spoiler rule" that withheld
  vocabulary until the debrief.
- **Pre-EFFL** (`notes/` + `activity/` + `exit_ticket/`, units 02–09) — guided notes with a
  `hookbox`, a **tiered** three-box activity (Tier R / Tier A / Tier E), and a short exit ticket.

`shared/lesson.mk` still merges all of these, and the scaffolder still accepts `experience` and
`exit_ticket` by name so an older lesson can be patched. **Do not author them into a new lesson.**

**Regenerating an EFFL lesson** means: scaffold `notes` (and its key); fold the QuickNotes
bullets into the **two** notes sections' fills and the Application into the `practicebox`; fold
Check Your Understanding and the old Activity into the **homework**, re-voiced to *use* the
vocabulary rather than discover it; delete `experience` and `experience_key`; split the old
homework into an unscored `ap_practice` plus a **new scored homework** in a fresh context;
rewrite the cover table, the plan, and the deck order. The debrief is spoken — do not add a
`reflectionbox`.

**Regenerating a pre-EFFL lesson** is the same, plus: delete `exit_ticket` and `exit_ticket_key`
(its item folds into the homework), and **flatten the three tier boxes into instruction for the
whole class**.

**Build gotcha when deleting a component:** a stale stamp under `.stamps/unitXX/lessonYY/` makes
`make` skip recompiling a *sibling* whose PDF was cleaned, and `pdfunite` then fails on a missing
file. Remove `.stamps/<unit>/<lesson>` alongside `target/<unit>/<lesson>`.

## Slides

`slides/` — **required** Beamer deck (it feeds two of the five work products) (`\documentclass[aspectratio=169,11pt]{beamer}` +
`\usepackage{<prefix>-beamer}`). No key. Title slide is hand-built (navy background canvas +
minipage), content slides use `\navyheader{Title}` and `\sectionlabel[color]{LABEL}`. Note
`\CourseName` is **not** defined in beamer — write the course name literally. Mirror the
existing `slides/main.tex` closely; the beamer theme is bespoke.

## Answer-key discipline

There is no key toggle — every key is a separate file under `<comp>_key/`:
- Copy the blank component **verbatim**, then swap `\usepackage{<prefix>-boxes}` for
  `\usepackage{<prefix>-key}`.
- Replace each blank/write-line with `\ans{answer}` (inline) or `\ansline{answer}` (fills a
  write-line). Title becomes "<DocTitle> — Answer Key".
- For multiple choice, keep all options and tag the correct one
  (`\textcolor{keyred}{\textbf{$\leftarrow$ correct}}`), then show the reasoning in a short
  `itemize`.
- **No `teachernote` in a key.** Teacher-only guidance goes in the lesson plan, one
  `\begin{teachernote}[Component]` per component (see the lesson-plan spec above).
- Carry over every `\boxguard` and every `\begin{work}` block **unchanged** — a `work` block is
  authored byte-identically in both files, so it cannot drift.
- Because the key matches the blank line-for-line, the two paginate identically — **verify** it:
  every component's page count must equal its key's.

## Unit cover

`unit_cover/main.tex` — **required for every unit**. A standalone full-page cover sheet that
appears at the front of the student and teacher unit packets. It is compiled by `make _unit_cover`
(run latexmk with `-outdir=target/…`; PDF lands in `target/compiled/UNIT/unit_cover.pdf`).
No PDF is committed to the source tree — it compiles fresh like a lesson component.

Structure (match `unit01/unit_cover/main.tex` and the other units exactly):
- Full-bleed navy banner (TikZ): course name, teacher name/year, unit number + title.
- Unit overview `tcolorbox` (sky/navy): 4–6 sentence summary of the unit arc.
- Lessons table in a `skillbox{goldbox}`: columns `#`, `\textbf{Title}`, `Focus` — one row per
  lesson, `\arraystretch=1.6`.
- Standards/LOs table in a `skillbox{greenbox}`: `\textbf{LO code}` + one-line description
  for every AP learning objective the unit covers.

## Unit tests (summative assessments)

Scaffolded automatically when a unit is first created (`new_lesson.py` also takes `--tests` to
(re)scaffold an existing unit, and `--no-tests` to skip). Four sibling dirs under `unitXX/`:

| Dir | Holds | Merged into a packet? |
| --- | --- | --- |
| `tests/practice_test/` | the study copy students keep | via `sample_test` — **yes** |
| `tests/actual_test/` | the real test, given in a testing setting | **never** |
| `test_keys/practice_test_key/` | its key | via `sample_test_key` — **yes** |
| `test_keys/actual_test_key/` | the real test's key | **never** |

`tests/Makefile` is `include ../../shared/tests.mk`; `test_keys/Makefile` is
`include ../../shared/test_keys.mk`. Each compiles every subdir holding a `main.tex`, and its
`drop` target publishes the **practice** test/key to `../sample_test/main.pdf` and
`../sample_test_key/main.pdf`, which `unit.mk` merges into the unit packets:

```bash
make -C unitXX/tests all && make -C unitXX/test_keys all
```

Shape it like the AP exam: **Section I — Multiple Choice** (five options, in context), **Section II
— Free Response** (2–3 multi-part FRQs, at least one ending in an interpret/justify-in-context
part). The test carries `\namedateperiod` — it and the packet cover are the only two documents that
do, because a test is taken in a testing setting.

**The practice test and its key must come out the same number of pages** — the unit pagination pass
pairs `sample_test` against `sample_test_key` exactly the way it pairs a component against its key.
Use `work` blocks authored byte-identically in both.

## Sample test & key

`sample_test/` and `sample_test_key/` — **required for every unit**, prefab drop-in dirs holding
only a `.gitkeep` until a PDF arrives. Two ways to fill them:

- **Generated** (preferred): author `tests/practice_test/` and `test_keys/practice_test_key/`, then
  `make -C unitXX/tests all && make -C unitXX/test_keys all` — the `drop` targets publish the
  compiled PDFs here. See [Unit tests](#unit-tests-summative-assessments).
- **Hand-dropped**: place a ready-made `main.pdf` in the directory; no `.tex` is authored.

Either way, `unit.mk`'s `_sample_test` / `_sample_test_key` rules copy them into
`target/compiled/` and merge them at the tail of the unit student and key packets.
