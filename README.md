# AP Statistics Curriculum

A LaTeX-based curriculum for AP Statistics, organized by unit and lesson. Includes slides, notes, activities, homework, exit tickets, and answer keys — all built from source into print-ready PDFs.

## Structure

Each lesson lives in `unitXX/lessonYY/`, with one subdirectory per component:

- `cover` (lesson cover sheet)
- `warmup` / `warmup_key`
- `notes` / `notes_key`
- `activity` / `activity_key`
- `exit_ticket` / `exit_ticket_key`
- `homework` / `homework_key`
- `slides` (Beamer deck), plus the lesson plan at the lesson root

## Work products

A lesson builds five files into `target/compiled/unitXX/`:

| File | What it is |
| --- | --- |
| `lessonYY_plan.pdf` | the lesson plan |
| `lessonYY_slides.pdf` | the deck printed — 3 slides per page with a ruled note column |
| `lessonYY_slides.pptx` | the deck projected — one full-page slide image each (Google Slides imports this) |
| `lessonYY_student.pdf` | cover + blank components, numbered packet-wide, components starting on a recto |
| `lessonYY_key.pdf` | the same packet answered, page for page with the student one |

Both slide files come from the one Beamer deck in `slides/main.tex` — edit that and rebuild,
never the products.

Units aggregate the last two into `unitXX_student.pdf` / `unitXX_key.pdf`, renumbered
unit-wide; the root does the same into `curriculum_student.pdf` / `curriculum_key.pdf`.

## Getting the Source

`math-shared/` is a git submodule, [code-layne/math-shared](https://github.com/code-layne/math-shared),
which holds the grading package shared across the courses. It sits at the project root, not under
`shared/`: the build searches `shared/` recursively, and `math-shared/examples` holds `main.tex`
files a component build would pick up. Clone with it:

```bash
git clone --recurse-submodules https://github.com/code-layne/advanced_statistics
```

In a clone made without `--recurse-submodules`, run `git submodule update --init` once. Ordinary
builds still work without the submodule. Only the grading targets below need it.

## Building from Source

Requires [XeLaTeX](https://tug.org/xetex/), `latexmk`, poppler (`pdfunite`, `pdftoppm`,
`pdfinfo`), and Python 3. The `.pptx` writer uses only the standard library.

```bash
make                              # all five products for every lesson
make -C unit01/lesson03 all       # just one lesson
make -C unit01/lesson03 slides    # both slide forms (PDF + PPTX)
make -C unit01 student            # unit01_student.pdf (+ the keys it aligns against)
make student                      # curriculum_student.pdf
make key                          # curriculum_key.pdf
make clean | make distclean
```

Output lands in `target/`: per-component PDFs under `target/unitXX/lessonYY/<comp>/`,
products and packets under `target/compiled/`.

### Grading

The graded components (AP Practice, homework, quizzes and tests) mark each answer with
`\gradedblank` from `math-shared/grading.sty`. Two targets work on one graded component at a time:

```bash
make -C unit01/lesson03 manifest COMP=homework           # blank + key, manifest.json, blank/key check
make -C unit01/lesson03 roster-packets COMP=homework ROSTER=~/Rosters/apstats/roster-map.csv
make -C unit01/tests manifest COMP=actual_test           # unit tests: tests/ (keys in test_keys/)
make -C unit01/quizzes manifest COMP=actual_quiz         # quizzes: quizzes/ (keys in quiz_keys/)
make -C unit01 manifest COMP=lesson03/homework           # the same, from the unit directory
```

`roster-packets` builds one copy of the packet per student, in roster order, into
`target/compiled/`: her name is preprinted on the lesson cover's Name line, and the QR codes and
id strip on graded pages carry only her tracking id. Lesson packets have no separate name sheet.
Tests and quizzes do: their first page is a name cover sheet that is torn off and fed into the
grading system, and is never scanned with the work. The roster
PDFs carry student names on the covers; `target/` is never committed, and `roster-map.csv` lives
outside the repository (see math-shared's README).

## Downloading Prebuilt PDFs

> Coming soon — versioned releases for each unit will be available on the [Releases](../../releases) page.

## License

TBD
