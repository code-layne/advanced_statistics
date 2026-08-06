# Migration Plan — Restructure to 8 Units × 8 Lessons

Executes [COURSE_RESTRUCTURE.md](COURSE_RESTRUCTURE.md). Target: 8 units, each with
lessons 0–7 (lesson 0 = "Introducing Statistics" hook), Units 8+9 merged, 16 lesson
pairs condensed to 8, one new lesson (3.7).

## Ground facts that shape the plan

- **Directory names drive everything.** `lesson.mk` derives `LESSON` from the
  directory name; products are `lessonYY_*.pdf`; stamps live under
  `.stamps/unitXX/lessonYY`. Renaming a directory renumbers the products for free.
  New scheme: `lesson00` … `lesson07` (zero-padded → sorts correctly in the
  `lesson*/Makefile` glob).
- **983 `.tex` files contain a `Lesson X.Y` string** (headers, `\pageheader`,
  `\LessonNumberName`, prose cross-references). Old and new numbering overlap
  (old 1.3 exists and new 1.3 exists, meaning different lessons), so the rewrite
  must be **one atomic pass with the full old→new map** — sequential seds would
  double-map.
- **Sample tests are `.gitkeep` placeholders** in every unit — nothing to merge.
- **Binder covers are generated** (`shared/cover.py`) from each unit's
  `lesson*/main.tex` — regenerate after renumbering, don't hand-edit.
- **Slides exist for only 24/80 lessons** (all of U1, U3; most of U2). Slides debt
  is tracked but kept **off the migration's critical path**; merged pairs where only
  one lesson has a deck (2.7+2.8) keep the surviving deck under the new number.

## Phase 0 — Freeze and baseline (½ session)

1. Branch `restructure/8x8` off current `main`; land or explicitly abandon any
   in-flight lesson work first — content PRs racing the renumber will conflict on
   every line.
2. `make distclean` (stamps and `target/` are keyed to old directory names; none
   survive the renumber).
3. Record a baseline: run the full out-of-tree compile scan (CLAUDE.md QA recipe)
   and save the OK/FAIL list. Post-migration scans are diffed against this — the
   migration must not introduce failures, but it also isn't on the hook for
   pre-existing ones.

## Phase 1 — Mechanical renumber, no content changes (1 session, one PR)

Goal: the whole course builds green under the new numbering, with merge-source
lessons parked out of the build. **No pedagogical content changes in this PR** — it
should be reviewable as "moves + number rewrites + green build".

1. **Move directories** per the map in COURSE_RESTRUCTURE.md (script in Appendix A).
   Every kept lesson moves to a strictly lower number, so processing each unit in
   ascending order gives collision-free `git mv`. Merge-**secondaries** park in
   `unitXX/_merge_src/<old-number>/` — the name deliberately fails the
   `lesson*/Makefile` glob, so parked lessons drop out of packets and unit builds
   while their sources stay in-tree for Phase 2. Delete parked `Makefile`s.
2. **Dissolve unit09**: `git mv` 9.2→`unit08/lesson05`, 9.4→`unit08/lesson06`;
   park 9.1, 9.3, 9.5, 9.6 in `unit08/_merge_src/`; delete the unit09 shell
   (Makefile, `unit_cover`, `binder_cover`, sample-test placeholders).
3. **Rewrite numbering in one pass** (Appendix B): a Python script applying the
   full old→new map to every `.tex` file — `%!` header comments,
   `\UnitNumberName`, `\LessonNumberName`, `\pageheader{...}`, and prose
   `Lesson X.Y` / `Unit 9` references. Regex must try two-digit minors first
   (`4.10` before `4.1`) and bound the match (`\b`). Unmapped hits are printed,
   not guessed — each is reviewed by hand.
   - Prose references **to a merge-secondary** (e.g. "recall Lesson 6.5") map to
     the merged lesson's new number and are also logged to a review list — after
     Phase 2 the referenced content may sit in a differently-shaped lesson.
