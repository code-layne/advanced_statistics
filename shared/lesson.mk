# shared/lesson.mk — included by every lesson-level Makefile.
# Auto-detects PROJECT_ROOT, UNIT, and LESSON from CURDIR.
#
# A lesson builds FIVE work products into target/compiled/$(UNIT)/:
#   lessonYY_plan.pdf     the teacher-facing lesson plan (the lesson-root main.tex)
#   lessonYY_slides.pdf   the deck PRINTED: three slides per page in a two-column
#                         layout, each with a ruled note area beside it
#   lessonYY_slides.pptx  the same deck wrapped for PowerPoint, full-page (one
#                         page image per slide) — the projected form
#   lessonYY_student.pdf  cover + blank components, paginated packet-wide
#   lessonYY_key.pdf      the same packet answered, page for page with the
#                         student one
#
# The two slide products are the deck's two forms: the PDF is what you print and
# hand out, the PPTX is what you project (and what Google Slides imports — it
# reads .pptx natively). Both come from the one Beamer deck compiled at
# target/$(UNIT)/$(LESSON)/slides/main.pdf, which is the source of truth —
# never edit either product, edit slides/main.tex and rebuild.
#
# `make slides` builds both. The plan and the deck are standalone deliverables;
# there is no longer a combined `full` teacher packet burying them behind the
# keys.
#
# A component subdirectory may provide EITHER:
#   - main.tex  → compiled with latexmk to target/.../<comp>/main.pdf, or
#   - main.pdf  → a prefab PDF, used as-is straight from the source tree.
# Either form is discovered and merged into the packet by pdfunite.

PROJECT_ROOT := $(abspath ../..)
UNIT         := $(notdir $(abspath ..))
LESSON       := $(notdir $(CURDIR))

