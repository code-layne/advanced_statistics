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

## Part 2 — Done: five work products per lesson

The `student` + `full` pair is replaced by **five** per-lesson products in
`target/compiled/unitXX/` — full parity with algebra_2:

| File | What it is |
| --- | --- |
| `lessonYY_plan.pdf` | the lesson plan — the lesson-root `main.tex`, compiled |
| `lessonYY_slides.pdf` | the deck **printed**: 3 slides per page, ruled note column beside each |
| `lessonYY_slides.pptx` | the deck **projected**: one full-bleed page image per slide |
| `lessonYY_student.pdf` | cover + blank components, paginated packet-wide |
| `lessonYY_key.pdf` | the same packet answered, **page for page** with the student one |

`full` is gone at all three levels and **fails loudly** with a message naming its
replacement. The plan and the deck are standalone deliverables instead of being buried in
a teacher packet.

### Slides policy (set 2026-07-30)

**Every lesson ships its deck in both forms — pptx to project, 3-up PDF to print.** Layne
had previously prohibited PowerPoint generation in this project and **explicitly
rescinded that**, so `shared/pdf2pptx.py` came over after all. Earlier drafts of this file
listed the pptx as "explicitly NOT ported"; that is no longer true.

The raw one-slide-per-page PDF is **not** a product any more — Google Slides imports
`.pptx` natively, so the pptx covers the import path it used to serve. It remains the
source of truth at `target/unitXX/lessonYY/slides/main.pdf`. `make slides` builds both
forms; `make pptx` builds just the pptx.

`shared/pdf2pptx.py` is **stdlib + poppler only** — it rasterizes with `pdftoppm` and
writes the OOXML package with `zipfile`. No LibreOffice, no `python-pptx`, no install
step. The ban on a *Node* step, from `UNIT_PACKET_REFACTOR_NOTES.md`, still stands.

**Consequence: every lesson now owes a deck.** `slides` is in `new_lesson.py`'s defaults,
and the skill's Retrofit section treats a missing deck as something to fix during review.

### The design question — resolved

**Pagination is owned by the lesson level, via the overlay.** The wrapper `.tex` approach
is retired.

Rationale: the overlay works from discovered component PDFs, so it needs no per-lesson or
per-unit source file across 80 lessons; it handles prefab PDFs identically; and it is the
only one of the two that can enforce student/key page-for-page alignment, which is the
defining property of the key product. The wrappers also only ever covered unit01 — units
02–09 silently fell back to `pdfunite`, so the course was numbering its packets two
different ways.

**Unit packets re-run the same pass** over the merged unit packet. The overlay is
idempotent — the white band covers whatever number is already on the page — so a unit
packet built from already-paginated lesson packets renumbers cleanly, unit-wide, with no
double numbering. This gives all nine units the continuous numbering that only unit01 had.

**Recto starts: adopted** (user decision). Every component opens on a right-hand page;
blank versos are inserted and numbered. The slot rule is
`ceil_even(max(blank pages, key pages))` — the `max` gives student/key alignment, the
`ceil_even` gives the recto start. The unit pass pairs
`[unit_cover, lesson*_student, sample_test]` against
`[unit_cover, lesson*_key, sample_test_key]`, so unit packets are recto-correct and
page-for-page end to end, which algebra_2's are not.

### What landed

| File | State |
| --- | --- |
| `shared/paginate.tex` | new — ported; band geometry re-measured against `apstats-article.sty` |
| `shared/paginate.sh` | new — the slot arithmetic, factored out so `lesson.mk` and `unit.mk` share it |
| `shared/handout.tex` | new — ported, `algebra2-colors` → `apstats-colors` |
| `shared/pdf2pptx.py` | new — ported verbatim bar one metadata string (`algebra2 build` → `apstats build`) |
| `shared/lesson.mk` | rewritten — `all plan slides pptx student key`, `full` errors |
| `shared/unit.mk` | rewritten — `student key`, unit-wide paginate pass, `full` errors |
| `Makefile` | rewritten — `student key`, `full` errors |

Deleted: `unit01/unit01_student.tex`, `unit01/unit01_full.tex`, and the unreferenced
`unit01/lesson01/lesson01_{student,full}.tex` (bare `\input` lists, no preamble, no
Makefile ever read them).

