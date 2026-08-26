# AP CED Workflow

Use this when the project has College Board AP documents in `spec/` (files named `ap-*.pdf`).
The goal: turn one CED **Topic** into one lesson, with the framework codes driving the
objective, skills, learning targets, and standards.

## The spec documents

| File | Use |
| --- | --- |
| `ap-*-course-at-a-glance.pdf` | Structural backbone: unit list, per-unit pacing + exam weighting, the ordered topics, and each topic's Big Idea + Skill tag. **Read this first.** |
| `ap-*-course-and-exam-description.pdf` | The full CED (large). Contains per-topic **Required Course Content**: Enduring Understanding, Learning Objectives, Essential Knowledge, Illustrative Examples. The authoring source. |
| `ap-*-course-overview.pdf`, `...poster.pdf` | Supplementary framing (skill category definitions, big-idea descriptions). Optional. |

Read PDFs with the techniques in `/mnt/skills/public/pdf-reading/SKILL.md`. For these text-layer
PDFs, `pdftotext -layout` is sufficient; rasterize only if a topic's layout is ambiguous.

## The framework vocabulary (AP Statistics example)

- **Big Ideas** (spiral across the course), used as the tag on objectives:
  `VAR` Variation & Distribution · `UNC` Patterns & Uncertainty · `DAT` Data-Based Predictions,
  Decisions & Conclusions. (Other AP courses have their own set — read them from the spec.)
- **Skill categories** (spiral across topics): `1` Selecting Statistical Methods ·
  `2` Data Analysis · `3` Using Probability & Simulation · `4` Statistical Argumentation.
- **Code scheme:**
  - Enduring Understanding → `BIGIDEA-n` (e.g. `VAR-1`)
  - Learning Objective → `BIGIDEA-n.LETTER` (e.g. `VAR-1.A`), each tagged `[Skill x.y]`
  - Essential Knowledge → `BIGIDEA-n.LETTER.number` (e.g. `VAR-1.A.1`)

## Extraction steps

1. **Identify the target topic.** From course-at-a-glance, find the topic number/title for the
   lesson (e.g. Topic 1.1 "Introducing Statistics: What Can We Learn from Data?") and note its
   Big Idea and Skill tag and the unit's pacing/weighting.
2. **Pull the topic's Required Course Content from the CED.** Locate the topic page (search the
   extracted text for `TOPIC 1.1`) and capture:
   - the **Enduring Understanding** (code + sentence),
   - every **Learning Objective** (code, sentence, and its `[Skill x.y]`),
   - every **Essential Knowledge** statement under each LO (code + sentence),
   - any **Illustrative Examples** (useful for vocabulary and problem contexts).
3. **Normalize the text.** CED extraction sometimes injects control characters (e.g. `\u0007`
   in place of a non-breaking space) and hyphenates across line breaks — strip control chars and
   rejoin wrapped lines before using the text.
4. **Confirm the mapping with the user** before authoring: show the topic, EU, the LO/EK list,
   and the proposed lesson title. Topics occasionally span more than one lesson, or you may
   bundle two short topics — let the user decide the granularity.

## Mapping CED content into the lesson

| Lesson element | Source |
| --- | --- |
| Lesson title (`\LessonNumberName`) | "Lesson X.Y: <Topic title>" |
| **Primary Objective** (lesson plan) | Restate the EU + LOs as student-facing aims; tag with the Big Idea, e.g. "(Big Idea: VAR)" |
| **Priority Ideas & Skills** (lesson plan, gold box) | Left: the AP Skill category + the specific sub-skill (e.g. "AP Skill 1 — Selecting Statistical Methods: identify the question to be answered"). Right: "Key Understandings" paraphrased from the EKs |
| **Vocabulary, Concepts & Theorems** | Terms named in the EKs and Illustrative Examples |
| **Learning Targets** (cover, "I can…") | One target per Learning Objective, reworded as "I can …" |
| Standards line | The LO/EK codes addressed (e.g. `VAR-1.A`, `VAR-1.A.1`) — record them in the lesson plan and, if the project keeps a coverage log, there too |
| Guided notes / activity / exit ticket / homework | Practice that exercises the named Skill against the EK statements; mirror the cognitive level of the LO verbs (identify, classify, construct, describe, justify) |

Keep wording **paraphrased**, not copied verbatim from the CED — the lesson should restate the
framework in teaching language, with the codes as the audit trail.

## Worked fragment (Topic 1.1)

From the CED: EU `VAR-1` ("Given that variation may be random or not, conclusions are uncertain."),
LO `VAR-1.A` ("Identify questions to be answered, based on variation in one-variable data. [Skill 1.A]"),
EK `VAR-1.A.1` ("Numbers may convey meaningful information when placed in context.").

Produces, in the lesson plan:
```latex
\begin{tcolorbox}[colback=sky,colframe=navy,boxrule=0.9pt,arc=2mm,...]
  \textbf{Primary Objective:} Students will identify statistical questions that can be
  answered with one-variable data, and explain why placing numbers in context gives them
  meaning --- recognizing that variation makes conclusions uncertain (Big Idea: VAR).
\end{tcolorbox}
...
\begin{skillbox}[Priority Ideas \& Skills]{goldbox}
  \textbf{AP Skill 1 --- Selecting Statistical Methods}
  \begin{itemize}\item Identify the question to be answered from a context (Skill 1.A).\end{itemize}
\end{skillbox}
```
Standards addressed: `VAR-1.A`, `VAR-1.A.1`.

**On the cover, that target must be de-spoilered.** "I can identify a *statistical question*" names
the term the debrief is meant to attach, so the cover gets the plain-language version instead —
"I can tell which questions data can actually answer, and which it can't." The formal LO stays in
the lesson plan. See the spoiler rule in `components.md`.

## EFFL: where CED content lands in the lesson

One CED **Topic** still maps to one lesson, but the pieces land in EFFL order — the vocabulary
arrives *after* the activity, not before it:

| CED piece | Where it goes |
| --- | --- |
| Topic, Big Idea, Skill, LO, EK codes | the lesson plan's objective box (the audit trail) |
| LO, as an "I can…" statement | plan: Learning Targets · cover: **de-spoilered** version |
| EK, as the "why" | plan: Key Understandings — with the target misconception named |
| The formal terms and notation the EK introduces | plan: Vocabulary box · packet: the
  **QuickNotes** box, filled during the debrief — **never** the activity, cover, or early slides |
| The reasoning the LO asks for | the Activity: students reach it from prior knowledge, in their
  own words, before it has a name |
| AP-style application of the topic | the Application, then Check Your Understanding |
| AP-style MC/FRQ reps on the topic | the **homework** (the graded practice) |

The practical consequence: read the EK to decide **what the groups must discover**, then design
two scenarios that get them there with only prior knowledge — and put the EK's own wording in
QuickNotes, where the debrief attaches it.

For the rest of the document structure, follow `references/components.md`; for macros and boxes,
`references/conventions.md`.
