#!/bin/bash
# Headroom on a SHARED machine, done the way that is actually actionable.
#
# THREE TRAPS, ALL OF WHICH BIT SOMEBODY ON 2026-08-21:
#  1. PAGE SIZE. This Mac reports 16384 bytes/page, not 4096. A hardcoded 4096 reads 4x LOW and
#     the error runs CONSERVATIVE -- it cancels runs rather than crashing them, so it produces no
#     symptom. It stood down two runs across two sessions before anyone noticed. Read hw.pagesize;
#     never type a page size into a formula. (One session parsed the header into a variable and
#     then hardcoded 4096 anyway -- knowledge acquired, held, and discarded at the point of use,
#     which is invisible to a review that sees the header being parsed and assumes units are fine.)
#  2. "FREE" IS NOT HEADROOM. Inactive pages are reclaimable. free alone reads near-zero on a
#     perfectly healthy machine, and an alarm thresholded on it is a false alarm generator. This
#     script's own author shipped a monitor with exactly that defect the same hour he wrote the
#     rule down in prose. Stating a rule and encoding it are separate acts.
#  3. SWAP-USED IS NOT PAGING. macOS allocates swap eagerly and compresses aggressively; over a
#     gigabyte of swap "used" alongside gigabytes free is ordinary steady state. The number that
#     means distress is the PAGEOUT RATE, which needs TWO samples. A single swap total reads
#     alarming on a healthy machine and cannot distinguish residue from thrashing.
#
# Usage:  scripts/machine_state.sh [sample_seconds]   (default 10)
set -u
SEC="${1:-10}"
PS=$(sysctl -n hw.pagesize)
stamp() { date -u +%Y-%m-%dT%H:%M:%SZ; }
pg() { vm_stat | awk -v k="$1" '$0 ~ k {gsub(/\./,"",$NF); print $NF; exit}'; }

P1=$(pg "Pageouts")
T1=$(stamp)
sleep "$SEC"
P2=$(pg "Pageouts")

FREE=$(pg "Pages free"); INACT=$(pg "Pages inactive"); SPEC=$(pg "Pages speculative")
USABLE=$(( (FREE + INACT + SPEC) * PS ))
DELTA=$(( P2 - P1 ))

printf '  %s  (page size %s B, read from hw.pagesize)\n' "$T1" "$PS"
printf '  free %.2f GB + inactive %.2f GB + speculative %.2f GB  ->  USABLE %.2f GB\n' \
  "$(bc -l <<< "$FREE*$PS/1073741824")" "$(bc -l <<< "$INACT*$PS/1073741824")" \
  "$(bc -l <<< "$SPEC*$PS/1073741824")" "$(bc -l <<< "$USABLE/1073741824")"
printf '  pageouts %s -> %s   delta %s pages (%.1f MB) over %ss\n' \
  "$P1" "$P2" "$DELTA" "$(bc -l <<< "$DELTA*$PS/1048576")" "$SEC"
if [ "$DELTA" -gt 256 ]; then
  printf '  VERDICT: PAGING -- %s pages out in %ss. Headroom figure is not trustworthy.\n' "$DELTA" "$SEC"
else
  printf '  VERDICT: not paging (delta %s pages). Usable figure above is actionable.\n' "$DELTA"
fi
echo "  top consumers:"
ps -axo rss,pid,comm | sort -rn | head -4 | awk '{printf "    %7.0f MB  pid %-7s %.48s\n", $1/1024, $2, $3}'
