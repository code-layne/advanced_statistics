# Conventions

Extracted from the `shared/<prefix>-*.sty` packages. The live project is always the source
of truth — if a course's styles diverge from this, follow the course. Replace `<prefix>`
with the detected prefix (`algebra2`, `apstats`, …) everywhere below.

## Style packages

| Package | Purpose | Required by |
| --- | --- | --- |
| `<prefix>-colors` | Color palette (loads `xcolor`) | everything |
| `<prefix>-article` | Article preamble: geometry, lists, fill-in helpers, page header, name rows | student components |
| `<prefix>-boxes` | All `tcolorbox` environments, plus `\boxguard`, `work`, `steptable`, `teachernote` | components + lesson plan |
| `<prefix>-key` | Answer macros (`\ans`, `\ansline`); flips `work` visible; requires `-boxes` | answer keys |
| `<prefix>-beamer` | Slide theme | `slides/` |

## Per-document-type preambles

**Every student component** (cover, warmup, notes, ap_practice, homework — and the legacy
activity/experience/exit_ticket) is **12pt**. Only the teacher-facing lesson plan stays at 10pt:
```latex
\documentclass[12pt]{article}
\usepackage{<prefix>-article}
\usepackage{<prefix>-boxes}
% cover and some components also: \usepackage{ltablex}\keepXColumns
```

**`activity/` and `homework/`** additionally define the open-answer-space macro in their
preamble, byte-identical in the blank and the key:
```latex
\newcommand{\answerspace}[2]{\par\nopagebreak\noindent\begin{minipage}[t][#1][t]{\linewidth}%
  \color{keyred}\bfseries #2\end{minipage}\par}
```
`\answerspace{1.5cm}{}` in the blank reserves exactly 1.5cm of open space glued to its prompt; the
key passes the answer as the second argument, occupying the identical height. **That is what keeps
the two files page-for-page without write-lines.** Sizing guide at 12pt: **1.2cm ≈ 2 handwritten
lines, 1.8cm ≈ 3, 2.4cm ≈ 4**; a key answer set in `\small` runs roughly **2.0 rendered lines per
centimetre**, so keep it inside the height you gave it (a key answer that overflows its minipage
does not warn — it just spills).

Two cautions that cost pages: **a key `\ans{}` narrower than the blank it replaces rewraps the
paragraph shorter and shifts a page break** — so size each `\blank{W}` close to its answer plus a
little writing room, rather than picking a round width. And **`\boxguard` counts are
baseline-relative**, so a value tuned in one document is not portable to another point size.

**Answer key** (the matching `_key` directory):
```latex
\documentclass[10pt]{article}
\usepackage{<prefix>-article}
\usepackage{<prefix>-key}     % pulls in -boxes; do NOT also load -boxes
```

**Lesson plan** (`main.tex` at the lesson root): loads `-boxes` (and usually `-colors`
implicitly through it) and defines the course/unit/lesson macros it needs. Note the two
observed styles — detect which the course uses:
- `apstats` defines `\CourseName`, `\SchoolYear`, `\MeetingLength` in its style package, so
  the lesson plan only sets `\UnitNumberName` and `\LessonNumberName`. The title block prints
  `\CourseName` alone — `\SchoolYear` and `\MeetingLength` stay out of it (see
  `components.md` → "Lesson plan").
- `algebra2` defines all of them inline in the lesson plan preamble and loads a richer set of
  packages directly (`pdfpages`, `graphicx` with `\graphicspath{{images/}}`, `tabularx`,
  `unicode-math`, `multicol`).

The `\TallMath` helper used for tall inline math is defined per-document where needed:
```latex
\newcommand{\TallMath}[1]{$\displaystyle #1\rule[-1.4em]{0pt}{3.2em}$}
```

## Fill-in helpers (from `-article`)

| Macro | Effect |
| --- | --- |
| `\blank{width}` | Underlined gap of the given width (e.g. `\blank{4.8cm}`) |
| `\writeline` | A full-width gray rule to write on |
| `\writelines{n}` | `n` stacked write-lines, breaks *between* them — exactly `n` line slots, no trailing blank line |
| `\termblank{Term}` | One vocabulary row: bold navy term + a rule running to the end of the line, then open space. A **fixed `\termrowheight` tall**. No second full-width line. |
| `\termblanklong{Term}` | Bold navy term on its own line + two write-lines (vocab style) |
| `\namedateperiod` | Name / Date / Period row — **cover only** (Namestrip) |
| `\namepartnerperiod` | Name / Partner / Period row — **not used**; superseded by Namestrip |
| `\pageheader{Unit X, Lesson Y.Z}{Document Type}` | Full-width navy banner header |
| `\answerspace{H}{answer}` | **Not from `-article`** — defined per-document in `activity/` and `homework/`; reserves H of open space in the blank, prints the answer in the key. See the preamble above. |
| `\termans{Term}{definition}` | **Key-side only, defined in `<prefix>-key.sty`** — the counterpart of `\termblank`, reusing its fixed `\termrowheight`, so a definition that wraps to a second line still costs exactly what the blank reserved. **Two arguments; never redefine it in a lesson file.** Never mirror a `\termblank` with `\termblanklong` plus an `\ansline`: that runs a line long every time. |