SHARED_STYS  := $(wildcard $(PROJECT_ROOT)/shared/*.sty)
# TeX search path: the course packages (recursive), then math-shared (the
# submodule at the project root, for grading.sty). math-shared is listed
# NON-recursively and lives outside shared/ because math-shared/examples holds
# main.tex files: kpathsea resolves even the main file through TEXINPUTS, so a
# recursive path reaching them would make a component build compile an
# example's main.tex instead of its own.
TEXINPUTS    := $(PROJECT_ROOT)/shared//:$(PROJECT_ROOT)/math-shared:
LATEXMK      = latexmk
LATEXFLAGS   = -xelatex \
               -interaction=nonstopmode \
               -halt-on-error \
               -file-line-error

STAMP_DIR    := $(PROJECT_ROOT)/.stamps/$(UNIT)/$(LESSON)
PDF_DIR      := $(PROJECT_ROOT)/target/$(UNIT)/$(LESSON)
COMPILED_DIR := $(PROJECT_ROOT)/target/compiled/$(UNIT)

# ── Component helpers ─────────────────────────────────────────────────────────
# A component "exists" if its directory holds a main.tex or a prefab main.pdf.
#   comp-present $1 → the dir name if usable, else empty
#   comp-pdf     $1 → the PDF to feed pdfunite: compiled target if main.tex,
#                     otherwise the source main.pdf used as-is
#   comp-stamp   $1 → a build stamp ONLY for tex components (prefab PDFs don't compile)
#   comp-dep     $1 → the prerequisite that guarantees the PDF exists: the build
#                     stamp for a compiled component, or the source PDF itself
#                     for a prefab. Using comp-pdf as a prerequisite would break
#                     the prefab case — a compiled target under target/ has no
#                     rule of its own.
comp-present = $(if $(or $(wildcard $1/main.tex),$(wildcard $1/main.pdf)),$1)
comp-pdf     = $(if $(wildcard $1/main.tex),$(PDF_DIR)/$1/main.pdf,$1/main.pdf)
comp-stamp   = $(if $(wildcard $1/main.tex),$(STAMP_DIR)/$1/main.stamp)
comp-dep     = $(if $(wildcard $1/main.tex),$(STAMP_DIR)/$1/main.stamp,$(wildcard $1/main.pdf))

# ── Component discovery (in pedagogical order) ────────────────────────────────
#
# `experience` is the EFFL centrepiece (Math Medic "experience first, formalize
# later"): one document carrying the group Activity, the QuickNotes the debrief
# fills, the Application, and Check Your Understanding. Students and teachers
# read it as "Experience & Formalize"; the DIRECTORY name stays `experience`
# because it is a build identifier — these two lists — and renaming it would
# mean editing the build system.
#
# It sits after `warmup` and before the legacy names. `notes`, `activity`, and
# `exit_ticket` are pre-EFFL components kept here so the ~78 lessons authored
# before the redesign still build unchanged; new lessons do not use them.
#
# In the legacy lessons that have both, `activity` comes before `notes`: the
# activity is the experience, and the notes formalize what students found in it.
# Those lessons' packets therefore put the activity pages ahead of the notes.
#
# `ap_practice` and `homework` close the packet, in that order. AP Statistics
# splits its post-lesson work in two: `ap_practice` is the AP-format rep — MC in
# context plus a free-response set — assigned but NOT scored, and `homework` is
# the graded practice, the last pages of the packet. Both names are optional; a
# lesson that provides only `homework` builds exactly as before, which is why
# adding `ap_practice` here is inert for every lesson that does not have the
# directory.
STUDENT_ORDER := cover warmup experience activity notes exit_ticket ap_practice homework
KEYED_PAIRS   := warmup experience activity notes exit_ticket ap_practice homework

STUDENT_COMPS := $(foreach c,$(STUDENT_ORDER),$(call comp-present,$(c)))

# Key packet: the student packet with every blank component swapped for its key.
# Derived from STUDENT_COMPS (not KEYED_PAIRS) so the two packets pair up 1:1,
# component for component — that pairing is what lets the pagination pass give
# both packets identical page boundaries. A component with no _key sibling
# (cover) appears unchanged in both.
key-of        = $(or $(call comp-present,$1_key),$1)
KEY_COMPS     := $(foreach c,$(STUDENT_COMPS),$(call key-of,$(c)))

# Root lesson plan and slides may also be prefab PDFs.
HAS_ROOT      := $(or $(wildcard main.tex),$(wildcard main.pdf))
ROOT_PDF      := $(if $(HAS_ROOT),$(if $(wildcard main.tex),$(PDF_DIR)/main.pdf,main.pdf))
ROOT_DEP      := $(if $(wildcard main.tex),$(STAMP_DIR)/main.stamp,$(wildcard main.pdf))

HAS_SLIDES    := $(call comp-present,slides)
SLIDES_PDF    := $(if $(HAS_SLIDES),$(call comp-pdf,slides))
SLIDES_DEP    := $(if $(HAS_SLIDES),$(call comp-dep,slides))

# ── Stamp and PDF lists ───────────────────────────────────────────────────────
# Stamps drive compilation (tex only); PDF lists drive the pdfunite merge.
STUDENT_STAMPS := $(foreach c,$(STUDENT_COMPS),$(call comp-stamp,$(c)))
STUDENT_PDFS   := $(foreach c,$(STUDENT_COMPS),$(call comp-pdf,$(c)))

KEY_STAMPS     := $(foreach c,$(KEY_COMPS),$(call comp-stamp,$(c)))
KEY_PDFS       := $(foreach c,$(KEY_COMPS),$(call comp-pdf,$(c)))

# Both packets are laid out against each other, so either target needs every
# component of both compiled before it can be paginated.
ALIGN_STAMPS   := $(sort $(STUDENT_STAMPS) $(KEY_STAMPS))

# ── The five work products ────────────────────────────────────────────────────
PLAN_OUT     := $(if $(HAS_ROOT),$(COMPILED_DIR)/$(LESSON)_plan.pdf)
SLIDES_OUT   := $(if $(HAS_SLIDES),$(COMPILED_DIR)/$(LESSON)_slides.pdf)
PPTX_OUT     := $(if $(HAS_SLIDES),$(COMPILED_DIR)/$(LESSON)_slides.pptx)
STUDENT_OUT  := $(COMPILED_DIR)/$(LESSON)_student.pdf
KEY_OUT      := $(COMPILED_DIR)/$(LESSON)_key.pdf

# Deck → printed handout: 3 slides per page, notes column beside each.
HANDOUT_TEX  := $(PROJECT_ROOT)/shared/handout.tex
HANDOUT_DIR  := $(PDF_DIR)/.handout

# PDF → PPTX: one full-bleed page image per slide, no external dependencies
# beyond the poppler tools the build already uses. Override PPTX_DPI to trade
# file size against projected sharpness. Fed the RAW deck, not the printed
# handout — a PowerPoint of 3-up handout pages would be useless to project.
PPTX_SCRIPT  := $(PROJECT_ROOT)/shared/pdf2pptx.py
PYTHON       ?= python3
PPTX_DPI     ?= 300

# Packet-wide pagination + recto starts + student/key alignment.
#
# One scratch dir per packet, never one shared between them. `student` and `key`
# are independent targets that run concurrently under -j, and paginate.sh writes
# a fixed paginated.pdf/.aux/.log into whatever directory it is handed — sharing
# one meant each packet clobbered the other's output mid-run and the loser died
# on `mv: .../paginated.pdf: No such file or directory`.
PAGINATE_SH          := $(PROJECT_ROOT)/shared/paginate.sh
PAGINATE_STUDENT_DIR := $(PDF_DIR)/.paginate-student
PAGINATE_KEY_DIR     := $(PDF_DIR)/.paginate-key

# ── Targets ───────────────────────────────────────────────────────────────────
# `slides` and `pptx` are .PHONY, so the slides/ directory never shadows them.
.PHONY: all plan slides pptx student key full clean

all: plan slides student key

# ── plan / slides ─────────────────────────────────────────────────────────────

plan: $(PLAN_OUT)
ifeq ($(strip $(HAS_ROOT)),)
	@echo "  (no lesson plan in $(UNIT)/$(LESSON))"
endif

# The deck's two forms — printed and projected. `slides` builds both.
slides: $(SLIDES_OUT) $(PPTX_OUT)
ifeq ($(strip $(HAS_SLIDES)),)
	@echo "  (no slides in $(UNIT)/$(LESSON))"
endif

pptx: $(PPTX_OUT)
ifeq ($(strip $(HAS_SLIDES)),)
	@echo "  (no slides in $(UNIT)/$(LESSON) — nothing to convert)"
endif

$(COMPILED_DIR)/$(LESSON)_plan.pdf: $(ROOT_DEP)
	@mkdir -p $(COMPILED_DIR)
	@cp $(ROOT_PDF) $@
	@echo "✓  Lesson plan    → target/compiled/$(UNIT)/$(LESSON)_plan.pdf"

# The printed form: 3 slides per letter page, ruled note column beside each.
# The page count is passed in because LaTeX cannot count the pages of an
# external PDF; pdfinfo is already a build dependency. See shared/handout.tex.
$(COMPILED_DIR)/$(LESSON)_slides.pdf: $(SLIDES_DEP) $(HANDOUT_TEX)
	@mkdir -p $(HANDOUT_DIR) $(COMPILED_DIR)
	@set -e; \
	deck=$(abspath $(SLIDES_PDF)); \
	n=$$(pdfinfo "$$deck" | awk '/^Pages:/{print $$2}'); \
	TEXINPUTS="$(TEXINPUTS)" xelatex -interaction=nonstopmode -halt-on-error \
	    -output-directory="$(HANDOUT_DIR)" -jobname=handout \
	    '\def\DeckSource{'"$$deck"'}\def\DeckPages{'"$$n"'}\input{handout}' \
	    > $(HANDOUT_DIR)/handout.log 2>&1 \
	  && mv $(HANDOUT_DIR)/handout.pdf $@ \
	  || { echo "!  handout pass failed — see $(HANDOUT_DIR)/handout.log"; \
	       grep -E "^(!|l\.)" $(HANDOUT_DIR)/handout.log | head -10; exit 1; }
	@echo "✓  Slides (PDF)   → target/compiled/$(UNIT)/$(LESSON)_slides.pdf (3 per page, notes column)"

# Built from the RAW deck, not from the 3-up handout above.
$(COMPILED_DIR)/$(LESSON)_slides.pptx: $(SLIDES_DEP) $(PPTX_SCRIPT)
	@mkdir -p $(COMPILED_DIR)
	@$(PYTHON) $(PPTX_SCRIPT) $(SLIDES_PDF) $@ --dpi $(PPTX_DPI) \
	    --title "$(UNIT) $(LESSON) slides"
	@echo "✓  Slides (PPTX)  → target/compiled/$(UNIT)/$(LESSON)_slides.pptx (full page, projectable)"

# ── student / key packets ─────────────────────────────────────────────────────
# Each component is its own document, so each numbers its pages from 1. After
# the merge, shared/paginate.sh rebuilds the packet so page numbers run across
# the whole document AND every component starts on a recto, and it lays the two
# packets against each other so page N of the key is page N of the student
# packet. See shared/paginate.tex.

student: $(ALIGN_STAMPS)
ifneq ($(strip $(STUDENT_PDFS)),)
	@mkdir -p $(COMPILED_DIR)
	pdfunite $(STUDENT_PDFS) $(STUDENT_OUT)
	@TEXINPUTS="$(TEXINPUTS)" $(PAGINATE_SH) $(STUDENT_OUT) $(PAGINATE_STUDENT_DIR) \
	    $(STUDENT_PDFS) -- $(KEY_PDFS)
	@echo "✓  Student packet → target/compiled/$(UNIT)/$(LESSON)_student.pdf (paginated $(LESSON)-wide, components start recto)"
else
	@echo "  (no student components in $(UNIT)/$(LESSON))"
endif

key: $(ALIGN_STAMPS)
ifneq ($(strip $(KEY_PDFS)),)
	@mkdir -p $(COMPILED_DIR)
	pdfunite $(KEY_PDFS) $(KEY_OUT)
	@TEXINPUTS="$(TEXINPUTS)" $(PAGINATE_SH) $(KEY_OUT) $(PAGINATE_KEY_DIR) \
	    $(KEY_PDFS) -- $(STUDENT_PDFS)
	@echo "✓  Key packet     → target/compiled/$(UNIT)/$(LESSON)_key.pdf (page-for-page with the student packet)"
else
	@echo "  (no keyed components in $(UNIT)/$(LESSON))"
endif

# `full` is gone: the lesson plan and the deck are standalone products now, so
# there is nothing left for a combined teacher packet to combine. Fail loudly
# rather than silently doing nothing to anyone with the old command in muscle
# memory or in a script.
full:
	@echo "!  \`make full\` was removed — a lesson now builds five products:" >&2
	@echo "     make plan     → $(LESSON)_plan.pdf" >&2
	@echo "     make slides   → $(LESSON)_slides.pdf  (3-up, printable)" >&2
	@echo "                   → $(LESSON)_slides.pptx (full page, projectable)" >&2
	@echo "     make student  → $(LESSON)_student.pdf" >&2
	@echo "     make key      → $(LESSON)_key.pdf     (replaces \`full\`)" >&2
	@echo "   \`make all\` builds all five." >&2
	@exit 1

# ── Pattern rule: compile a component subdirectory (tex components only) ───────
$(STAMP_DIR)/%/main.stamp: %/main.tex $(SHARED_STYS)
	@mkdir -p $(dir $@) $(PDF_DIR)/$*
	cd $* && TEXINPUTS="$(TEXINPUTS)" $(LATEXMK) $(LATEXFLAGS) \
		-outdir="$(PDF_DIR)/$*" main.tex
	@touch $@

# ── Rule: compile root-level main.tex ────────────────────────────────────────
$(STAMP_DIR)/main.stamp: main.tex $(SHARED_STYS)
	@mkdir -p $(dir $@) $(PDF_DIR)
	TEXINPUTS="$(TEXINPUTS)" $(LATEXMK) $(LATEXFLAGS) \
		-outdir="$(PDF_DIR)" main.tex
	@touch $@

clean:
	rm -rf $(STAMP_DIR) $(PDF_DIR)
	rm -f $(COMPILED_DIR)/$(LESSON)_plan.pdf \
	      $(COMPILED_DIR)/$(LESSON)_slides.pdf \
	      $(COMPILED_DIR)/$(LESSON)_slides.pptx \
	      $(COMPILED_DIR)/$(LESSON)_slides_3up.pdf \
	      $(COMPILED_DIR)/$(LESSON)_student.pdf \
	      $(COMPILED_DIR)/$(LESSON)_key.pdf \
	      $(COMPILED_DIR)/$(LESSON)_full.pdf

# ── Grading (math-shared, the submodule at the project root) ──────────────────
# Per-lesson entry points to math-shared's grading.mk, for ONE component that
# uses grading.sty (\gradedblank items — ap_practice and homework):
#
#   make manifest COMP=homework
#       blank + key builds, target/<unit>/<lesson>/grading/<COMP>/manifest.json,
#       and the check that the blank and key agree on every graded item.
#   make roster-packets COMP=homework ROSTER=~/Rosters/apstats/roster-map.csv [SECTION=…]
#       per student, in roster order: one copy of the lesson's student packet
#       with her name preprinted on the lesson cover and her personalized COMP (QR codes and the id strip carry only
#       her tracking id) in place of the master copy, paginated by
#       shared/paginate.sh exactly like `make student`. Joined into
#       target/compiled/<unit>/lessonYY_<COMP>_roster.pdf to print as one
#       collated job. A COMP that is not in the student packet gets math-shared's
#       own run per student instead: cover, blank back, then the component
#       padded to an even page count.
#
# A lesson packet has NO separate name sheet: the lesson cover carries the name
# (2026-10-26). Tests and quizzes keep math-shared's tear-off name sheet as their
# first page (shared/assessment-grading.mk). A lesson with no cover/ falls back to
# that sheet so the name is still somewhere. The roster PDFs carry names, so they
# stay under target/, which is never committed.
# grading-namecheck (shared/check_namelines.py) runs first in both: it fails if
# COMP or its key loads grading.sty and still carries a name line.
GRADING_MK  := $(PROJECT_ROOT)/math-shared/grading.mk
COMP        ?=
COMPONENT   := $(COMP)
GRADING_OUT := $(PDF_DIR)/grading/$(COMP)

.PHONY: manifest roster-packets grading-need-comp grading-namecheck

ifneq ($(wildcard $(GRADING_MK)),)
include $(GRADING_MK)

grading-need-comp:
	@test -n "$(COMP)" || { echo "!  set COMP=<component directory>, e.g. COMP=homework"; exit 1; }

grading-namecheck: grading-need-comp
	@$(GRADING_PYTHON) $(PROJECT_ROOT)/shared/check_namelines.py $(COMPONENT) $(KEY_COMPONENT)

manifest: grading-namecheck
	@$(MAKE) --no-print-directory grading-manifest
	@echo "✓  Manifest       → target/$(UNIT)/$(LESSON)/grading/$(COMP)/manifest.json"

# Roster order and tracking ids, read only when ROSTER is given.
ROSTER_IDS     := $(if $(ROSTER),$(shell $(GRADING_PYTHON) $(GRADING_SCRIPTS)/roster_tex.py \
                    "$(ROSTER)" --ids-only $(if $(SECTION),--section "$(SECTION)")))
ROSTER_PKT_DIR := $(GRADING_OUT)/roster
ROSTER_PACKETS := $(foreach id,$(ROSTER_IDS),$(ROSTER_PKT_DIR)/$(id).pdf)
ROSTER_OUT     := $(COMPILED_DIR)/$(LESSON)_$(COMP)_roster.pdf

# The master copy of COMP as it appears in the student packet, if it does.
COMP_MASTER_PDF := $(PDF_DIR)/$(COMP)/main.pdf
COMP_IN_PACKET  := $(filter $(COMP_MASTER_PDF),$(STUDENT_PDFS))

roster-packets: grading-namecheck grading-need-roster
	@test -n "$(strip $(ROSTER_IDS))" || { echo "!  no students in $(ROSTER)"; exit 1; }
	@$(MAKE) --no-print-directory $(ROSTER_PACKETS)
	@mkdir -p $(COMPILED_DIR)
	@if [ $(words $(ROSTER_PACKETS)) -eq 1 ]; then cp $(ROSTER_PACKETS) $(ROSTER_OUT); \
	 else pdfunite $(ROSTER_PACKETS) $(ROSTER_OUT); fi
	@echo "✓  Roster packets → target/compiled/$(UNIT)/$(LESSON)_$(COMP)_roster.pdf ($(words $(ROSTER_IDS)) students, roster order)"

# One student's run. grading-personalized (math-shared) compiles every student's
# COMP into $(GR_STUDENTS)/<id>.pdf, her cover into $(GR_COVERS)/cover-<id>.pdf
# and the blank back into $(GR_BACK); its own run per student, for COMP alone,
# is $(GR_PACKETS)/<id>.pdf. When COMP is in the student packet, her copy
# replaces the master in the packet's PDF list, the packet is paginated against
# the same key-packet list `make student` uses (so its page boundaries are
# identical, and its page count even).
# Each student gets a paginate.sh scratch dir of its own (see PAGINATE_*_DIR).
#
# The lesson cover is personalized too: it is compiled once per student with
#   \def\StudentName{Preferred Last}
# ahead of it (roster_tex.py's TeX-safe names, as on math-shared's cover
# sheet), so \namedateperiod prints her name on the Name line, and her copy
# replaces the master cover in the packet. Only cover/ is compiled with a
# name; every graded component is built by math-shared from ids alone.
COVER_MASTER_PDF := $(if $(wildcard cover/main.tex),$(PDF_DIR)/cover/main.pdf)
ROSTER_NAME_DIR  := $(ROSTER_PKT_DIR)/covers
ROSTER_PKT_PDFS = $(patsubst $(COMP_MASTER_PDF),$(GR_STUDENTS)/$*.pdf,$(if $(COVER_MASTER_PDF),\
                    $(patsubst $(COVER_MASTER_PDF),$(ROSTER_NAME_DIR)/$*.pdf,$(STUDENT_PDFS)),\
                    $(STUDENT_PDFS)))

ifneq ($(COMP_IN_PACKET),)
$(ROSTER_PKT_DIR)/%.pdf: grading-personalized $(ALIGN_STAMPS)
	@mkdir -p $(dir $@)
ifneq ($(COVER_MASTER_PDF),)
	@mkdir -p $(ROSTER_NAME_DIR)
	@set -e; \
	row=$$($(GRADING_PYTHON) $(GRADING_SCRIPTS)/roster_tex.py "$(ROSTER)" --id $*); \
	pref=$$(printf '%s\n' "$$row" | cut -f2); last=$$(printf '%s\n' "$$row" | cut -f3); \
	( cd cover && TEXINPUTS="$(TEXINPUTS)" $(LATEXMK) $(LATEXFLAGS) -jobname=$* \
	    -usepretex="\def\StudentName{$$pref $$last}" \
	    -outdir="$(ROSTER_NAME_DIR)" main.tex > "$(ROSTER_NAME_DIR)/$*.out" 2>&1 ) \
	  || { echo "!  LaTeX failed for the named cover of $* — see $(ROSTER_NAME_DIR)/$*.log"; \
	       grep -E "^(!|l\.|.*:[0-9]+: )" "$(ROSTER_NAME_DIR)/$*.log" | head -10; exit 1; }
endif
	@set -- $(ROSTER_PKT_PDFS); \
	if [ $$# -eq 1 ]; then cp "$$1" $(ROSTER_PKT_DIR)/.body-$*.pdf; \
	else pdfunite "$$@" $(ROSTER_PKT_DIR)/.body-$*.pdf; fi
	@TEXINPUTS="$(TEXINPUTS)" $(PAGINATE_SH) $(ROSTER_PKT_DIR)/.body-$*.pdf \
	    $(ROSTER_PKT_DIR)/.paginate-$* $(ROSTER_PKT_PDFS) -- $(KEY_PDFS)
ifneq ($(COVER_MASTER_PDF),)
	@mv $(ROSTER_PKT_DIR)/.body-$*.pdf $@
else
	@pdfunite $(GR_COVERS)/cover-$*.pdf $(GR_BACK) $(ROSTER_PKT_DIR)/.body-$*.pdf $@
	@rm -f $(ROSTER_PKT_DIR)/.body-$*.pdf
endif
else
$(ROSTER_PKT_DIR)/%.pdf: grading-personalized
	@mkdir -p $(dir $@)
	@cp $(GR_PACKETS)/$*.pdf $@
endif
else
manifest roster-packets grading-need-comp grading-namecheck:
	@echo "!  math-shared is empty — run: git submodule update --init"; exit 1
endif
