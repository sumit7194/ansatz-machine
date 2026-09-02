#!/bin/bash
# Rank-3 feasibility AND a real extension of the validated control. The open question is sGB ranks
# 3-6; if rank 3 is already impractical the double-expansion design has to account for that, so
# this is on the critical path regardless of the zeta/chi bookkeeping still to be built.
cd /Users/sumit/Github/conjecture_machine
L=data/kt_overnight.log
say(){ echo "$(date '+%m-%d %H:%M:%S')  $*" >> "$L"; }
say "RANK 3 FEASIBILITY: generic perturbation on Kerr, rank 3, denpow 2 (3380 columns)"
say "  rank 2 at 1690 columns took 2628s; cost is ~cols^3, so expect roughly 6h"
s=$(date +%s)
.venv/bin/python scripts/_kt_perturb.py --rank 3 --denpow 2 --selftest --only 2 \
  > data/kt_perturb_r3.out 2>&1
d=$(( $(date +%s) - s ))
P=$(grep -c "SELFTEST PASSED" data/kt_perturb_r3.out)
say "  rank 3 done in ${d}s, PASSED=$P  $(grep -oE 'background [0-9]+, surviving [0-9]+, expected [0-9]+ -> [A-Z]+' data/kt_perturb_r3.out | tail -1)"
say "  scaling: rank2 2628s at 1690 cols -> rank3 ${d}s at 3380 cols"
say "=== RANK 3 FEASIBILITY DONE ==="
