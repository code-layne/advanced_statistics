#!/usr/bin/env bash
# shared/release.sh — build one unit's teacher kit, zip it, and (optionally)
# publish it as a GitHub Release.
#
#   shared/release.sh unit02            build + stage + zip, no upload  (make package UNIT=unit02)
#   shared/release.sh unit02 --publish  …and create the GitHub Release  (make release UNIT=unit02)
#
# Env: VERSION=3 forces the release number (default: one past the highest
#      existing unitXX-vN tag on GitHub, or v1).
#      NOBUILD=1 skips the make pass and packages whatever is already in target/.
#
# The kit (target/release/unitXX/, zipped to target/release/<name>.zip):
#
#   unitXX_student.pdf, unitXX_key.pdf          the two bound unit packets
#   lessons/lessonYY_{plan,slides,student,key}.pdf, lessonYY_slides.pptx
#   <dir>/<doc>.pdf     for every non-lesson unit folder with its own Makefile
#                       (tests, test_keys, quizzes, quiz01, warmups, extras, review, …)
#   covers, sample test(s), study guide — whatever else the unit build left in
#                       target/compiled/unitXX/ — plus unitXX*.pptx from the unit folder
#
# Repo-agnostic: the same file lives in every curriculum repo (stats, saar,
# algebra_2, precalculus); the GitHub repo comes from `origin`.
#
# Roster packets (lessonYY_roster.pdf, *_roster.pdf) carry student names and are
# NEVER packaged: files are copied by explicit name, and a final guard refuses
# to zip anything with "roster" in its name.
#
# The repo is public, so a release is public too — keys and actual tests
# included. That is a deliberate choice; see README "Releases".

set -euo pipefail
unset MAKEFLAGS MFLAGS MAKELEVEL   # `make release UNIT=…` must not leak UNIT into sub-makes

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

UNIT="${1:-}"
PUBLISH=0
[ "${2:-}" = "--publish" ] && PUBLISH=1

if [[ ! "$UNIT" =~ ^unit[0-9]{2}$ ]] || [ ! -f "$UNIT/Makefile" ]; then
  echo "!  usage: shared/release.sh unitXX [--publish]   (no $UNIT/Makefile)" >&2
  exit 1
fi

REPO="$(git remote get-url origin | sed -E 's#^.*github\.com[:/]##; s#\.git$##')"
COMPILED="target/compiled"
BUILT="target/$UNIT"
STAGE_ROOT="target/release"
STAGE="$STAGE_ROOT/$UNIT"

# ── Title, from \UnitNumberName in the lesson sources (same source as cover.py) ──
TITLE="$(grep -h '\\newcommand{\\UnitNumberName}' "$UNIT"/lesson*/main.tex 2>/dev/null \
         | head -1 | sed -E 's/.*\\UnitNumberName\}\{(.*)\}.*/\1/; s/\\quad//; s/[[:space:]]+$//')"
[ -n "$TITLE" ] || TITLE="Unit $((10#${UNIT#unit}))"

# ── Publish preconditions, checked before the long build ─────────────────────
if [ "$PUBLISH" = 1 ]; then
  if [ -n "$(git status --porcelain --untracked-files=no)" ]; then
    echo "!  uncommitted changes — commit first so the release matches its tag" >&2; exit 1
  fi
  git fetch -q origin
  if [ -z "$(git branch -r --contains HEAD 2>/dev/null)" ]; then
    echo "!  HEAD ($(git rev-parse --short HEAD)) is not on GitHub — push it first" >&2; exit 1
  fi
  if [ -z "${VERSION:-}" ]; then
    last="$(gh release list -R "$REPO" --limit 200 --json tagName -q '.[].tagName' \
            | sed -nE "s/^$UNIT-v([0-9]+)$/\1/p" | sort -n | tail -1)"
    VERSION=$(( ${last:-0} + 1 ))
  fi
fi
VERSION="${VERSION:-dev}"
TAG="$UNIT-v$VERSION"
ZIPNAME="$(basename "$REPO" | tr _ -)-$TAG"