### Namestrip — the name row belongs on the cover, nowhere else

The packet is stapled behind its cover, and since unit packets are built from a
`unitXX_student.tex` wrapper the whole unit is one continuously-paginated document — so a
name/date/period row on every component costs vertical space at the top of each page for
something the student wrote once on page 1.

In this course the keys mostly *dropped* the row while the blanks kept it, so the row is also a
live source of blank/key drift. Strip it from every component except `cover/`:

```bash
python3 .claude/skills/lesson-planning/scripts/namestrip.py --project . --unit 01 --lesson 02 --check
python3 .claude/skills/lesson-planning/scripts/namestrip.py --project . --unit 01 --lesson 02
```

`--check` reports without writing (exit 1 if anything would change). It touches both the blank
and its `_key`, so the two stay in lockstep. Never strip `cover/`.

### `\noindent` trap — the vocabpar fix

`\termblanklong` opens with `\noindent`, which is a **no-op mid-paragraph**, and `\ansline` ends
with `\dotfill` without ending the paragraph. Unfixed, the intro sentence and the first term
collide in the blank, and in the key every term label after the first is dragged onto the previous
answer's dotted line. So put a `\par` on both sides inside a `vocabbox`:

```latex
% notes/main.tex
Fill in each term as we build it together.
\par\vspace{2pt}                 % \par is REQUIRED here
\termblanklong{First term}

% notes_key/main.tex — \par on BOTH ends
\newcommand{\vocabans}[2]{%
  \par\noindent\textbf{\textcolor{navy}{#1:}}\\[1pt]\ansline{#2}\par}
```

Fix it per-lesson, **not** in `shared/` — a shared-package change re-flows every already-verified
unit at once.

## Box environments (from `-boxes`)

Lesson-plan boxes take a background color as the last argument (use the aliases `goldbox`,
`greenbox`, `redbox`, or palette colors like `sky`):
```latex
\begin{skillbox}[Priority Ideas \& Skills]{goldbox} ... \end{skillbox}   % breakable
\begin{skillbox}[Activate Prior Knowledge]{sky} ... \end{skillbox}       % also skillbox
```

> **`fixedskillbox` does not exist** — there is only `skillbox`. Never write `fixedskillbox`.

Titled student boxes (title is fixed by the environment unless it takes an argument):

| Environment | Title / use | Arg |
| --- | --- | --- |
| `objectivebox` | "Primary Objective" | — |
| `learningtargetbox` | "Learning Targets — I Can…" (cover sheet) | — |
| `vocabbox` | "Vocabulary & Key Concepts" | — |
| `hookbox` | "Hook" | — |
| `notesbox{Title}` | generic titled notes section | title |
| `practicebox` | "Guided Practice" | — |
| `spiralbox` | "Connections & Big Ideas" | — |
| `scenariobox[Title]{color}` | activity/homework scenario | title, color |
| `headlinebox{color}` | colored callout strip | color |
| `blurbbox[Title]{color}` | study/excerpt blurb | title, color |
| `reflectionbox` | "Reflection" (homework) | — |
| `extensionbox` | "Extension — optional" | — |
| `tocbox` | "What's in This Packet" (cover) | — |
| `remindbox` | "Keep in Mind" (cover) | — |

Reusable component-identification table (AP Stats):
- `\componenttable` — blank version (student), four rows: Individual / Population / Sample / Variable(s).
- `\componenttablekey{ind}{pop}{samp}{vars}` — filled version (key), defined in `-key`.

## `\boxguard` — the page-break guard (from `-boxes`)

**Never let a box break leaving a ~1in sliver** — a title plus a line or two — at the top or
bottom of a page. If that little would print, push the whole box to the next page. Breaking is
fine only when each side of the break gets a substantial chunk.

```latex
\boxguard                 % 16 lines must remain, or the box starts a new page
\begin{notesbox}{2. Checking the conditions}

\boxguard[30]             % raise it when the box OPENS with something unbreakable
\begin{notesbox}{3. ...}  % a TikZ figure, an \fbox, or a tabularx never splits
```

