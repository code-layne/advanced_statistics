# Root Makefile — delegates to unit sub-makes and stitches the full curriculum.
#
# Targets:
#   all        build all four work products for every lesson, across all units
#   student    build + merge per-unit student packets, then curriculum_student.pdf
#   key        build + merge per-unit key packets,     then curriculum_key.pdf
#   clean      remove compiled output for all units
#   distclean  clean + remove all build artifacts (target/, .stamps/)
#
# Only the student and key packets aggregate to this level. Each lesson's other
# two products — lessonYY_plan.pdf and lessonYY_slides.pdf — stay in
# target/compiled/unitXX/; they are per-lesson teacher artifacts, not something
# to bind into one document.

COMPILED_DIR := target/compiled

UNITS := $(patsubst %/Makefile,%,$(sort $(wildcard unit*/Makefile)))

.PHONY: all student key full clean distclean $(UNITS)

all: $(UNITS)

$(UNITS):
	$(MAKE) -C $@

student:
	@for u in $(UNITS); do $(MAKE) -C $$u student || exit 1; done
	@mkdir -p $(COMPILED_DIR)
	@pdfs=$$(ls $(COMPILED_DIR)/unit*_student.pdf 2>/dev/null | sort); \
	if [ -n "$$pdfs" ]; then \
	  pdfunite $$pdfs $(COMPILED_DIR)/curriculum_student.pdf; \
	  echo "✓  Curriculum student → target/compiled/curriculum_student.pdf"; \
	fi

key:
	@for u in $(UNITS); do $(MAKE) -C $$u key || exit 1; done
	@mkdir -p $(COMPILED_DIR)
	@pdfs=$$(ls $(COMPILED_DIR)/unit*_key.pdf 2>/dev/null | sort); \
	if [ -n "$$pdfs" ]; then \
	  pdfunite $$pdfs $(COMPILED_DIR)/curriculum_key.pdf; \
	  echo "✓  Curriculum key     → target/compiled/curriculum_key.pdf"; \
	fi

full:
	@echo "!  \`make full\` was removed — the curriculum builds two packets:" >&2
	@echo "     make student  → curriculum_student.pdf" >&2
	@echo "     make key      → curriculum_key.pdf     (replaces \`full\`)" >&2
	@echo "   Lesson plans and decks are now standalone per-lesson products:" >&2
	@echo "     target/compiled/unitXX/lessonYY_plan.pdf" >&2
	@echo "     target/compiled/unitXX/lessonYY_slides.pdf" >&2
	@exit 1

clean:
	@for u in $(UNITS); do $(MAKE) -C $$u clean; done
	rm -f $(COMPILED_DIR)/curriculum_student.pdf $(COMPILED_DIR)/curriculum_key.pdf \
	      $(COMPILED_DIR)/curriculum_full.pdf

distclean: clean
	rm -rf target .stamps
