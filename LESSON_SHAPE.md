---
course: Statistics
prefix: apstats
meeting_length: 55
reference_lesson: unit01/lesson01
components: [cover, warmup, notes, ap_practice, homework, slides]
keyed: [warmup, notes, ap_practice, homework]
one_page: [warmup]
doc_titles:
  warmup: Warm-Up
  notes: Guided Notes \& Practice
  ap_practice: AP Practice
  homework: Homework
  activity: Group Activity
  experience: Experience \& Formalize
  exit_ticket: Exit Ticket
note_labels:
  warmup: Warm-Up
  notes: Guided Notes \& Practice
  ap_practice: AP Practice
  homework: Homework
skeletons: templates/lesson
unit_tests: true
structure_source: ced
spec_dir: spec
course_index: COURSE_OUTLINE.md
check_target: false
---

# Lesson Shape — AP Statistics

This is the course profile the shared `lesson-planning` skill (`~/.claude/skills/lesson-planning/`)
reads before authoring anything. The skill carries the mechanism — build, LaTeX rules, workflow,
scripts; **this file carries the policy** — everything true of this course that is not
necessarily true of the others. Keep it current: when a convention changes, change it here first.
The frontmatter is machine-read by the scaffolder; the sections below are read by the skill at
Step 0. The skeletons and the per-component spec live in `templates/lesson/`.

## 1. The lesson shape

**Every new lesson follows a traditional gradual-release model: I do → we do → you do.** The
teacher delivers the vocabulary and the core idea directly in guided notes, in **two longer
sections**; a guided practice problem is worked together with students holding the pen; a
whole-class debrief closes the loop; and **the period ends with students starting the homework
in class, alone** — the homework *is* the individual practice.

| Phase | Minutes | Component |
| --- | --- | --- |
| Warm-up | 5 | `warmup` |
| Guided notes & practice (I do ~20, we do ~14) | 34 | `notes` |
| Debrief — whole class, spoken | 8 | — (in the plan only) |
| Close & start the homework, alone, teacher circulating | 8 | `homework` |

**`notes` — *Guided Notes & Practice* — is the in-class centrepiece:** an objective box and a
vocabulary box filled *as each term is named*; **exactly two numbered notes sections** (the I
do), each long — the second half of a section is introduced by a bold run-in heading
`\textbf{\textcolor{navy}{Its Title.}}` rather than a second box; then a `practicebox` worked
together (the we do; it takes no argument, its title is fixed as "Guided Practice"). **The notes
end there.** Target 3–4 pages at 12pt. **The crux — the item that surfaces the lesson's target
misconception — lives in the second half of section 2.**

**`ap_practice`** — four multiple-choice items (five options, in context) plus one multi-part
free-response set, AP format. **`homework`** — the graded individual practice, in a *third*
context (instruction, guided practice, and homework each use a different one). **`cover`** —
packet table (Warm-Up · Guided Notes & Practice · AP Practice · Homework), learning targets that
name the formal term in bold, and a *Keep in Mind* box that carries the lesson's ideas, never the
lesson's process. **`slides`** — the Beamer deck, ordered targets → warm-up → I-do divider → two
instruction frames → we-do → debrief → close & start the homework.

**What this course does not have — do not re-add any of it:**

- **No group activity.** Never scaffold, author, or restore `activity/`; the notes absorbed it.
- **No exit ticket.** The formative read comes twice — circulating during Guided Practice, and
  again during the supervised homework start — and the plan says what to do with each of three
  piles of what the teacher sees.
- **No independent practice set in the notes, no *Putting It Together* transfer set, no
  `reflectionbox`.** The debrief is spoken; the individual practice is the homework.
- **No tiered instruction.** One document, one version, for the whole class. Differentiation is
  in how the teacher circulates, not on the page.

**`unit01/lesson01` is the reference implementation** of this shape. Mirror its preamble, box
usage, pacing, and tone; the live lesson overrides every document, this one included.

## 2. Grading and homework policy

Every lesson carries **both** back-of-packet components, authored every time:

- **`ap_practice` — assigned but NOT scored.** The cover's score column prints `\textbf{NA}`.
  Students keep it and bring it to review.
