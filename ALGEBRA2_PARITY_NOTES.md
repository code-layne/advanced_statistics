# Algebra 2 Parity Notes

Context for bringing the AP Statistics course up to parity with the conventions and
build system developed in `../algebra_2`. Written 2026-07-30 on branch
`claude/algebra-2-course-updates-5cf220`.

Companion to `UNIT_PACKET_REFACTOR_NOTES.md`, which records the unit-wrapper
pagination work that came before this.

---

## Part 1 — Done: authoring conventions ported

Five named conventions came over from algebra_2, along with the macros that back them.
**Additive only — no existing document changes how it renders.**

### Macros added to `shared/`

| Macro / env | Package | What it does |
| --- | --- | --- |
| `\boxguard[n]` | `apstats-boxes` | `\Needspace{n\baselineskip}` (default 16). Put on its own line before a breakable box so it never breaks leaving a ~1in sliver. |
| `work` (env) | `apstats-boxes` | Worked steps. Under `-boxes` ships a `\vphantom` (exact height, no ink, nothing in the text layer); under `-key` prints the same box in `keyred`. |
| `steptable` / `\step` / `\steprel` | `apstats-boxes` | A *printed* solution aligned on its relation, where only column 3 (the reason) differs between blank and key. |
| `teachernote` | `apstats-boxes` | **Moved here from `apstats-key`**, now takes an optional component title: `\begin{teachernote}[Exit Ticket]`. |
| `\aps@workvisibletrue` | `apstats-key` | Flips `work` blocks visible in keys. |

`needspace` is now required by `apstats-boxes`.

### Why the `work` environment is the important one

The block is authored **byte-identically in the blank and the key**. Both files build
the box through the same code with the same formatting; the package swap decides only
whether it is shipped. The two therefore *cannot* drift, which is what makes a component
the same number of pages blank and keyed without anyone counting lines.

Format rules: one statement per line, `&` immediately before the relation so the whole
block aligns on it. Never `$a=b \Rightarrow c=d$` on one line — that is the idiom this
replaces.

### The five conventions

| Name | Rule |
| --- | --- |
| **work rule** | A component is the same number of pages blank and keyed. |
| **boxguard** | No box stranded as a ~1in sliver across a page break. |
| **teachernotes** | Teacher prose in the lesson plan, one titled note per component — never in a `_key`. |
| **namestrip** | Name/date/period row on the cover only. |
| **vocabpar** | `\par` on both sides of `\termblanklong` / `\ansline` inside a `vocabbox`. |

### Skill changes (`.claude/skills/lesson-planning/`)

- **New Retrofit mode.** `apply boxguard namestrip retrofit to 1.1 and 1.3` is a
  first-class invocation, with a per-convention table and a requirement to close with
  build + page-count evidence.
- **Hard constraints 1b/1c** — page-for-page parity (with a `pdfinfo` check loop) and
  `\boxguard`.
- **`references/conventions.md`** — full spec for all five (+177 lines).
- **`references/build.md`** — refreshed against *this* project's build (unit wrappers),
  not algebra_2's.
- **Scripts** — `namestrip.py` and `movenotes.py` added; both take `--check`.
- **`new_lesson.py`** — now scaffolds namestrip-clean components and a lesson plan
  pre-stubbed with five titled `teachernote`s.

### Global rules (`~/.claude/CLAUDE.md`)

- **Fixed a real bug:** the Compile QA snippet compiled in-place, overwriting tracked
  `main.pdf` files (prefab components, slide decks) in the source tree. It now uses
  `-output-directory` into a per-document scratch dir. It also used one shared
  `/tmp/scan.log`, so on a failure you were often reading a different document's errors.
- Added the page-parity section and three known-bad rows, including the two failure
  modes that produce **no compile error at all**: a `teachernote` in a key, and a `work`
  block that differs between blank and key.

### Verification

136 existing documents compiled clean across all nine units — every lesson plan and the
keys that use `teachernote`. A throwaway scaffolded lesson compiles, is namestrip-clean
out of the box, and every component matches its key page-for-page.

### Backlog — nothing is retrofitted yet

- **~136 `_key` files still carry teacher notes.** Run `movenotes.py` per lesson.
- **`\namedateperiod` is on every component**, not just covers. Run `namestrip.py`.
  Note: this course's keys mostly *dropped* the row while blanks kept it, so namestrip
  **fixes an existing blank/key mismatch** rather than creating one.
- No lesson uses `work` blocks yet, so blank/key page parity is currently unenforced.

Retrofit lesson by lesson (or unit by unit) while reviewing, and rebuild the unit packet
each time. Do not attempt the whole course in one pass.

---

## Part 2 — Next: four work products per lesson

**Goal.** Replace the current `student` + `full` pair with **four** per-lesson products:

| File | What it is |
| --- | --- |
| `lessonYY_plan.pdf` | the lesson plan — the lesson-root `main.tex`, compiled |
| `lessonYY_slides.pdf` | the deck, one slide per page (display + Google Slides import) |
| `lessonYY_student.pdf` | cover + blank components, paginated packet-wide |
| `lessonYY_key.pdf` | the same packet answered, **page for page** with the student one |

`full` disappears. The plan and the deck become standalone deliverables instead of being
buried in a teacher packet.

**Explicitly NOT ported:** algebra_2's fifth product, `lessonYY_slides.pptx`, and its
`shared/pdf2pptx.py`. `UNIT_PACKET_REFACTOR_NOTES.md` already rules out a PowerPoint
generation step for this workflow.

### The open design question — resolve this before writing any Makefile