4. **Rewrite unit covers**: new lesson tables (0–7) per COURSE_RESTRUCTURE.md;
   merged rows carry the merged title; unit08 cover gets the combined
   "Distributions and Relationships" overview. Update root `README.md` and
   `COURSE_OUTLINE.md`.
5. **Regenerate binder covers**: `make -C unitXX clean_unit_cover` for all eight
   units (cover.py re-reads the renamed lesson sources; parked `_merge_src` dirs
   are invisible to its `lesson*/main.tex` glob).
6. **Gate** (must all pass before the PR):
   - full out-of-tree compile scan — zero new failures vs. Phase 0 baseline
   - `make student && make key` — all eight unit packets and both curriculum
     packets build
   - `pdfinfo` page parity: every component count == its key's
   - `pdftoppm` one-page check on every warmup and exit ticket
   - sweeps come back empty:
     `grep -rn "Unit 9" --include="*.tex" unit0*` and, excluding `_merge_src/`,
     `grep -rn "Lesson 9\." --include="*.tex" unit0*`, plus a script pass
     verifying no old-only numbers (e.g. `4.12`, `6.11`, `1.10`) survive outside
     `_merge_src`.

After this PR the course is **teachable under the new numbering**: merged slots
temporarily contain only the primary lesson's content; nothing is lost (secondaries
are parked in-tree).

## Phase 2 — Author the merged lessons (the long phase; one PR per unit)

Eight merges, worked unit by unit. Suggested order — easiest first to shake out the
process, hardest content last:

| PR | Unit | Merges | Notes |
| --- | --- | --- | --- |
| 2a | U1 | 1.3+1.4 → 1.2, 1.8+1.9 → 1.6 | Both decks exist — merge slides too |
| 2b | U2 | 2.7+2.8 → 2.6 | 2.8 had no deck; extend 2.7's |
| 2c | U7 | 7.6+7.7 → 7.5, 7.8+7.9 → 7.6 | CI/justify and setup/carry patterns |
| 2d | U6 | 6.5+6.6 → 6.4, 6.8+6.9 → 6.6, 6.10+6.11 → 6.7 | Heaviest inference unit |
| 2e | U4 | 4.3+4.4 → 4.2, 4.5+4.6 → 4.3, 4.8+4.9 → 4.5, 4.10+4.11 → 4.6 | Most merges; probability sequencing is delicate |
| 2f | U8 | 8.4+8.5 → 8.3, 9.2+9.3 → 8.5, 9.4+9.5 → 8.6, 8.7+9.6 → 8.7, 9.1 hook → 8.0 | Plus unit-identity work (Phase 3) |
| 2g | U3 | new 3.7 Skills Focus | Scaffold with `new_lesson.py`; author from scratch |

Per-merge procedure (per lesson-planning skill + CLAUDE.md conventions):

1. Read both parked sources; draft the merged lesson plan (objectives, timing —
   one class period, not two).
2. Author merged components **to a single lesson's page budget**: one-page warmup
   and exit ticket (max 3 questions), condensed notes/activity/homework. This is
   selection and rewriting, not concatenation — expect to cut ~40% of the pair's
   combined exercises, keeping the best-discriminating items.
3. Work rule: `work` blocks byte-identical between blank and `_key`; `\boxguard`
   before breakable boxes; teacher notes to the plan, never the key; `\ans{}`
   rules; run the Rule-7 grep on every key before building.
4. Merge or extend the deck where one exists; slide debt for deckless lessons is
   logged, not blocked on.
5. Delete the pair's `_merge_src/` entries **in the same commit** that lands the
   merged lesson — parked dirs must not outlive their merge.
6. Unit gate before each PR: unit compile scan, `make -C unitXX student key`,
   pdftoppm one-pagers, pdfinfo parity, then delete stale stamps.

