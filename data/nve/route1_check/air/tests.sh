#!/bin/zsh
# T1-T4 of the route-(i) registration (§3(d)) on the Air, under .venv313 (Python 3.13.18), spin 3/5, one process at a time.
# T1: v4's proof stage, then v5's, both here and under the same Python; rows compared by _nve_route1_t1_compare.py.
# Then T2-T4 (_nve_route1_t234.py) on the v5 files T1 leaves. Refuses to start if any v4 or v5 spin-3/5 checkpoint exists.
cd ~/GitHub/ansatz-air || exit 1
E=data/nve/eps
export NVE_SPIN=3/5 R1_R0=1.35
for f in $E/route1_seg_v4_rows.jsonl $E/route1_seg_v4_dqck.jsonl $E/route1_seg_v5_*(N); do
  [[ -e $f ]] && { echo "REFUSE: $f exists"; exit 1; }
done
mkdir -p $E/kept && cp -p $E/route1_seg_M_v4_nseg1.json $E/kept/   # the committed 3/5 v4 proof JSON (P1's input): v4 rewrites it
echo "=== T1 v4 prove $(date '+%F %T') $(.venv313/bin/python -V)"
.venv313/bin/python -I -u scripts/_nve_route1_segment_v4.py || exit 1
mv $E/route1_seg_M_v4_nseg1.json $E/route1_seg_M_v4_nseg1_T1run.json && cp -p $E/kept/route1_seg_M_v4_nseg1.json $E/
echo "=== T1 v5 prove $(date '+%F %T')"
.venv313/bin/python -I -u scripts/_nve_route1_segment_v5.py prove || exit 1
echo "=== T1 compare $(date '+%F %T')"
.venv313/bin/python -I -u scripts/_nve_route1_t1_compare.py $E/route1_seg_v4_rows.jsonl $E/route1_seg_v5_*_rows.jsonl committed/route1_seg_v4_rows.jsonl || exit 1
echo "=== T2-T4 $(date '+%F %T')"
.venv313/bin/python -I -u scripts/_nve_route1_t234.py || exit 1
echo "=== TESTS_DONE $(date '+%F %T')"
