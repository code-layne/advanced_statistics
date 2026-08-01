#!/bin/sh
# shared/paginate.sh — the packet-wide pagination pass, shared by lesson.mk and
# unit.mk so the slot arithmetic lives in exactly one place.
#
# Rewrites an already-merged packet in place so page numbers run across the
# whole document and every piece starts on a recto. The piece list is passed
# twice over: once for the packet being built (SELF) and once for its
# counterpart (OTHER, 1:1 with SELF), because each piece's slot is
#
#     slot = ceil_even( max(self pages, counterpart pages) )
#
# and the shorter of the two is padded with blank versos to fill it. Both the
# student and the key packet compute the same slots from the same two lists, so
# page N of the key is page N of the student packet whether they were built
# together or separately.
#
# Usage:
#   TEXINPUTS=... paginate.sh MERGED WORKDIR SELF... -- OTHER...
#
# MERGED   the merged packet, rewritten in place
# WORKDIR  scratch directory for the xelatex run and its log. The run always
#          writes paginated.pdf/.aux/.log here, so every concurrent invocation
#          needs a WORKDIR of its own — the student and key packets of one
#          lesson are separate make targets and do run at the same time under
#          -j. Sharing one directory makes them delete each other's output.
# SELF     the piece PDFs that were merged, in merge order
# OTHER    the counterpart packet's pieces, same order, 1:1 with SELF
#
# Pass an empty OTHER list to align a packet against nothing; every slot is then
# just its own page count rounded up to even.

set -eu

if [ $# -lt 2 ]; then
    echo "usage: paginate.sh MERGED WORKDIR SELF... -- OTHER..." >&2
    exit 2
fi

merged=$1; shift
workdir=$1; shift

self=''
while [ $# -gt 0 ]; do
    if [ "$1" = '--' ]; then shift; break; fi
    self="$self $1"; shift
done
other="$*"

pages() {
    n=$(pdfinfo "$1" 2>/dev/null | awk '/^Pages:/{print $2}')
    if [ -z "$n" ]; then
        echo "!  paginate: cannot read page count of $1" >&2
        exit 1
    fi
    echo "$n"
}

# Walk SELF and OTHER in lockstep. OTHER is consumed off the positional
# parameters so the two lists stay paired without arrays (this is /bin/sh).
# shellcheck disable=SC2086
set -- $other

spec=''
first=1
for f in $self; do
    n=$(pages "$f")
    slot=$n
    if [ $# -gt 0 ]; then
        m=$(pages "$1")
        shift
        if [ "$m" -gt "$slot" ]; then slot=$m; fi
    fi
    slot=$(( (slot + 1) / 2 * 2 ))          # round up to even → next piece is recto
    last=$(( first + n - 1 ))
    spec="$spec,$first-$last"
    pad=$(( slot - n ))
    while [ $pad -gt 0 ]; do
        spec="$spec,{}"                      # pdfpages: insert a blank page
        pad=$(( pad - 1 ))
    done
    first=$(( last + 1 ))
done
spec=${spec#,}

if [ -z "$spec" ]; then
    echo "!  paginate: no input pieces given for $merged" >&2
    exit 1
fi

mkdir -p "$workdir"

if xelatex -interaction=nonstopmode -halt-on-error \
        -output-directory="$workdir" -jobname=paginated \
        "\\def\\PacketSource{$merged}\\def\\PacketPages{$spec}\\input{paginate}" \
        > "$workdir/paginate.log" 2>&1; then
    mv "$workdir/paginated.pdf" "$merged"
else
    echo "!  pagination pass failed — see $workdir/paginate.log" >&2
    grep -E '^(!|l\.)' "$workdir/paginate.log" | head -10 >&2
    exit 1
fi