# ── Build ────────────────────────────────────────────────────────────────────
# Every non-lesson folder with its own Makefile builds standalone documents into
# target/unitXX/<dir>/<doc>/main.pdf. They go first: the tests `drop` rule writes
# sample_test/main.pdf, which the packets merge.
EXTRA_DIRS=""
for d in "$UNIT"/*/; do
  d="$(basename "$d")"
  case "$d" in lesson*) continue ;; esac
  [ -f "$UNIT/$d/Makefile" ] && EXTRA_DIRS="$EXTRA_DIRS $d"
done
if [ "${NOBUILD:-0}" != 1 ]; then
  dirty_before="$(git diff --name-only -- "$UNIT")"
  for d in $EXTRA_DIRS; do make -C "$UNIT/$d"; done
  make -C "$UNIT" all
  make -C "$UNIT" student key
  # Some repos commit sample_test*/main.pdf; the `drop` rule rewrites it with a
  # fresh timestamp. The packets (and so the release) already carry the fresh
  # build, so put any committed file the build touched back as it was — a
  # release must never leave the working tree dirty.
  for f in $(git diff --name-only -- "$UNIT"); do
    if ! grep -qxF "$f" <<<"$dirty_before"; then
      git checkout -q -- "$f" && echo "   restored committed $f (the release uses the fresh build)"
    fi
  done
fi

# ── Stage ────────────────────────────────────────────────────────────────────
rm -rf "$STAGE"
mkdir -p "$STAGE/lessons"

copy() { [ -f "$1" ] && cp "$1" "$2"; return 0; }

copy "$COMPILED/${UNIT}_student.pdf" "$STAGE/"
copy "$COMPILED/${UNIT}_key.pdf"     "$STAGE/"
for f in "$COMPILED/$UNIT"/*.pdf "$UNIT"/"$UNIT"*.pptx; do   # covers, sample tests, study guide, unit deck
  case "$(basename "$f")" in lesson*) continue ;; esac
  copy "$f" "$STAGE/"
done

for l in "$UNIT"/lesson*/; do
  l="$(basename "$l")"
  for f in plan.pdf slides.pdf slides.pptx student.pdf key.pdf; do
    copy "$COMPILED/$UNIT/${l}_$f" "$STAGE/lessons/"
  done
done

for d in $EXTRA_DIRS; do
  [ -d "$BUILT/$d" ] || continue
  for doc in "$BUILT/$d"/*/main.pdf; do
    [ -f "$doc" ] || continue
    name="$(basename "$(dirname "$doc")")"
    [ -d "$UNIT/$d/$name" ] || continue       # skip stale builds of deleted sources
    mkdir -p "$STAGE/$d"
    cp "$doc" "$STAGE/$d/$name.pdf"
  done
done

if find "$STAGE" -iname '*roster*' | grep -q .; then
  echo "!  a roster file reached the staging dir — refusing to package student names" >&2
  find "$STAGE" -iname '*roster*' >&2; exit 1
fi
[ -f "$STAGE/${UNIT}_student.pdf" ] || { echo "!  no ${UNIT}_student.pdf — did the build fail?" >&2; exit 1; }

# ── Zip ──────────────────────────────────────────────────────────────────────
ZIP="$STAGE_ROOT/$ZIPNAME.zip"
rm -f "$ZIP"
(cd "$STAGE_ROOT" && rm -rf "$ZIPNAME" && cp -R "$UNIT" "$ZIPNAME" \
   && zip -qr "$ZIPNAME.zip" "$ZIPNAME" -x '*.DS_Store' && rm -rf "$ZIPNAME")
echo "✓  $TITLE → $ZIP ($(du -h "$ZIP" | cut -f1), $(find "$STAGE" -type f | wc -l | tr -d ' ') files)"

[ "$PUBLISH" = 1 ] || { echo "   (package only — \`make release UNIT=$UNIT\` publishes)"; exit 0; }

# ── Publish ──────────────────────────────────────────────────────────────────
NOTES="$(mktemp)"
{
  echo "Teacher kit for **$TITLE**, built from \`$(git rev-parse --short HEAD)\` on $(date +%Y-%m-%d)."
  echo
  echo "- \`$ZIPNAME.zip\` — everything below"
  echo "- \`${UNIT}_student.pdf\` / \`${UNIT}_key.pdf\` — the bound unit packets, page for page"
  echo
  echo "Zip contents:"
  echo '```'
  (cd "$STAGE" && find . -type f | sed 's|^\./||' | sort)
  echo '```'
} > "$NOTES"

assets=("$ZIP" "$STAGE/${UNIT}_student.pdf")
[ -f "$STAGE/${UNIT}_key.pdf" ] && assets+=("$STAGE/${UNIT}_key.pdf")

gh release create "$TAG" "${assets[@]}" -R "$REPO" \
   --target "$(git rev-parse HEAD)" --title "$TITLE (v$VERSION)" --notes-file "$NOTES"
rm -f "$NOTES"
