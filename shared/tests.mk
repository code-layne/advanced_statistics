# shared/tests.mk — build a unit's summative assessments (blank student copies).
# Included by each unitNN/tests/Makefile (`include ../../shared/tests.mk`).
# Every subdirectory holding a main.tex compiles to target/<unit>/tests/<name>/main.pdf.

PROJECT_ROOT := $(abspath ../..)
UNIT         := $(notdir $(abspath ..))
TEXINPUTS    := $(PROJECT_ROOT)/shared//:
PDF_DIR      := $(PROJECT_ROOT)/target/$(UNIT)/tests
LATEXFLAGS   := -xelatex -interaction=nonstopmode -halt-on-error -file-line-error

TESTS := $(patsubst %/main.tex,%,$(wildcard */main.tex))

# The practice test doubles as the unit "sample test" drop-in: its compiled PDF is
# published to ../sample_test/main.pdf, which shared/unit.mk merges into BOTH the
# student and key packets (the key packet takes sample_test_key when there is one,
# and falls back to sample_test when there is not). The ACTUAL test is never
# published into any packet — it stays out of student hands.
DROP_SRC := practice_test
DROP_DST := ../sample_test/main.pdf

.PHONY: all clean drop $(TESTS)

all: $(TESTS) drop

$(TESTS):
	@mkdir -p $(PDF_DIR)/$@
	cd $@ && TEXINPUTS="$(TEXINPUTS)" latexmk $(LATEXFLAGS) \
	    -outdir="$(PDF_DIR)/$@" main.tex
	@echo "OK  $(UNIT) test -> target/$(UNIT)/tests/$@/main.pdf"

drop: $(DROP_SRC)
	@mkdir -p $(dir $(DROP_DST))
	cp $(PDF_DIR)/$(DROP_SRC)/main.pdf $(DROP_DST)
	@echo "OK  Published practice test -> $(UNIT)/sample_test/main.pdf (student + key packet)"

clean:
	rm -rf $(PDF_DIR)
