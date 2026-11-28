#!/bin/zsh
# v7 pilot P1 at spin 3/5, circle picture, k_c 79/20, half-width 1/20 (registration V7_REGISTRATION.md, addendum 6):
# floats, then the code hash (after the floats file exists), v7 prove, verdict with full controls, engine gate.
# Run under air/v7_job.sh (pause-only guard, nice 10).
cd /Users/sumit/Github/conjecture_machine-check || exit 1
P13=/Users/sumit/Github/conjecture_machine-check/.venv313/bin/python
P14=/Users/sumit/Github/conjecture_machine/.venv/bin/python
export NVE_SPIN=3/5 R1_R0=1.35 R1_KC=79/20 R1_HALF=1/20 R1_FLOATS=route1_floats_v7p_3_5.json R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel
echo "=== floats $(date '+%F %T')"
${=P14} -I -u scripts/_nve_route1_floats.py 79/20 || exit 1
CODE=$(${=P13} -I -c "import sys; sys.path.insert(0, 'scripts'); import _nve_route1_segment_v7 as S; print(S.CODE)")
[ -n "$CODE" ] || exit 1
BASE=v7_kc79o20h1o20_$CODE
echo "=== v7 P1 code $CODE base $BASE $(date '+%F %T')"
echo "=== prove $(date '+%F %T')"
${=P13} -I -u scripts/_nve_route1_segment_v7.py prove || exit 1
echo "=== verdict (full controls) $(date '+%F %T')"
R1_FULLCTL=1 ${=P13} -I -u scripts/_nve_route1_segment_v7.py verdict; echo "verdict rc $?"
echo "=== engine gate $(date '+%F %T')"
NODES=data/nve/eps/route1_seg_nodes_$BASE.jsonl FLOATS=data/nve/eps/route1_floats_v7p_3_5.json \
  OUTJ=data/nve/eps/route1_seg_engine_$BASE.jsonl R1_CODE=$CODE ${=P14} -I -u scripts/_nve_route1_engine_gate.py
echo "engine gate rc $?"
echo "=== V7_P1_DONE $(date '+%F %T')"
