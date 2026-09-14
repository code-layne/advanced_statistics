# unit01/quizzes/Makefile — mid-unit quiz documents (blank student copies).
#
# Mirrors shared/tests.mk in spirit: every subdirectory holding a main.tex compiles
# to target/<unit>/quizzes/<name>/main.pdf. It deliberately has NO `drop` rule —
# unlike the unit practice test, nothing here is published into the unit student or
# key packet. The study guide and the sample quiz are handed out on their own, and
# the actual quiz must never reach a packet at all.
PROJECT_ROOT := $(abspath ../..)
UNIT         := $(notdir $(abspath ..))
TEXINPUTS    := $(PROJECT_ROOT)/shared//:
PDF_DIR      := $(PROJECT_ROOT)/target/$(UNIT)/quizzes
LATEXFLAGS   := -xelatex -interaction=nonstopmode -halt-on-error -file-line-error

DOCS := $(patsubst %/main.tex,%,$(wildcard */main.tex))

.PHONY: all clean $(DOCS)

all: $(DOCS)

$(DOCS):
	@mkdir -p $(PDF_DIR)/$@
	cd $@ && TEXINPUTS="$(TEXINPUTS)" latexmk $(LATEXFLAGS) \
	    -outdir="$(PDF_DIR)/$@" main.tex
	@echo "OK  $(UNIT) quiz -> target/$(UNIT)/quizzes/$@/main.pdf"

clean:
	rm -rf $(PDF_DIR)