- **`homework` — the lesson's GRADED practice**, last in the packet. **Paper homework is the
  default** and is generated for every lesson. DeltaMath is an *occasional* override the teacher
  may choose on a given day — never the default, never assumed by the author. When used, it
  replaces the page, the cover's score cell is struck, and the page stays in the packet as extra
  practice. The plan carries the DeltaMath-override note.
- **Homework is due the first class after two study halls** — never "due next class." Write it
  that way on the cover and in the plan.

## 3. Where structure comes from

The **College Board CED** in `spec/` — `ap-statistics-course-and-exam-description.pdf` and the
course-at-a-glance files. **One CED Topic maps to one lesson**; confirm the mapping with the user
before authoring (`references/ap-workflow.md` in the skill). The units are shorter than the CED
by choice (Unit 1 is 8 lessons); **trust the live `unit*/lesson*` directories, not
`COURSE_OUTLINE.md`**, for what exists. `COURSE_OUTLINE.md` is the unit → lesson index; update its
row after authoring a lesson.

**AP habits of mind** in every component: real, plausible contexts; every answer phrased **in
context**; conclusions acknowledge uncertainty. That is what the exam scores.

## 4. Style notes

- **Prefix `apstats`** — `shared/apstats-{colors,article,boxes,key,beamer}.sty`.
- **Course macros live in the style package.** `\CourseName` (`Statistics`), `\SchoolYear`, and
  `\MeetingLength` are defined in `apstats-article.sty`; a lesson plan sets only `\UnitNumberName`
  and `\LessonNumberName`. The printed title is **just `Statistics`** — no teacher name, no school
  year, anywhere a title renders.
