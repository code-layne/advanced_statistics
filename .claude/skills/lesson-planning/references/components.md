# Components

The spec for authoring each file after scaffolding. The scaffolder (`scripts/new_lesson.py`)
gives you a correctly-preambled skeleton with TODO markers; this file says what fills them.
**Always also open a real built lesson in the same course as the gold reference** — these specs
summarize the pattern, but the live project is authoritative. For macros and boxes see
`references/conventions.md`.

Contents: [Lesson plan](#lesson-plan) · [Cover](#cover) · [Warm-up](#warm-up) ·
[**Experience & Formalize**](#experience--formalize) · [Homework](#homework) · [Slides](#slides) ·
[Legacy components](#legacy-components--pre-effl) · [Answer-key discipline](#answer-key-discipline) ·
[Unit cover](#unit-cover) · [Unit tests](#unit-tests-summative-assessments) ·
[Sample test & key](#sample-test--key)

**A new lesson is `cover` + `warmup` + `experience` + `homework` + `slides`.** That is the EFFL
(experience first, formalize later) shape. `notes`, `activity`, and `exit_ticket` are pre-EFFL
components — the build still merges them so the ~78 legacy lessons keep working, but do not author
new ones. See [Legacy components](#legacy-components--pre-effl).

General rules:
- Student components preamble with `-article` + `-boxes`; keys with `-article` + `-key`.
  The `experience` component is **12pt**; everything else is 10pt.
- Keep the **key structurally identical** to its blank — it is the blank with answers filled in.
- Paraphrase any AP CED language into teaching wording; keep LO/EK codes as the audit trail.
- Use the project's boxes and fill-in macros rather than hand-rolling layout.
- **The spoiler rule:** nothing the student sees *before* the activity — the cover, the warm-up,
  the deck's learning-targets frame — may pre-name the vocabulary the debrief will attach. Write
  targets in plain language ("how spread out the values are", not "standard deviation"). The
  teacher-facing lesson plan keeps the formal AP vocabulary.

## Lesson plan

`main.tex` at the lesson root — teacher-facing, never handed to students. **The spoiler rule does
not apply here:** use the formal AP vocabulary freely. Canonical EFFL section order:

1. **Title block** — `\CourseName` + `\UnitNumberName \LessonNumberName`. **Course name only:**
   never put the school year (`\SchoolYear`) or the meeting length (`\MeetingLength`) in the
   title, so a plan does not go stale when either changes.
2. **Primary Objective / CED alignment / Lesson model** — a `tcolorbox` (sky/navy) carrying three
   lines: the objective in student-outcome terms; the CED audit trail (Topic · Big Idea · AP Skill
   · LO · EK); and the standing EFFL paragraph naming the model (groups work from prior knowledge,
   the teacher circulates with questions/cues/prompts *not answers*, the debrief attaches the
   vocabulary, the application and practice apply it — **no separate direct-instruction block**).
3. **Learning Targets & Key Understandings** — `skillbox{goldbox}` with a two-column `tabularx`:
   "I can…" targets on the left (traceable to the LO), the "why" paraphrased from the EKs on the
   right — **including the lesson's target misconception, stated explicitly**.
   Fill the `\item` text only; do not re-nest the `tabularx`/`itemize` pair.
4. **Vocabulary, Concepts & Theorems** — `skillbox{greenbox}`, a term/definition `tabularx` (use
   `\TallMath{...}` for tall formulas). These are what the *debrief* attaches — they must not
   appear on the cover or in the pre-debrief slides.
5. **Lesson at a Glance — `\MeetingLength`** — `skillbox{sky}` with a phase table
   (Phase | Min | Students | Teacher). The 55-minute split is
   **5 warm-up / 20 activity / 12 debrief / 6 application / 8 CYU / 4 close & assign**.
   Guard it with `\boxguard[30]`: a `tabularx` never splits.
6. **Warm-Up — Activate Prior Knowledge** — `skillbox{sky}`: the ~3 items and the **seed** each
   plants (which formal idea it sets up *without naming it*), plus what to debrief aloud.
7. **Experience & Formalize — The Activity** — `skillbox{sky}`: the 2-minute launch script, then
   `multicols{2}` — *what students do* (the arc of the two scenarios, naming the **crux question**)
   beside *what the teacher does* (circulate; give a **question, cue, or prompt, not an answer**;
   pick the group work to display in the debrief).
8. **Debrief — Formalize** — `skillbox{sky}`: the ordered "red-ink" moves, each attaching a formal
   name to something a group already wrote (`"student phrase" → formal term/notation`), plus the
   QuickNotes walkthrough and why this order.
9. **Application** — `skillbox{sky}`: the one problem worked together, the interpret-in-context
   step, and the three questions the teacher asks while the students hold the pen.
10. **Check Your Understanding — *not scored*** — `skillbox{redbox}`: the ~5 items, which one is
    the **formative check** and how to sort responses, the priority items and the early-finisher
    bank, and the instruction to spot-check rather than collect.
11. **Homework — AP-style practice (assigned, scored)** — `skillbox{goldbox}`: the assignment, how
    it is scored, when it is due.
12. **Watch For** — `skillbox{redbox}`: misconceptions keyed to item numbers; cold-call prompts.
13. **Close & Preview** — `skillbox{goldbox}`: assign the homework, name what changed today,
    preview the next lesson.
14. **Teacher notes** — set at the plan's body size: never open a note with `\scriptsize`,
    `\footnotesize`, or `\small`. One `\begin{teachernote}[Component]` per component, in packet
    order (`[Warm-Up]`, `[Experience \& Formalize]`, `[Homework]`), closing the plan. This is where
    *all* teacher-only prose lives; a `teachernote` never goes in a `_key`, because it is the one
    block with no counterpart in the blank and it makes the key run long.

**No `fixedskillbox`** — it does not exist in this course. Every box above is `skillbox`
(breakable) preceded by `\boxguard`. There are **no tier boxes** either: EFFL has no tiered
instruction block. Differentiation happens through the teacher's circulating prompts and the CYU
priority/early-finisher split.

*(Legacy plans use the old Hook / Explicit Instruction / Tiers / Exit Ticket order — items 5–12 of
the pre-EFFL spec. Leave them alone unless regenerating the lesson.)*

## Cover

`cover/main.tex` — student-facing front page of the packet. No key. Structure:
- Full-bleed navy banner (tikz) with `\LARGE` course name, unit, and `Lesson <id>  <title>`.
- `\namedateperiod` — **the only component that carries it** (Namestrip).
- `learningtargetbox` — an "I can…" list. **Spoiler rule:** plain language only. The AP Learning
  Objective belongs in the lesson plan; the cover must not pre-name the vocabulary the debrief
  will attach.
- `tocbox` — a `tabularx` listing each packet component (#, Component, Description, Score) with a
  Total row: Warm-Up, **Experience & Formalize**, **Check Your Understanding**, Homework. Keep the
  rows aligned with the components you actually scaffolded. **Check Your Understanding's score cell
  prints `\textbf{NA}`, never a `\blank{}`** — it is unscored practice. Homework carries a blank.
- `remindbox` ("Keep in Mind") — describes the **EFFL process** only and stops there: "you will
  experience first, formalize later… and only afterward will we name what you found." No content
  preview, no vocabulary.

## Warm-up

`warmup/` (+ `warmup_key/`) — short spiral review of *prerequisite* skills, sized to the
thumbnail shown on the lesson plan. Frequently a **prefab PDF**: if so, just drop it in as
`warmup/main.pdf` (and `warmup_key/main.pdf`) — `lesson.mk` merges it directly, and the lesson
plan can embed its thumbnail via `\includegraphics{warmup/main}`. If authored: 3–5 quick
problems with work space (`\vspace`), **no name row**, and the spiral review stays text-only
in the plan. Key mirrors with `\ans`; multi-step solutions go in `work` blocks.

## Experience & Formalize

**The component's name is "Experience & Formalize"** — that is what the cover, the packet header,
the deck, and the lesson plan call it. **The directory stays `experience/`**: it is a build
identifier listed in `shared/lesson.mk`'s `STUDENT_ORDER`/`KEYED_PAIRS`, and renaming it would mean
editing the build system. Directory `experience`, label *Experience & Formalize*.

`experience/` (+ `experience_key/`) — **the heart of the lesson**, one document, **four parts**, in
this order, on an explicit **page budget**:

| Part | Budget | What it is |
| --- | --- | --- |
| 1. Activity | **≤ 2 pages** | group work from prior knowledge only |
| 2. QuickNotes | **½ page** | the debrief fills it |
| 3. Application | **½–1 page** | one problem worked *together*, right after the notes |
| 4. Check Your Understanding | **1–2 pages** | in-class practice — **not scored** |

Hold the budget: it is the whole point of the four-part split. A part that runs over gets cut, not
carried. `\documentclass[12pt]{article}` (Math Medic sizing — the rest of the packet is 10pt),
`\pageheader{Unit X, Lesson Y.Z}{Experience \& Formalize: <Activity Title>}`, no name row.

The preamble defines `\answerspace{H}{answer}` (see `conventions.md`). The blank passes `{}`; the
key passes the answer, occupying the identical height — so the two files paginate identically by
construction. **No `\writelines` in Experience & Formalize** — answers go in open space. Short
inline `\blank{}`s remain for table cells and one-word fills.

1. **Activity** — a `headlinebox{sky}` framing one motivating **data context**, then **two
   `scenariobox`es** (~10–13 lettered sub-questions total, ~2 pages) that students work **from
   prior knowledge only**: complete a table, compute a value, circle/annotate a **pre-drawn**
   display, answer in the open space. Scenario 1 builds the toolkit on one data set; scenario 2
   varies it (the contrast case) and carries the lesson's **crux question** — the one that
   surfaces the target misconception. **The timebox rule:** the activity must fit the 20-minute
   block; extra examples belong to the debrief, the Application, or CYU. Never name the formal
   vocabulary here — students answer in their own words. Every display is pre-drawn; **never ask a
   student to sketch a graph from scratch** (dotplots, histograms, boxplots, and scatterplots are
   given, and students read or annotate them).
2. **QuickNotes** — one titled `tcolorbox` (sky/navy) the **debrief fills**: a small worked example
   or formula beside fill-in bullets covering the lesson's formal terms and notation. A summary of
   what the groups discovered, not a lecture; **half a page**. Blanks are `\blank{}` (key: `\ans{}`).
3. **Application** — a `notesbox{Application: <Title>}` with **one problem worked together**. This
   is the first place the just-named vocabulary is *used*: state the question in context, compute
   in a `work` block, **interpret the result in context**, then one "what if we change a number?"
   question that tests the concept rather than the procedure. Note `practicebox` takes **no
   argument** (its title is fixed as "Guided Practice"), so a titled Application uses `notesbox`.
4. **Check Your Understanding** — a `notesbox` with **~5 items in new contexts**, worked pairs →
   solo, spanning the lesson's CED topic: the core procedure, a *deliberate contrast pair* (same
   task, opposite condition — the pair that surfaces the target misconception), an interpret-in-
   context item, and an **AP-style item as the formative check** (the plan says how to sort
   responses). Use `\answerspace` for explain items.

   **It carries no point value.** It is in-class practice, so the cover's score column prints
   **`\textbf{NA}`** for it instead of a `\blank{}`, the plan tells the teacher to spot-check
   rather than collect for a grade, and the deck says "practice, not a quiz." The **graded**
   practice in this course is the homework. Budget 1–2pp; 2pp is a **ceiling**.

Key mirrors exactly: same `\answerspace` macro, answers in its second argument, `\ans{}` in the
blanks, `work` blocks carried over byte-identically, MC option tagged
`\textcolor{keyred}{\textbf{$\leftarrow$ correct}}`. `\boxguard` counts here are 12pt-relative:
use ~14–16, not the 24–30 used in 10pt components.

## Legacy components — pre-EFFL

`notes/`, `activity/`, and `exit_ticket/` (with their `_key`s) predate the 2026-08 EFFL redesign.
`shared/lesson.mk` still merges them, so all ~78 legacy lessons keep building untouched, and the
scaffolder still accepts them by name (`--components ...,notes,activity,exit_ticket`) so a legacy
lesson can be patched. **Do not author them into a new lesson.**

**Regenerating** a legacy lesson in EFFL shape means: create `experience/` + `experience_key/`;
fold the activity into the Activity part, the guided notes into QuickNotes, the worked examples
into the Application, and the exit ticket into the CYU formative-check item; delete `notes`,
`activity`, `exit_ticket` and their keys; rewrite the cover's packet table and the lesson plan;
keep `homework`. Their specs are below for reference while converting.

**Build gotcha when deleting a component:** a stale stamp under `.stamps/unitXX/lessonYY/` makes
`make` skip recompiling a *sibling* whose PDF was cleaned, and `pdfunite` then fails on a missing
file. Remove `.stamps/<unit>/<lesson>` alongside `target/<unit>/<lesson>`.

## Guided notes

`notes/` (+ `notes_key/`) — the student's fill-in notes. Structure:
- `\pageheader{Unit X, Lesson Y.Z}{Guided Notes}` (no name row — Namestrip).
- `objectivebox` — "By the end of this lesson, I will be able to…" with `\writeline`s for
  students to fill (the key uses `\ansline{...}`, one per Learning Objective).
- `vocabbox` — `\termblanklong{Term}` per key term (key replaces each with `\ans{definition}`).
  Wrap these in `\par` on both sides — the vocabpar fix; see `conventions.md`.
- `hookbox` — the same hook as the plan, with write-lines for student responses.
- Direct-instruction sections in `notesbox{Title}` with blanks (`\blank`, `\writeline`) at the
  points where students record steps/definitions/results.
- Optional `practicebox` ("Guided Practice") with 1–2 worked-with-class problems.

## Activity

`activity/` (+ `activity_key/`) — differentiated group practice.
- `\pageheader{Unit X, Lesson Y.Z}{Group Activity}` (no name row — Namestrip).
- Three `tcolorbox`es titled **Tier R — Remediate**, **Tier A — Approaching Proficiency**,
  **Tier E — Extension** (`colframe=black!40`), each with problems and generous `\vspace` work
  room. Tiers escalate in difficulty and align to the same skills.
- Key mirrors exactly, filling answers with `\ans{...}` and marking correct MC options with
  `\textcolor{keyred}{\textbf{$\leftarrow$ correct}}`, plus brief worked steps.

## Exit ticket

`exit_ticket/` (+ `exit_ticket_key/`) — a short independent check (2–3 items), no notes.
`\pageheader{...}{Exit Ticket}` (no name row); a tight `enumerate` with a little work
space. Key fills with `\ans`. Graded for completion in the example courses ("mistakes happen,
blanks don't").

## Homework

`homework/` (+ `homework_key/`) — **retained in this course** (unlike Algebra 2, which dropped it).
Check Your Understanding is unscored in-class practice; homework is the **graded** practice, and it
is where AP-style reps live.

`\pageheader{...}{Homework}` (no name row); AP-style **multiple-choice** items (five options, in
context) plus at least one **multi-part free-response** item, one spiral item reaching back to an
earlier topic, an optional `extensionbox` ("Extension — optional"), and a short `spiralbox` preview
of the next lesson. Every answer is phrased in context — that is what the AP exam scores.

Key fills with `\ans`, carries every `work` block over unchanged, tags the correct MC option, and
shows worked steps for the harder items. Scoring guidance goes in the lesson plan's
`\begin{teachernote}[Homework]`, **not** in the key.

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