Docs updated: the skill's `references/build.md` and SKILL.md Steps 5 / 1b / Retrofit,
`UNIT_PACKET_REFACTOR_NOTES.md` (now marked superseded), and `new_lesson.py` — `slides` is
in `DEFAULT_COMPONENTS` now that the deck feeds a product.

### Two things to know when authoring

- **A lesson's `student` and `key` each compile every component of both packets** (slots are
  sized against the counterpart) **but each emits only its own packet.** `make student` on a
  clean lesson gives no `lessonYY_key.pdf` — use `make all`. Verified that building them
  separately still yields identical page counts, so alignment does not depend on build order.
  At the *unit* level both targets do build both lesson packets, since the unit pass needs
  the real PDFs on both sides.
- **The pass pads a page-count mismatch instead of reporting it.** A key that runs one page
  longer than its blank still yields two equal-length packets — the student one just gains
  a blank verso. So the work rule is *silently* violated. Check the compiled components
  under `target/unitXX/lessonYY/<comp>/main.pdf`, never the packets.

### Backlog

- **57 of 80 lessons have no `slides/main.tex`**, so they build three products, not five.
  `make slides` prints `(no slides in …)` and moves on. Per Layne (2026-07-30), those decks
  **get authored during the lesson review pass**, alongside the convention retrofits — not
  as a bulk sweep. The skill's Retrofit section carries this as a named `deck` convention.

---

## Part 3 — Done: binder covers

Shipped 2026-07-30. All nine units generate; `binder_cover/main.pdf` is committed.
Two decisions taken with Layne before coding: the art is **figure-led** (statistics
displays carry the page, equations support), and covers are **committed artifacts**
as in algebra_2.

### What the reconnaissance got wrong

The inventory in "Reconnaissance done" below counted **prose mentions, not figures**.
Corrected, by actually drawn TikZ:

| Claimed | Actual |
| --- | --- |
| regression/LSRL 121, scatterplots 83, histograms 69, dotplots 58, boxplots 43 | ~40 drawn figures in the whole course, most of them the navy banner on cover sheets; only unit01 L8/L10 and unit02 L4/L7 hold real plots |

So scanning TikZ would have yielded almost nothing either. **The discoverable
primitive in this course is the dataset**, not the equation and not the figure:
88 numeric table rows plus 21 comma lists. `discover()` reads the numbers and the
builders draw the display. Three things had to be true before that worked:

- the tables are **`tabularx`**, not `tabular` — matching only the latter found one
  table in unit02 and zero pairs, so the two-variable unit drew no scatterplot;
- a tabular yielding exactly two equal-length numeric rows is **bivariate** — that
  is how the course lays paired data out, one variable per row;
- adjacent pairs are the notes' worked example and the homework's echo of it, so the
  two scatters are taken from **opposite ends** of the unit or they draw as the same
  picture.

### Two units the notes did not anticipate

**Unit 3 has no mathematics at all.** Its student components contain five distinct
inline math fragments, all of them typographic (`$\to$`, `$\times$`, `$\ldots$`).
It is a study-design unit. `cover.py` now sets the title block on a clean sheet and
says so on stderr rather than failing the build — a unit with nothing to draw is not
an error, and inventing statistics it never taught would violate the file's own rule
that nothing is invented. **Unit 3 wants a hand-tuned `spec.py`**, and the art it
needs (sampling frames, random assignment to treatment groups) is builders that do
not exist yet.

**Units 5 and 9 are thin** (4 and 2 elements). Not a scanner bug: this course states
its formulas *with blanks in them* — it is a workbook — and `_HOLE` correctly rejects
those. There is no display-math reservoir to fall back on; `\[…\]` is essentially
unused. They also want hand-tuned specs.

### Bugs found and fixed on the way

- `\def\UnitNumberName` — as predicted. Regex widened to accept both forms **and**
  unit01's ten plans normalised to `\newcommand`. Both, as the notes asked.
- **`"quiz scores"` matched `z\s*-?\s*score`**, so unit03 — which never mentions the
  normal model — was getting a normal curve. Needed `\b` before the `z`.
- The equation path let through three junk classes the notes only half-named: a
  leading `=`, a trailing `=`, and `symbol = number` scenario settings. Added a
  fourth filter the notes did not anticipate — **shape dedupe**, which collapses
  `H_0: p = 0.30 / 0.40 / 0.45 / 0.60` to one. Unit 9 was otherwise six `t^* = …`.