Parallel dispatch (CLAUDE.md multi-lesson rules) fits Phase 2e/2f: coordinator
scaffolds, one Write-only subagent per merged lesson, coordinator builds and QAs.

## Phase 3 — Unit 8 identity (folded into PR 2f)

- **8.0**: old 8.1's hook, widened with 9.1's "Do Those Points Align?" scatterplot
  motivation — the unit now asks one question ("is this pattern real?") over both
  chi-square and slope contexts.
- **8.7**: single course-wide procedure-selection capstone from old 8.7 + 9.6 —
  the flowchart now spans every procedure in the course.
- Unit 8 cover, overview, and binder cover redrawn (`clean_unit_cover` after
  content lands).

## Phase 4 — Follow-on debt (tracked, not in the migration)

Logged as issues/spawned tasks, explicitly out of scope here:

- **Slide decks for the 40 deckless lessons** (Units 4–8 after restructure) —
  per current policy, missing decks are authored at review time.
- **Sample tests** — still placeholders in every unit; the merged Unit 8 needs one
  spanning chi-square + slopes when tests are authored.
- Unit 1 open items (`UNIT01_OPEN_ITEMS.md`) — unaffected by renumbering except
  lesson references inside that doc, which Phase 1's sweep updates.

## Phase 5 — Final QA and release (½ session, final PR)

1. Full course build from clean: `make distclean && make && make student && make key`.
2. Full compile scan — zero failures (baseline failures must be resolved or
   explicitly carried).
3. Course-wide checks: every warmup/exit-ticket one page; every blank/key page
   count equal; `_merge_src` directories gone; stale-number sweep empty.
4. Update `COURSE_OUTLINE.md` to describe the new structure as current; retire
   `COURSE_RESTRUCTURE.md`'s mapping table into it; delete this plan or mark done.
5. Print-order sanity pass: open `curriculum_student.pdf` and spot-check unit
   boundaries, binder covers, recto starts.

## Risks and mitigations

| Risk | Mitigation |
| --- | --- |
| Double-mapping during renumber (old 1.3 → new 1.2 while new 1.3 also exists) | Single-pass script with full map (Appendix B); never sequential seds |
| `4.1` matching inside `4.10`/`4.11`/`4.12` | Longest-alternative-first regex with `\b` boundary |
| Parked lessons leaking into packets | `_merge_src/` fails the `lesson*/Makefile` glob; gate greps confirm |
| Merged lesson silently breaks blank/key parity | `work`-rule authoring + pdfinfo gate every PR |
| Prose refs pointing at content that moved *within* a merge | Phase 1 logs every remapped reference-to-secondary for Phase 2 review |
| Stale stamps building old artifacts | `make distclean` at Phase 0; stamp deletion in every unit gate |
| Mid-migration teaching need | Phase 1 leaves the course fully buildable; every Phase 2 PR leaves it green |

## Effort estimate

| Phase | Sessions |
| --- | --- |
| 0 + 1 (freeze, renumber, green build) | 1–1.5 |
| 2a–2g (8 merges + 1 new lesson, unit gates) | 5–7 |
| 3 (inside 2f) | — |
| 5 (final QA) | 0.5 |
| **Total** | **~7–9 sessions** |

---

## Appendix A — Directory move script (Phase 1)

Run from the repo root on a clean tree. Ascending order per unit; all kept targets
are strictly lower numbers, so no collisions. Verify with `git status` after.

