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
#       one personalized copy of COMP per student (QR codes carry her tracking
#       id, the name strip her name), each padded by shared/paginate.sh to an
#       even page count so every copy starts on a fresh sheet, joined in roster
#       order into target/compiled/<unit>/<COMP>_roster.pdf. An assessment is
#       handed out on its own, never inside a lesson packet, so there is no
#       packet to rebuild around it.
#
# Rubric files for unit assessments live in the unit's rubrics/ folder
# (unitNN/rubrics/). grading.mk resolves rubric paths against the directory
# above the component (unitNN/tests/ or unitNN/quizzes/), so a rubric item
# names its file as rubric=../rubrics/<assignment>-<id>.yaml.
#
# Per-student builds carry student names: they stay under target/.
GRADING_MK    := $(PROJECT_ROOT)/math-shared/grading.mk
COMPILED_DIR  ?= $(PROJECT_ROOT)/target/compiled/$(UNIT)
PAGINATE_SH   ?= $(PROJECT_ROOT)/shared/paginate.sh
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

ROSTER_IDS     := $(if $(ROSTER),$(shell $(GRADING_PYTHON) $(GRADING_SCRIPTS)/roster_tex.py \
                    "$(ROSTER)" --ids-only $(if $(SECTION),--section "$(SECTION)")))
ROSTER_PKT_DIR := $(GRADING_OUT)/packets
ROSTER_PACKETS := $(foreach id,$(ROSTER_IDS),$(ROSTER_PKT_DIR)/$(id).pdf)
ROSTER_OUT     := $(COMPILED_DIR)/$(COMP)_roster.pdf

roster-packets: grading-need-comp grading-need-roster
	@test -n "$(strip $(ROSTER_IDS))" || { echo "!  no students in $(ROSTER)"; exit 1; }
	@$(MAKE) --no-print-directory $(ROSTER_PACKETS)
	@mkdir -p $(COMPILED_DIR)
	@if [ $(words $(ROSTER_PACKETS)) -eq 1 ]; then cp $(ROSTER_PACKETS) $(ROSTER_OUT); \
	 else pdfunite $(ROSTER_PACKETS) $(ROSTER_OUT); fi
	@echo "✓  Roster copies  → $(patsubst $(PROJECT_ROOT)/%,%,$(ROSTER_OUT)) ($(words $(ROSTER_IDS)) students, roster order)"

$(ROSTER_PKT_DIR)/%.pdf: grading-personalized
	@mkdir -p $(dir $@)
	@cp $(GR_STUDENTS)/$*.pdf $@
	@TEXINPUTS="$(TEXINPUTS)" $(PAGINATE_SH) $@ $(ROSTER_PKT_DIR)/.paginate-$* $(GR_STUDENTS)/$*.pdf --
else
manifest roster-packets grading-need-comp:
	@echo "!  math-shared is empty — run: git submodule update --init"; exit 1
endif
