# Standards Workflow

Use this when the project has **no** `spec/ap-*` documents (e.g. Algebra 2). The lesson is
driven by three inputs the user supplies:

1. **Lesson title** — e.g. "Solving Linear Equations".
2. **Description** — a few sentences on what the lesson covers and why.
3. **Standards** — the list being addressed. These are usually codes from the course's
   framework (for Virginia courses, SOL codes such as `A.1`, `AII.3`; elsewhere CCSS, state
   standards, or a district scope-and-sequence). Take them as given; don't invent codes.

If the user gives only a title, ask for the description and standards before authoring — those
two are what make the lesson plan specific rather than generic. A review lesson (e.g. Algebra 2
Unit 1) uses the same skeleton; its "standards" are typically the prerequisite skills being
re-activated.

## Mapping inputs into the lesson

The document structure is identical to the AP path (`references/components.md`); only the
*source* of the content differs. There are no Big Idea / Skill tags.

| Lesson element | Source |
| --- | --- |
| Lesson title (`\LessonNumberName`) | the supplied title |
| **Primary Objective** | one or two sentences distilled from the description (what students will be able to do) |
| **Priority Ideas & Skills** | the concrete skills implied by the standards + description; group them as the lesson's priority list |
| **Vocabulary, Concepts & Theorems** | the terms and formulas the lesson introduces or relies on |
| **Learning Targets** (cover, "I can…") | one target per standard (or per major skill), reworded as "I can …" |
| Standards line | the supplied standard codes, recorded in the lesson plan (and a coverage log if the project keeps one) |
| Guided notes / activity / exit ticket / homework | practice that exercises each standard; scale the activity tiers (R/A/E) across the difficulty range the standards imply |

## Steps

1. Confirm the title, description, and standards with the user; clarify scope if a standard is
   broad enough to span multiple lessons.
2. Scaffold the lesson (`scripts/new_lesson.py`) with the components you need — note Algebra 2
   uses inline course macros, so pass `--course` so the generated lesson plan defines
   `\CourseName` correctly.
3. Author the lesson plan and components per `references/components.md`, keeping the objective
   and learning targets traceable to the standards.
4. Mirror Algebra 2's existing assessment conventions where they apply — e.g. an "SOL-Style
   Multiple Choice" item in the Individual Work & Assessment section and on the exit ticket.
5. Build (`references/build.md`).

The live project is the gold reference: open a built Algebra 2 lesson and match its tone,
section depth, and box usage.