The two courses solved continuous pagination **differently**, and they are not
compatible:

- **algebra_2** merges component PDFs with `pdfunite`, then re-runs the merged PDF
  through `shared/paginate.tex`, which overlays packet-wide page numbers (a white band
  inside the bottom margin hides each component's own number) and forces every component
  to start on a **recto**, inserting numbered blank versos.
- **this course** compiles a unit wrapper `.tex` (`unitXX_student.tex` /
  `unitXX_full.tex`) that source-includes each component with `docmute` + `import`, so
  pagination is continuous by construction — there is no overlay pass.

Decide which layer owns pagination before mirroring anything. Mixing them means a packet
numbered twice. The wrapper approach is already working here for units; the algebra_2
approach numbers at the *lesson* level, which is what makes a standalone
`lessonYY_student.pdf` paginate on its own.

Also note: algebra_2 forces recto starts and inserts blank versos. This course currently
does not. That is a **pedagogical/print decision**, not a technical one — confirm it
before adopting.

### What to mirror from algebra_2

- `shared/lesson.mk` — targets `all plan slides student key` (drop `pptx`). Relevant
  variables: `PLAN_OUT`, `SLIDES_OUT`, `STUDENT_OUT`, `KEY_OUT`, `STUDENT_ORDER`,
  `KEYED_PAIRS`, `ALIGN_STAMPS`.
- `shared/handout.tex` — the 3-up printed form of a deck: three slide thumbnails down a
  left column, a ruled `Notes` area beside each. Invoked with `\def\DeckSource{...}` and
  `\def\DeckPages{n}` (the Makefile gets the count from `pdfinfo`; LaTeX cannot count an
  external PDF's pages). **Change the `\usepackage{algebra2-colors}` line to
  `apstats-colors`.**
- `shared/paginate.tex` — only if the lesson-level pagination approach wins above. Its
  band geometry is measured against `algebra2-article.sty`'s bottom margin (0.75in);
  `apstats-article.sty` uses the same, but **re-measure** with
  `pdftotext -f <p> -l <p> -bbox` before trusting it.
- `shared/unit.mk` / root `Makefile` — units aggregate only `student` and `key`; the plan
  and the deck stay per-lesson.

### Knock-on changes

- The unit wrappers `unitXX_student.tex` / `unitXX_full.tex` need renaming/reworking —
  `unitXX_full.tex` becomes `unitXX_key.tex` and loses the lesson plans and the slide
  handout, since both become standalone products.
- `make full` must fail loudly rather than silently doing nothing.
- The skill's `references/build.md`, SKILL.md Step 5, and `UNIT_PACKET_REFACTOR_NOTES.md`
  all describe `student`/`full` and will be wrong.
- Every lesson then owes a deck (`slides` feeds a product), so it stops being optional in
  `new_lesson.py`'s defaults.

---

## Part 3 — Next: binder covers

**Goal.** Per-unit binder cover sheets, as in algebra_2's `shared/cover.py`.

### How it works there

A two-page letter PDF — same sheet twice, page 1 for the front of the binder, page 2 for
the back. Background art is built **from that unit's own lessons**. Content comes from
one of two places:

- `unitNN/binder_cover/spec.py` — a hand-tuned spec (`ELEMENTS`: a list of dicts with a
  type, payload, and placement). Authoritative when present.
- **auto-discovery** — otherwise the unit's lesson sources are scanned for plotted
  functions, worked solutions, and display equations, laid out on a jittered grid.
  Deterministic for a given `--seed`, so `make` stays honest.

Unit number comes from the directory name; unit title from `\UnitNumberName` in
`unitNN/lesson*/main.tex` — never hardcoded.

```bash
python3 shared/cover.py unit01          # → unit01/binder_cover/main.pdf
python3 shared/cover.py --check-fonts
make -C unit01 clean_unit_cover         # throw it away and redraw
```

### Wiring

`binder_cover/` is a prefab-PDF component like `sample_test/`, with one difference: its
`main.pdf` is *generated*. In `shared/unit.mk` the rule has **no prerequisites on
purpose** — once generated the cover is a stable artifact, because a regenerated cover is
byte-different every time (jitter) and would otherwise churn on every build. `make -C
unitXX clean_unit_cover` is the explicit "redraw it" escape hatch.

### What needs adapting for AP Statistics

- **Ink budget is a hard constraint** — these print on a school printer. White
  background, no solid fills, line work in grays `#5f5f5f`–`#c9c9c9`, `#ffffff` fills for
  occlusion only. Keep this.
- **Auto-discovery is tuned for algebra**: plotted functions, solved equations, display
  math. AP Stats lesson sources hold dotplots, boxplots, normal curves, scatterplots with
  LSRL, and formula displays (`\bar{x}`, `SE`, test statistics). The scanner and the
  element renderers will need statistics-appropriate types, or every unit falls back to a
  thin cover.
- **Fonts.** Four OTFs must be installed where the OS font service can see them:
  `lmroman10-regular`, `lmroman10-italic`, `latinmodern-math`, `texgyretermes-regular`,
  `texgyrechorus-mediumitalic`. Verify with `--check-fonts` before assuming a failure is
  a code bug.
- Colors: algebra_2's cover is forest-green-derived where it uses accent; this course is
  navy (`#1F3A5F`). Check whether the palette constants at the top of `cover.py` need a
  course-specific swap.

### Suggested order

Do Part 2 before Part 3 — the cover is a unit-level prefab component, and Part 2 changes
how unit packets are assembled. Building the cover first means wiring it twice.