```bash
set -e
park() { mkdir -p "$1/_merge_src"; git mv "$2" "$1/_merge_src/$3"; git rm -q "$1/_merge_src/$3/Makefile" || true; }

# Unit 1: 1.3+1.4→1.2, 1.8+1.9→1.6
git mv unit01/lesson01 unit01/lesson00
git mv unit01/lesson02 unit01/lesson01
git mv unit01/lesson03 unit01/lesson02
park  unit01 unit01/lesson04 old-1.4
git mv unit01/lesson05 unit01/lesson03
git mv unit01/lesson06 unit01/lesson04
git mv unit01/lesson07 unit01/lesson05
git mv unit01/lesson08 unit01/lesson06
park  unit01 unit01/lesson09 old-1.9
git mv unit01/lesson10 unit01/lesson07

# Unit 2: 2.7+2.8→2.6
git mv unit02/lesson01 unit02/lesson00
git mv unit02/lesson02 unit02/lesson01
git mv unit02/lesson03 unit02/lesson02
git mv unit02/lesson04 unit02/lesson03
git mv unit02/lesson05 unit02/lesson04
git mv unit02/lesson06 unit02/lesson05
git mv unit02/lesson07 unit02/lesson06
park  unit02 unit02/lesson08 old-2.8
git mv unit02/lesson09 unit02/lesson07

# Unit 3: pure shift; new lesson07 scaffolded in Phase 2g
for i in 1 2 3 4 5 6 7; do git mv unit03/lesson0$i unit03/lesson0$((i-1)); done

# Unit 4: 4.3+4.4→4.2, 4.5+4.6→4.3, 4.8+4.9→4.5, 4.10+4.11→4.6
git mv unit04/lesson01 unit04/lesson00
git mv unit04/lesson02 unit04/lesson01
git mv unit04/lesson03 unit04/lesson02
park  unit04 unit04/lesson04 old-4.4
git mv unit04/lesson05 unit04/lesson03
park  unit04 unit04/lesson06 old-4.6
git mv unit04/lesson07 unit04/lesson04
git mv unit04/lesson08 unit04/lesson05
park  unit04 unit04/lesson09 old-4.9
git mv unit04/lesson10 unit04/lesson06
park  unit04 unit04/lesson11 old-4.11
git mv unit04/lesson12 unit04/lesson07

# Unit 5: pure shift
for i in 1 2 3 4 5 6 7 8; do git mv unit05/lesson0$i unit05/lesson0$((i-1)); done

# Unit 6: 6.5+6.6→6.4, 6.8+6.9→6.6, 6.10+6.11→6.7
git mv unit06/lesson01 unit06/lesson00
git mv unit06/lesson02 unit06/lesson01
git mv unit06/lesson03 unit06/lesson02
git mv unit06/lesson04 unit06/lesson03
git mv unit06/lesson05 unit06/lesson04
park  unit06 unit06/lesson06 old-6.6
git mv unit06/lesson07 unit06/lesson05
git mv unit06/lesson08 unit06/lesson06
park  unit06 unit06/lesson09 old-6.9
git mv unit06/lesson10 unit06/lesson07
park  unit06 unit06/lesson11 old-6.11

# Unit 7: 7.6+7.7→7.5, 7.8+7.9→7.6
git mv unit07/lesson01 unit07/lesson00
git mv unit07/lesson02 unit07/lesson01
git mv unit07/lesson03 unit07/lesson02
git mv unit07/lesson04 unit07/lesson03
git mv unit07/lesson05 unit07/lesson04
git mv unit07/lesson06 unit07/lesson05
park  unit07 unit07/lesson07 old-7.7
git mv unit07/lesson08 unit07/lesson06
park  unit07 unit07/lesson09 old-7.9
git mv unit07/lesson10 unit07/lesson07

# Unit 8: 8.4+8.5→8.3; 8.7 stays lesson07 (merges with 9.6 in Phase 2)
git mv unit08/lesson01 unit08/lesson00
git mv unit08/lesson02 unit08/lesson01
git mv unit08/lesson03 unit08/lesson02
git mv unit08/lesson04 unit08/lesson03
park  unit08 unit08/lesson05 old-8.5
git mv unit08/lesson06 unit08/lesson04

# Unit 9 → Unit 8: 9.2+9.3→8.5, 9.4+9.5→8.6, 9.1→8.0 hook, 9.6→8.7 capstone
park  unit08 unit09/lesson01 old-9.1
git mv unit09/lesson02 unit08/lesson05
park  unit08 unit09/lesson03 old-9.3
git mv unit09/lesson04 unit08/lesson06
park  unit08 unit09/lesson05 old-9.5
park  unit08 unit09/lesson06 old-9.6
git rm -r unit09
```