Inside a long box, guard a bold lead-in that introduces a table so the heading never orphans from
its table: `\boxguard[14]` before the lead-in paragraph.

Prefer `\boxguard` over a hard `\newpage` — it self-adjusts when content above it changes. Reserve
`\newpage` for "this box must start a page." **Apply every guard to the blank AND its `_key`**;
they stay in lockstep.

## The work rule — `\begin{work}` (from `-boxes`, visible under `-key`)

**Any worked solution goes in a `work` block, and that block is byte-identical in the blank and
the key.** The package swap decides only whether it is shipped: under `-boxes` the blank builds
the box and emits a `\vphantom` of it (exact height, nothing on the page and nothing in the PDF's
text layer); under `-key` the same box is printed in `keyred`. The two therefore *cannot* drift —
which is what keeps a component the same length on both sides.

```latex
% notes/main.tex AND notes_key/main.tex — the same lines in both files
\begin{work}
  t &= \dfrac{\bar{x}-\mu_0}{s/\sqrt{n}} \\
    &= \dfrac{12.4-11.0}{4.2/\sqrt{25}}  \\
    &\approx 1.67
\end{work}
```

Format, non-negotiable:

- **One statement per line.** Never two steps on one row, and never an inline
  `a=b \Rightarrow c=d` chain — that is the idiom this rule replaces.
- **The `&` goes immediately before the relation**, so every relation in the block lands in one
  column. Works for `=`, `<`, `>`, `\le`, `\ge`, `\approx`.
- **Computing:** row 1 is the formula, the relation, and the substitution; every later row starts
  at the `&=` and aligns to the one above.
- **Multi-step (a test statistic, a margin of error, an interval):** one row per step, each
  aligned on its relation.

Do not wrap a `work` block in `\[ \]`, `align`, or `equation` — it supplies its own display. It is
set flush left (2em indent), not centered.

**When it applies:** a task that asks for multi-step work. A table cell holding a single final
answer is already the same size in both files — leave those as `\blank{}`/`\ans{}`. `work` blocks
do not go inside table cells; if a table asks for real work, pull the items out of the table.

`\workrowsep` (default `0pt`) adds leading between rows. It moves the blank and the key together,
so raising it for handwriting room can never break the match.

### `steptable` / `\step` — a *printed* solution, aligned on its relation

`work` is for steps the **student** writes. Its counterpart is for steps **printed in both files**
— the "name the reason for each line" tables, where the computation is given and the student says
what each line does (which condition it checks, which quantity it estimates). Same alignment
requirement, different mechanism: a plain one-column table cannot align relations, so the step is
split into a right-aligned left side and a left-aligned relation + right side.

```latex
\begin{steptable}[Why this step]        % bare → "Reason for this step"
  \step{z}{=\dfrac{x-\mu}{\sigma}}{Standardizing formula}
  \step{}{=\dfrac{74-70}{2.5}}{\blank{6.0cm}}
  \step{}{=1.6}{\blank{6.0cm}}
\end{steptable}
```

Argument 2 begins with the relation. Use `\steprel{lhs}{cell}{reason}` when the *relation itself*
is what the student supplies — comparing a p-value to $\alpha$, where the direction is the point:
`\steprel{p\text{-value}}{\blank{0.9cm} $\alpha$}{\blank{6.0cm}}`.

Only column 3 differs between the blank and the key, so the two cannot drift. It is a **chain**
rule: a table of independent statements to classify is a list, not a solution, and stays a plain
table.

## Teacher notes — in the lesson plan, one per component

**Teacher-only prose goes in the lesson plan, never in a `_key`.** A `teachernote` is the one block
in a key with no counterpart in the blank, so it makes the key run longer than its blank for no
student-facing reason — the last thing costing a packet blank pages once the work rule is in.

The lesson plan closes with one note per component, in packet order, each titled for it:

```latex
\begin{teachernote}[Warm-Up]        ... \end{teachernote}   % → "Teacher Note: Warm-Up"
\begin{teachernote}[Guided Notes]   ... \end{teachernote}
\begin{teachernote}[Group Activity] ... \end{teachernote}
\begin{teachernote}[Exit Ticket]    ... \end{teachernote}
\begin{teachernote}[Homework]       ... \end{teachernote}
```

The environment is defined in **`-boxes`** (the lesson plan does not load `-key`) and the argument
is **optional** — a bare `\begin{teachernote}` still renders plain "Teacher Note", so the ~136
keys not yet migrated keep compiling. To migrate one lesson:

```bash
python3 .claude/skills/lesson-planning/scripts/movenotes.py unit01/lesson02 --check   # report only
python3 .claude/skills/lesson-planning/scripts/movenotes.py unit01/lesson02
```

