# shared/assessment-grading.mk — grading entry points for a unit's assessments.
# Included at the END of shared/tests.mk and of unitNN/quizzes/Makefile, after
# PROJECT_ROOT, UNIT, TEXINPUTS and PDF_DIR are set. The including file sets
# ASSESS_KEYS to the sibling directory that holds each document's key, named
# <name>_key: ../test_keys for tests/, ../quiz_keys for quizzes/.
#
#   make manifest COMP=actual_test
#       blank + key builds, target/<unit>/<dir>/grading/<COMP>/manifest.json,
#       and the check that the blank and key agree on every graded item.
#   make roster-packets COMP=actual_test ROSTER=~/Rosters/apstats/roster-map.csv [SECTION=…]
#       math-shared's grading-personalized, copied to
#       target/compiled/<unit>/<COMP>_roster.pdf: per student, in roster order,
#       her name cover sheet, its blank back, then her copy of COMP (QR codes and
#       the id strip carry only her tracking id) padded to an even page count,
#       so every cover starts on an odd page. An assessment is handed out on its
#       own, never inside a lesson packet, so there is no packet to rebuild
#       around it.
#
# Rubric files for unit assessments live in the unit's rubrics/ folder
# (unitNN/rubrics/). grading.mk resolves rubric paths against the directory
# above the component (unitNN/tests/ or unitNN/quizzes/), so a rubric item
# names its file as rubric=../rubrics/<assignment>-<id>.yaml.
#
# Names are printed only on the cover sheets, which are in the roster PDF: it
# stays under target/.
GRADING_MK    := $(PROJECT_ROOT)/math-shared/grading.mk
COMPILED_DIR  ?= $(PROJECT_ROOT)/target/compiled/$(UNIT)
COMP          ?=
COMPONENT     := $(COMP)
KEY_COMPONENT := $(ASSESS_KEYS)/$(COMP)_key
GRADING_OUT   := $(PDF_DIR)/grading/$(COMP)

.PHONY: manifest roster-packets grading-need-comp

ifneq ($(wildcard $(GRADING_MK)),)
include $(GRADING_MK)

grading-need-comp:
	@test -n "$(COMP)" || { echo "!  set COMP=<assessment directory>, e.g. COMP=actual_test"; exit 1; }

manifest: grading-need-comp
	@$(MAKE) --no-print-directory grading-manifest
	@echo "✓  Manifest       → $(patsubst $(PROJECT_ROOT)/%,%,$(GRADING_OUT))/manifest.json"

ROSTER_OUT := $(COMPILED_DIR)/$(COMP)_roster.pdf

roster-packets: grading-need-comp grading-personalized
	@mkdir -p $(COMPILED_DIR)
	@cp $(GR_OUT)/personalized.pdf $(ROSTER_OUT)
	@echo "✓  Roster copies  → $(patsubst $(PROJECT_ROOT)/%,%,$(ROSTER_OUT)) (roster order, covers first)"
else
manifest roster-packets grading-need-comp:
	@echo "!  math-shared is empty — run: git submodule update --init"; exit 1
endif
