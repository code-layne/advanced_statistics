# Components

The spec for authoring each file after scaffolding. The scaffolder (`scripts/new_lesson.py`)
gives you a correctly-preambled skeleton with TODO markers; this file says what fills them.
**Always also open a real built lesson in the same course as the gold reference** — these specs
summarize the pattern, but the live project is authoritative. For macros and boxes see
`references/conventions.md`.

Contents: [Lesson plan](#lesson-plan) · [Cover](#cover) · [Warm-up](#warm-up) ·
[Guided notes](#guided-notes) · [Activity](#activity) · [Exit ticket](#exit-ticket) ·
[Homework](#homework) · [Slides](#slides) · [Answer-key discipline](#answer-key-discipline) ·
[Unit cover](#unit-cover) · [Sample test & key](#sample-test--key)

General rules:
- Student components preamble with `-article` + `-boxes`; keys with `-article` + `-key`.
- Keep the **key structurally identical** to its blank — it is the blank with answers filled in.
- Paraphrase any AP CED language into teaching wording; keep LO/EK codes as the audit trail.
- Use the project's boxes and fill-in macros rather than hand-rolling layout.

## Lesson plan

`main.tex` at the lesson root — teacher-facing, never handed to students. Canonical section
order (same skeleton for review and primary-content lessons; review lessons simply carry no
AP tags and list review topics):

1. **Title block** — `\CourseName` + `\UnitNumberName \LessonNumberName`. **Course name only:**
   never put the school year (`\SchoolYear`) or the meeting length (`\MeetingLength`) in the
   title, so a plan does not go stale when either changes.
2. **Primary Objective** — a `tcolorbox` (sky/navy). One or two sentences. For AP courses,
   end with the governing big idea, e.g. `(Big Idea: VAR)`.
3. **Priority Ideas & Skills** — `skillbox{goldbox}`, two `minipage`s. Left: the priority
   skills (for AP, label with the AP Skill category and sub-skill, e.g. "AP Skill 1 —
   Selecting Statistical Methods"). Right: "Key Understandings" paraphrased from the EKs.
4. **Vocabulary, Concepts & Theorems** — `skillbox{greenbox}`, a `tabularx` term/definition
   table (use `\TallMath{...}` for tall formulas).
5. **Activate Prior Knowledge & Spiral Review** — `skillbox{sky}` (**not** `fixedskillbox` — that environment does not exist); left lists the reviewed skills, right shows the warm-up thumbnail via `\includegraphics[page=1]{warmup/main}`.
6. **Hook** — `skillbox{sky}`: the entry question or scenario.
7. **Lesson** (and optional **Lesson (cont.)**) — `skillbox{sky}` with `\begin{multicols}{2}`;
   the worked instructional progression, bolding the questions you'll pose.
8. **Explicit Instruction: <technique>** — one `skillbox{sky}` per technique, two columns:
   numbered steps on the left, a worked example (often with a Desmos screenshot) on the right.
9. **Active Monitoring** — `skillbox{redbox}`: what to circulate and check; cold-call prompts.
10. **Group Work & Differentiation** — `skillbox{redbox}`: a `multicols{3}` with **Tier R —
    Remediate / Tier A — Approaching Proficiency / Tier E — Extension** bullet lists that
    mirror the activity tiers.
11. **Individual Work & Assessment** — `skillbox{redbox}`: exit-ticket items + an SOL/AP-style
    MC, with a note on collecting and using results.
12. **Reinforcement & Extension** — `skillbox{goldbox}`: homework overview, an extension, and a
    preview of the next lesson.
13. **Teacher notes** — set at the plan's body size: never open a note with `\scriptsize`,
    `\footnotesize`, or `\small`, so every note reads the same as the rest of the plan. One
    `\begin{teachernote}[Component]` per component, in packet order
    (Warm-Up, Guided Notes, Group Activity, Exit Ticket, Homework), closing the plan. This is
    where *all* teacher-only prose lives; a `teachernote` never goes in a `_key`, because it is
    the one block with no counterpart in the blank and it makes the key run long.

## Cover

`cover/main.tex` — student-facing front page of the packet. No key. Structure:
- Full-bleed navy banner (tikz) with `\LARGE` course name, unit, and `Lesson <id>  <title>`.
- `\namedateperiod` — **the only component that carries it** (Namestrip).
- `learningtargetbox` — an "I can…" list, **one target per Learning Objective**.
- `tocbox` — a `tabularx` listing each packet component (#, Component, Description, Score blank)
  with a Total row. Keep the rows aligned with the components you actually scaffolded.
- Optionally mirror the lesson plan's Priority Ideas & Vocabulary for student reference.

## Warm-up

`warmup/` (+ `warmup_key/`) — short spiral review of *prerequisite* skills, sized to the
thumbnail shown on the lesson plan. Frequently a **prefab PDF**: if so, just drop it in as
`warmup/main.pdf` (and `warmup_key/main.pdf`) — `lesson.mk` merges it directly, and the lesson
plan can embed its thumbnail via `\includegraphics{warmup/main}`. If authored: 3–5 quick
problems with work space (`\vspace`), **no name row**, and the spiral review stays text-only
in the plan. Key mirrors with `\ans`; multi-step solutions go in `work` blocks.

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

`homework/` (+ `homework_key/`) — independent practice + stretch.
`\pageheader{...}{Homework}` (no name row); a numbered practice set, an `extensionbox`
("Extension — optional"), and a short preview of the next lesson. Key fills with `\ans` and
shows worked steps for the harder items.

## Slides

`slides/` — optional Beamer deck (`\documentclass[aspectratio=169,11pt]{beamer}` +
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

## Sample test & key

`sample_test/` and `sample_test_key/` — **required for every unit**. Create each directory with
only a `.gitkeep` file. The teacher drops the final PDF directly into the directory; no `.tex`
source is authored here. The `unit.mk` `_sample_test` rule copies `sample_test/main.pdf` to
`target/compiled/` when present.