### The navy question — resolved, no

`cover.py`'s palette is eight neutral grays; there is no forest-green accent to swap.
Introducing `#1F3A5F` would put colored ink on a page whose whole premise is
grayscale line work. Kept gray.

### Ink coverage

Measured on the 150 dpi raster, not on paper — **a real print check is still owed**.
Every cover is lighter than the algebra_2 covers already in use: 2.3–4.0% of pixels
inked against their 6.0–6.2%, mean gray ~251 against ~250.

### Open question: does the binder cover get a page number?

It currently does. The cover leads both packet lists, so the pagination pass numbers
its two sheets 1 and 2, and the unit overview becomes page 3 — every page number in
the course shifts by two. Arguably right (it is a sheet of the packet) and arguably
wrong (it goes in a binder sleeve and is not part of the reading sequence). Making it
unnumbered means teaching `paginate.sh`/`paginate.tex` to hold an unnumbered head
before restarting the count — perhaps 15 lines across the two files, but it changes
pagination semantics for lesson packets too. **Not decided; left as-is.**

### What landed

| File | State |
| --- | --- |
| `shared/cover.py` | new — ported; `COURSE`, widened unit-name regex, 5 statistics builders, dataset discovery, 4 equation filters, empty-unit fallback |
| `shared/unit.mk` | `binder_cover` as a generated prefab, leading **both** packet lists; `clean_unit_cover` |
| `.gitignore` | `!**/binder_cover/main.pdf` negates the blanket `**/*.pdf`; `**/__pycache__` added |
| `unit01/lesson*/main.tex` | ten plans normalised `\def` → `\newcommand` |
| `unit0*/binder_cover/main.pdf` | nine committed covers |

Verified: unit05 builds a 114-page student packet and a 114-page key, page for page,
with the cover leading both; `clean_unit_cover` redraws and a second `make` does not.

### Part 3a — context scenes (2026-07-30, Layne's request)

The covers now also draw **the situations the unit's problems are set in**. A dataset
is always about something, and a student recognises "sleep vs. reaction time" long
before they recognise a scatterplot. A `scene` element is a sheet of graph paper
carrying line art of the situation as a watermark, with the display for that dataset
drawn on top and the variable named underneath. **Ink budget suspended for these**
per Layne.

- 21 scenes, keyed to the contexts the course actually uses: sleep, commuting,
  reaction/wait time, study time, free throws, archery, plant growth, prices,
  battery life, rainfall, weights, vitamin C, salmon, clinical trials, temperature,
  social media, voter turnout, test scores, chance, caffeine, quality control.
- Displays are now **captioned with the row label** that sits on the data —
  "Sleep (hr) vs. RT (ms)", "Distance vs. Rent" — via `_row_label`.
- A unit that names a context but tabulates no numbers for it gets the scene alone.
  **This is what finally gave Unit 3 a cover**: 4 scenes where it had nothing.

**Keyword matching needs word boundaries, and the failure is always silent.** Two
more of the same bug class as `quiz scores`/`z score`:

| Pattern | Fired on | Hits |
| --- | --- | --- |
| `arch(?:er|ery)` | **rese*arch*er** | 214 → 8 after `\b` |
| `degrees` | **degrees of freedom** | 25, all wrong — dropped |

`shared/`-adjacent probe scripts print every matched substring with its count; run
that before trusting a new keyword. Also added: contingency tables and probability
distributions are skipped (they announce themselves with a `Total` margin or a
`P(X = x)` row) — Unit 4 was dotplotting "Sports"/"Arts/Music"/"Neither" as if the
category counts were a sample.

`auto_place` no longer falls back to random placement when it cannot fit an element;
it **drops it**. The old fallback stacked panels precisely when the page was full,
which is how two scene captions ended up overprinted.

Ink, measured as before: 10.4–21.7% of pixels inked, up from 2.3–4.0%. But **% dark
is unchanged** (1.25–1.75 against 1.24–1.74) and mean gray moved 251 → 249 — the
paper tint is `#f4f7fb` and its rules `#cfdcea`, so almost every new "inked" pixel is
nearly white. Real toner cost should be close to flat, but that is still a raster
measurement, not a print.

