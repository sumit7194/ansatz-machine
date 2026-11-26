#!/bin/zsh
# (a') the spin-9/10 v4 reproduction again, under Homebrew Python 3.13.18 (.venv313: python-flint 0.9.0, mpmath 1.3.0,
# sympy 1.14.0, numpy 2.5.0, the committed 3.13.12 run's packages). The Bridge's ruling after the 3.14 run differed in the
# gauge: get the exact reproduction. The 3.14 outputs were moved to data/nve/eps/run314/ first, so no rows or dqck file exists.
cd ~/GitHub/ansatz-air || exit 1
for f in route1_seg_v4_9_10_rows.jsonl route1_seg_v4_9_10_dqck.jsonl; do [[ -e data/nve/eps/$f ]] && { echo "REFUSE: $f exists"; exit 1; }; done
export NVE_SPIN=9/10 R1_R0=1.2639
echo "=== prove $(date '+%F %T') $(.venv313/bin/python -V)"
.venv313/bin/python -I -u scripts/_nve_route1_segment_v4.py || exit 1
echo "=== verdict $(date '+%F %T')"
.venv313/bin/python -I -u scripts/_nve_route1_v4_verdict.py || exit 1
echo "=== REPRO313_DONE $(date '+%F %T')"