- **Palette** — the course was recolored to an earthy-yellow scheme, so the names no longer
  describe the hues: `navy` is a dark olive (#3A3D28), `sky` a pale cream. Defined:
  `navy navylight sky skymid goldacc goldbg hookbg greenbg greenacc redbg redacc charcoal slate
  linegray keyred goldbox greenbox redbox`. Bare `gold` is undefined — use `goldacc`/`goldbg`.
- **Algebra 2's `forest` family is undefined here.** When porting: `forest`→`navy`,
  `forestbg`→`sky`, `forestmid`→`skymid`, `forestlight`→`navylight`. The deck's header macro is
  `\navyheader`, not `\forestheader`.
- **`fixedskillbox` does not exist** — the only lesson-plan box is `skillbox` (breakable). Where a
  phase table must stay intact, `\boxguard[30]` before the `skillbox`.
- **`tierbox` does not exist** and there is no tiered instruction — drop the concept.
- `practicebox` takes **no** argument; a titled box is `notesbox{Title}`. `work` takes **no**
  argument and its body is math (an amsmath `aligned`).
- `\ding{55}` — `pifont` is not loaded; use `\textbf{$\times$}`.
- `[resume]` on an `enumerate` split across `tcolorbox`es does not carry; accept per-box
  numbering (A1/B2) or keep the enumerate in one box.
- `\termans{Term}{def}` is defined in `apstats-key.sty` (two arguments) — never redefine it.
  `\par` still brackets each `\termblank`/`\termans` inside a `vocabbox` (the vocabpar fix).
- `\componenttable` / `\componenttablekey{ind}{pop}{samp}{vars}` — the Individual / Population /
  Sample / Variable(s) table, blank and key.
- Every student component is 12pt; the plan is 10pt. `\namedateperiod` on the cover and the unit
  tests only.

## 5. Lesson-plan section order

Primary Objective (tagged with CED Topic, Big Idea, AP Skill, LO, EK) → Learning Targets & Key
Understandings (the target misconception named) → Vocabulary, Concepts & Theorems → Lesson at a
Glance (55-min phase table **5 / 34 / 8 / 8**) → Warm-Up → **Guided Notes & Practice — I do, we
do** (the must-land section; the questions asked while students hold the pen; the formative
read and its reteach trigger) → **Debrief — whole class, spoken** (open on the *almost*-right crux
answer) → **AP Practice — assigned, not scored** → **Homework — scored, due the first class after
two study halls** (with the DeltaMath override) → Watch For (the misconception again) → Close &
Start the Homework → Teacher Notes, **four** of them in packet order: `[Warm-Up]`,
`[Guided Notes \& Practice]`, `[AP Practice]`, `[Homework]`.

## 6. Unit-level assessments

A unit holds `tests/` (`practice_test/`, `actual_test/`; `include ../../shared/tests.mk`; its
`drop` publishes the *practice* test to `sample_test/main.pdf`), `test_keys/` (likewise, to
`sample_test_key/main.pdf`), the two `sample_test*` drop-in dirs (merged into the unit student /
key packets by `shared/unit.mk`), and `unit_cover/` + `binder_cover/` at the front. **The actual
test and its key are never merged into any packet.** The scaffolder creates all of this the first
time a unit is created. Build: `make -C unitXX/tests all && make -C unitXX/test_keys all`. The
practice test and its key must be the same number of pages.

There is no course-wide final in this repository.

## 7. Legacy shapes and regeneration

Recognize the shape by the component directories:

| Shape | Has | Notes |
| --- | --- | --- |
| **current** | `notes/` + `ap_practice/`, no `activity/` | the target |
| **group-activity** (2026-08) | `notes/` + `activity/`, no `exit_ticket/` | `unit01/lesson00` |
| **EFFL** | `experience/` | `unit01/lesson02`–`lesson07` |
| **pre-EFFL legacy** | `notes/` + `activity/` + `exit_ticket/`, tiered activity boxes | units 02–09 |

The build accepts all of them. When asked to touch one, **ask whether to regenerate it** in the
current shape.

**From the group-activity shape:**

1. Fold the activity's crux scenario into the **second half of notes section 2**, re-voiced as
   direct instruction. Its debrief becomes the *spoken* whole-class debrief in the plan — no
   `reflectionbox`.
2. `git rm -r activity activity_key`.
3. Repace the plan to **5 / 34 / 8 / 8**, delete its Group Activity `skillbox`, fold its teacher
   note into the Guided Notes one (four notes, not five).
4. Renumber the cover's packet table to four rows; re-voice its *Keep in Mind* box so the third
   move is **starting the homework in class**, not a third practice set.
5. Re-title the deck's activity divider and launch frames as the supervised homework start.

**From the EFFL shape:**

1. Scaffold `notes`, `notes_key` into the existing lesson dir.
2. Fold the old **QuickNotes** into the two notes sections' fills, the old **Application** into
   the `practicebox`, and the old **Check Your Understanding** and **Activity** into the
   **homework** — re-voiced to *use* the vocabulary rather than discover it.
3. The debrief is spoken and lives in the plan; no `reflectionbox`.
4. Delete `experience`, `experience_key`.
5. If the lesson has no `ap_practice/`, split the existing homework: AP-format items to
   `ap_practice/` (unscored), and author a **new scored homework** in a fresh context.
6. Rewrite the cover's packet table (Warm-Up · Guided Notes & Practice · AP Practice with `NA` ·
   Homework) and re-voice its learning targets with the formal vocabulary.
7. Rewrite the plan in gradual-release order; re-cut its teacher notes to four.
8. Reorder the deck: targets → warm-up → I-do divider → two instruction frames → we-do →
   debrief → close & start the homework.

**From the pre-EFFL legacy shape:** the same, plus delete `exit_ticket`, `exit_ticket_key` (fold
its item into the homework) and flatten the tiered activity into instruction for the whole class.

Either way, delete stale stamps — `rm -rf .stamps/unitXX/lessonYY target/unitXX/lessonYY` — or
`make` will skip a sibling whose PDF was cleaned and `pdfunite` will fail. Finish with the
evidence per lesson: `make -C unitXX/lessonYY all` exits 0 and every component's page count
equals its `_key`'s, compared on the compiled components, not the padded packets.

**Scoreboard (2026-09):** 1 of 78 lessons is in the current shape (`unit01/lesson01`); 1 in the
group-activity shape (`unit01/lesson00`); 6 in EFFL (`unit01/lesson02`–`07`); 70 pre-EFFL legacy,
of which 96 `_key` files still hold teacher notes, `\namedateperiod` appears on every component,
and 57 lessons have no deck. Convert lesson by lesson or unit by unit as you review, authoring
the missing deck as you go, and rebuild the unit packet each time — never the whole course in one
pass.

## 8. Review order

When reviewing or converting a lesson: shape → deck → teachernotes → namestrip → work rule →
boxguard → vocabpar, then build and prove page parity.
