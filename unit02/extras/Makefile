# unit02/extras/Makefile — standalone one-off handouts (e.g. the parent-visit activity). Merged
# into NO packet and NOT listed in shared/unit.mk or shared/root.mk (unit.mk globs lesson*/ only),
# so the unit's verified packets never reflow. Every subdirectory holding a main.tex compiles to
# target/<unit>/extras/<name>/main.pdf.

PROJECT_ROOT := $(abspath ../..)
UNIT         := $(notdir $(abspath ..))
TEXINPUTS    := $(PROJECT_ROOT)/shared//:
PDF_DIR      := $(PROJECT_ROOT)/target/$(UNIT)/extras
LATEXFLAGS   := -xelatex -interaction=nonstopmode -halt-on-error -file-line-error

EXTRAS := $(patsubst %/main.tex,%,$(wildcard */main.tex))

.PHONY: all clean $(EXTRAS)
all: $(EXTRAS)
$(EXTRAS):
	@mkdir -p $(PDF_DIR)/$@
	cd $@ && TEXINPUTS="$(TEXINPUTS)" latexmk $(LATEXFLAGS) -outdir="$(PDF_DIR)/$@" main.tex
	@echo "OK  $(UNIT) extras -> target/$(UNIT)/extras/$@/main.pdf"

clean:
	rm -rf $(PDF_DIR)
