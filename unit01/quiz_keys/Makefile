# unit01/quiz_keys/Makefile — answer keys for the mid-unit quiz documents.
#
# Mirrors shared/test_keys.mk in spirit: every subdirectory holding a main.tex compiles
# to target/<unit>/quiz_keys/<name>/main.pdf. It deliberately has NO `drop` rule —
# unlike the unit practice test, nothing here is published into the unit student or
# key packet. Each key here is page-for-page with its blank in ../quizzes/, and
# the actual quiz key never leaves the teacher.
PROJECT_ROOT := $(abspath ../..)
UNIT         := $(notdir $(abspath ..))
TEXINPUTS    := $(PROJECT_ROOT)/shared//:
PDF_DIR      := $(PROJECT_ROOT)/target/$(UNIT)/quiz_keys
LATEXFLAGS   := -xelatex -interaction=nonstopmode -halt-on-error -file-line-error

DOCS := $(patsubst %/main.tex,%,$(wildcard */main.tex))

.PHONY: all clean $(DOCS)

all: $(DOCS)

$(DOCS):
	@mkdir -p $(PDF_DIR)/$@
	cd $@ && TEXINPUTS="$(TEXINPUTS)" latexmk $(LATEXFLAGS) \
	    -outdir="$(PDF_DIR)/$@" main.tex
	@echo "OK  $(UNIT) quiz key -> target/$(UNIT)/quiz_keys/$@/main.pdf"

clean:
	rm -rf $(PDF_DIR)