## Appendix B — Renumber-rewrite script sketch (Phase 1)

One pass, full map, longest-match-first. Also matches `%!` comments,
`\pageheader{Unit X, Lesson X.Y}`, and bare `Unit 9` → `Unit 8`.

```python
# scratch script — run once, review its report, commit alongside the moves
import re, pathlib

MAP = {  # old display number -> new display number (secondaries -> merged slot)
  "1.1":"1.0","1.2":"1.1","1.3":"1.2","1.4":"1.2","1.5":"1.3","1.6":"1.4",
  "1.7":"1.5","1.8":"1.6","1.9":"1.6","1.10":"1.7",
  "2.1":"2.0","2.2":"2.1","2.3":"2.2","2.4":"2.3","2.5":"2.4","2.6":"2.5",
  "2.7":"2.6","2.8":"2.6","2.9":"2.7",
  "3.1":"3.0","3.2":"3.1","3.3":"3.2","3.4":"3.3","3.5":"3.4","3.6":"3.5","3.7":"3.6",
  "4.1":"4.0","4.2":"4.1","4.3":"4.2","4.4":"4.2","4.5":"4.3","4.6":"4.3",
  "4.7":"4.4","4.8":"4.5","4.9":"4.5","4.10":"4.6","4.11":"4.6","4.12":"4.7",
  "5.1":"5.0","5.2":"5.1","5.3":"5.2","5.4":"5.3","5.5":"5.4","5.6":"5.5",
  "5.7":"5.6","5.8":"5.7",
  "6.1":"6.0","6.2":"6.1","6.3":"6.2","6.4":"6.3","6.5":"6.4","6.6":"6.4",
  "6.7":"6.5","6.8":"6.6","6.9":"6.6","6.10":"6.7","6.11":"6.7",
  "7.1":"7.0","7.2":"7.1","7.3":"7.2","7.4":"7.3","7.5":"7.4","7.6":"7.5",
  "7.7":"7.5","7.8":"7.6","7.9":"7.6","7.10":"7.7",
  "8.1":"8.0","8.2":"8.1","8.3":"8.2","8.4":"8.3","8.5":"8.3","8.6":"8.4","8.7":"8.7",
  "9.1":"8.0","9.2":"8.5","9.3":"8.5","9.4":"8.6","9.5":"8.6","9.6":"8.7",
}
SECONDARIES = {"1.4","1.9","2.8","4.4","4.6","4.9","4.11","6.6","6.9","6.11",
               "7.7","7.9","8.5","9.1","9.3","9.5","9.6"}
# longest first so 4.10 wins over 4.1
alts = "|".join(sorted((k.replace(".", r"\.") for k in MAP), key=len, reverse=True))
pat = re.compile(rf"\b(Lesson[s]?~?\s+)({alts})\b")

review = []
for f in pathlib.Path(".").glob("unit0*/**/*.tex"):
    if "_merge_src" in f.parts: continue
    src = f.read_text()
    def sub(m):
        if m.group(2) in SECONDARIES: review.append((f, m.group(0)))
        return m.group(1) + MAP[m.group(2)]
    out = pat.sub(sub, src)
    out = re.sub(r"\bUnit 9\b", "Unit 8", out)
    if out != src: f.write_text(out)

for f, hit in review: print("REVIEW (ref to merge-secondary):", f, hit)
```

The script's REVIEW list is the Phase 2 checklist of cross-references whose target
content is moving inside a merge. `\pageheader`, `\UnitNumberName`, `%!` headers,
and unit-cover tables use the same `Lesson X.Y` / `Unit N` forms and are caught by
the same pass; anything the report shows as unmatched is fixed by hand.
```
