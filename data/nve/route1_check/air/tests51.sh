#!/bin/zsh
# T1-T4 again, on v5.1 + B1 (b64a43c), the Bridge's condition after its v5.1 read. Air, .venv313 (Python 3.13.18), spin 3/5.
# T1: v5.1's proof stage at the DEFAULT segment against the v4 rows written by this machine and Python in the first T1
# run (tests.sh, 7f96efc). Then T2-T4 (+ B1's refusal) on v5.1's files. Refuses if any file of this code already exists.
cd ~/GitHub/ansatz-air || exit 1
E=data/nve/eps
export NVE_SPIN=3/5 R1_R0=1.35
CODE=$(.venv313/bin/python -I -c "import sys; sys.path.insert(0, 'scripts'); import _nve_route1_segment_v5 as S; print(S.CODE)") || exit 1
echo "=== v5.1 code $CODE"
for f in $E/*_$CODE*(N); do echo "REFUSE: $f exists"; exit 1; done
[[ -e $E/route1_seg_v4_rows.jsonl ]] || { echo "REFUSE: no v4 rows from the first T1 run"; exit 1; }
echo "=== T1' v5.1 prove $(date '+%F %T') $(.venv313/bin/python -V)"
.venv313/bin/python -I -u scripts/_nve_route1_segment_v5.py prove || exit 1
echo "=== T1' compare $(date '+%F %T')"
T1_MJSON=$E/route1_seg_M_v4_nseg1_T1run.json:$E/route1_seg_M_v5_${CODE}_nseg1.json .venv313/bin/python -I -u scripts/_nve_route1_t1_compare.py $E/route1_seg_v4_rows.jsonl $E/route1_seg_v5_${CODE}_rows.jsonl || exit 1
echo "=== T2-T4' $(date '+%F %T')"
.venv313/bin/python -I -u scripts/_nve_route1_t234.py || exit 1
echo "=== TESTS51_DONE $(date '+%F %T')"