It lifts the note out of each `_key`, appends it to the plan with the right title, and refuses to
run twice on the same lesson. Rebuild afterward and confirm every component matches its key page
for page.

## Answer-key macros (from `-key`)

| Macro / env | Effect |
| --- | --- |
| `\ans{text}` | Inline answer in bold `keyred`; use in place of a blank |
| `\ansline{text}` | Bold `keyred` answer that fills a write-line with a dotted trail |
| `\componenttablekey{..}{..}{..}{..}` | Filled component-ID table |
| `work` (env) | Worked steps — **defined in `-boxes`**, authored identically in both files; see "The work rule" |

**`teachernote` is no longer a key macro.** It lives in `-boxes` and belongs in the **lesson
plan** — see "Teacher notes" above.

**`\ansline` is the other place lengths drift.** A `\writeline` in the blank is exactly one line;
an `\ansline` whose prose wraps to four is three lines longer. When a key's prose answer runs long,
give the blank `\writelines{n}` for the same n — the same principle as the work rule, applied by
hand because prose cannot be measured from a shared body.

**`\writelines{n}` occupies exactly n line slots** — the breaks go *between* the rules, never
after the last one, so it matches *n* `\ansline{}` calls in the key with nothing left over. (It
used to end in a trailing `\\`, which added a spurious empty line and was a standing cause of a
blank running a page past its key.) Raising one is still *not* free: it can overflow a 2pp blank
to 3pp against a 2pp key. Set n from the key's true wrapped length, then rebuild and re-measure
the **blank**.

**Reach for `work` before `\writelines`.** If the answer is a multi-step computation rather than
prose, a `work` block fixes the drift correctly and cannot come apart; a lengthened write-line only
papers over it.

**Key-authoring rule:** copy the blank component verbatim, then replace each blank/`\writeline`
with `\ans{…}`/`\ansline{…}` and mark correct multiple-choice options, e.g.
`\textcolor{keyred}{\textbf{$\leftarrow$ correct}}`. The key and blank must stay structurally
identical so they paginate the same way.

## Color palette (from `-colors`)

The course was recolored to an earthy-yellow palette, so the names no longer describe their
hues — `navy` is a dark olive and `sky` is a pale cream. **Use the names, not the hues.**

Primary: `navy` (#3A3D28, dark olive — the frame/banner color), `navylight` (#6E7340),
`sky` (#F8F8EE, the pale background), `skymid` (#DCD08A, the banner subtitle), `goldacc` (#C39A1F),
`goldbg`, `hookbg`, `greenbg`/`greenacc`, `redbg`/`redacc`, `charcoal`, `slate`, `linegray`,
`keyred` (#BF3A1C — every answer). Lesson-plan background aliases: `goldbox`, `greenbox`, `redbox`.

Algebra 2's `forest` family (`forest`, `forestbg`, `forestmid`, `forestlight`) is **not defined
here**. When porting anything from that course, map `forest`→`navy`, `forestbg`→`sky`,
`forestmid`→`skymid`, `forestlight`→`navylight`.

## Lesson-plan section order (canonical, gradual release)

Primary Objective / CED alignment / Lesson model → Learning Targets & Key Understandings →
Vocabulary, Concepts & Theorems → Lesson at a Glance (55-min phase table: **5/22/16/8/4**) →
Warm-Up (the seeds) → **Guided Notes & Practice — I do, we do, you do** (pacing 12/6/4; the
must-land section; the questions asked while students hold the pen; the formative-check item and
its reteach trigger) → **Group Activity** ("one activity for the whole class — there is no tiered
version"; launch + ground rule, then what students do | what the teacher does) → **Debrief —
whole class** (open on the *almost*-right crux answer; the Debrief-box walkthrough) →
**AP Practice — assigned, not scored** → **Homework — scored, due next class** (with the
DeltaMath override) → Watch For → Close & Assign → Teacher Notes (`[Warm-Up]`,
`[Guided Notes \& Practice]`, `[Group Activity]`, `[AP Practice]`, `[Homework]`).

Tag the objective with the CED Topic, Big Idea, AP Skill, LO, and EK (see `ap-workflow.md`).

**There is no `fixedskillbox` in this course** — every lesson-plan box is `skillbox` (breakable).
Where Algebra 2 uses `fixedskillbox` to keep a phase table intact, use `skillbox` preceded by a
raised `\boxguard[30]`; a `tabularx` never splits on its own, so the guard is what protects it.

*(Legacy plans use either the pre-EFFL Hook / Explicit Instruction / Tiers / Exit Ticket order or
the EFFL Activity / Debrief / Application / CYU order. Leave them alone unless regenerating.)*