### Backlog

- Hand-tuned `spec.py` for units **5 and 9**, still thin (7 and 5 elements). Unit 3
  is now carried by scenes.
- The page-number question above.
- A real printed proof before these go to a class set — more relevant now that the
  covers carry a tinted panel.

---

## Part 3 — original plan (superseded by the section above)

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

### Wiring, now that Part 2 has landed

`binder_cover/` is a prefab-PDF component like `sample_test/`, with one difference: its
`main.pdf` is *generated*.

Add `binder_cover` to `shared/unit.mk` as a generated prefab, then put it at the **head of
both packet lists** — in the `unit_lesson_lists` variable, ahead of `$(UNIT_COVER_PDF)` in
`student_list` and `key_list` alike. It must appear in both so the alignment pass keeps
them paired; it is the same two-page sheet in each, so it takes a slot of 2 and nothing
downstream shifts.

Mirror algebra_2's rule shape: `$(BINDER_COVER_SRC)` has **no prerequisites on purpose**
(jitter makes a redraw byte-different every time, so dependency-tracking it would churn
the repo on every build), with `make -C unitXX clean_unit_cover` as the explicit redraw
escape hatch.

### Reconnaissance done 2026-07-30 — read this before starting

**Environment is clear.** `python3 shared/cover.py --check-fonts` against algebra_2's copy
reports `all cover fonts present` and `cairosvg present` on this machine. Font installation
is *not* a task; if a run fails, it is a code bug.

**One hard blocker, and it fails silently.** `cover.py`'s `_UNIT_NAME_RE` matches only
`\newcommand{\UnitNumberName}{...}`. Units 02–09 use exactly that. **Unit 1 uses
`\def\UnitNumberName{...}` in all ten of its lesson plans**, so `unit_metadata()` finds
nothing and falls back to `title or unit_dir.name` — unit01's cover would be titled
"unit01" rather than "Exploring One-Variable Data", with no error. Fix by widening the
regex to accept both forms (more robust) *and* normalising unit01 to `\newcommand` (more
consistent). Do both. The `\quad` suffix and the `Unit N:` prefix are already stripped by
`unit_metadata`, so those need no work.

**Auto-discovery will produce near-empty covers as written.** Measured against this
course's sources:

| `cover.py` looks for | This course has |
| --- | --- |
| `f(x) = …` / `y = …` definitions → `graph` | essentially none — **0 graphs discovered** |
| `\begin{work}` blocks → `slab` | **0 files** use `work` yet (Part 1 backlog) |
| `\numline` or `\draw[<->` → `numberline` | 52 files have axis-ish TikZ, but stats number lines are not solution sets |
| inline `$…$` containing `=` → `equation` | plentiful, but heavily polluted: `$Q_1 = $`, `$\bar{x} = \dfrac{…}{5} = \blank{2cm}$`, `$= \blank{2cm}$` |

So every unit falls through to a pile of low-quality loose equations. `_HOLE` already drops
anything containing `\blank`, which removes many of them and leaves the page thin.

**What the course actually has to draw from**, by file count across all nine units:
regression/LSRL 121, scatterplots 83, histograms 69, dotplots 58, boxplots 43, normal
curves 9. That is the real inventory — the work is new `BUILDERS` entries for those forms
plus a scanner that recognises them, not tuning the existing algebra builders.

Keep unchanged: the **ink budget** (white background, no solid fills, line work in
`#5f5f5f`–`#c9c9c9`, `#ffffff` fills for occlusion only) — these print on a school printer.
Also check whether the accent constants need a navy (`#1F3A5F`) swap; algebra_2's are
forest-green-derived.

### Suggested sequencing

1. Port `cover.py`, fix the `\def` regex, normalise unit01, and confirm a unit with good
   metadata (say unit05) renders *something* end to end. Prove the pipeline before
   touching discovery.
2. Add statistics `BUILDERS` — dotplot and boxplot first (simplest geometry, 101 files
   between them), then histogram, scatter+LSRL, normal curve.
3. Extend `discover()` to recognise those TikZ idioms and to reject the `\blank`/trailing-`=`
   fragments the current equation path lets through.
4. Wire into `unit.mk`, generate all nine, and check ink coverage on a real printer before
   committing the PDFs.
