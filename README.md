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

## Downloading Prebuilt PDFs

> Coming soon — versioned releases for each unit will be available on the [Releases](../../releases) page.

## License

TBD
