#!/bin/bash
# Rank-3 feasibility AND a real extension of the validated control. The open question is sGB ranks
# 3-6; if rank 3 is already impractical the double-expansion design has to account for that, so
# this is on the critical path regardless of the zeta/chi bookkeeping still to be built.
cd /Users/sumit/Github/conjecture_machine
L=data/kt_overnight.log
say(){ echo "$(date '+%m-%d %H:%M:%S')  $*" >> "$L"; }
say "RANK 4 FEASIBILITY: generic perturbation on Kerr, rank 3, denpow 2 (5915 columns)"
say "  rank2 2628s@1690, rank3 6221s@3380 -> scaling is NEAR-LINEAR (2.37x for 2x cols), not cubic. Expect ~3-4h, not the 30h a cubic law predicted."
s=$(date +%s)
.venv/bin/python scripts/_kt_perturb.py --rank 4 --denpow 2 --selftest --only 2 \
  > data/kt_perturb_r4.out 2>&1
d=$(( $(date +%s) - s ))
P=$(grep -c "SELFTEST PASSED" data/kt_perturb_r4.out)
say "  rank 4 done in ${d}s, PASSED=$P  $(grep -oE 'background [0-9]+, surviving [0-9]+, expected [0-9]+ -> [A-Z]+' data/kt_perturb_r4.out | tail -1)"
say "  scaling: rank2 2628s at 1690 cols -> rank4 ${d}s at 5915 cols"
say "=== RANK 4 FEASIBILITY DONE ==="
