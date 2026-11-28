#!/bin/zsh
# v7 region-B pilot (registration V7_REGISTRATION.md, stage P, addenda 5-10): ONE attempt, per the Bridge's ruling.
#   usage: v7_pB.sh KC HALF        e.g. 83/20 1/20 (pilot 2) or 59979/14000 1/2000 (pilot 3)
# Prove, verdict with full controls, region-B engine gate (HP engine). Floats entries from _nve_v7_floatsB.py (committed
# geometry rule; generated before the pilots). Run under air/v7_job.sh (pause-only guard, nice 10).
cd /Users/sumit/Github/conjecture_machine-check || exit 1
P13=/Users/sumit/Github/conjecture_machine-check/.venv313/bin/python
P14=/Users/sumit/Github/conjecture_machine/.venv/bin/python
KC=$1; HALF=$2
export NVE_SPIN=3/5 R1_R0=1.35 R1_KC=$KC R1_HALF=$HALF R1_FLOATS=route1_floats_v7B_3_5.json R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel
CODE=$(${=P13} -I -c "import sys; sys.path.insert(0, 'scripts'); import _nve_route1_segment_v7B as S; print(S.CODE)")
[ -n "$CODE" ] || exit 1
BASE=v7B_kc${KC//\//o}h${HALF//\//o}_$CODE
echo "=== v7B pilot k_c $KC half $HALF code $CODE base $BASE $(date '+%F %T')"
echo "=== prove $(date '+%F %T')"
${=P13} -I -u scripts/_nve_route1_segment_v7B.py prove || exit 1
echo "=== verdict (full controls) $(date '+%F %T')"
R1_FULLCTL=1 ${=P13} -I -u scripts/_nve_route1_segment_v7B.py verdict; echo "verdict rc $?"
echo "=== engine gate B $(date '+%F %T')"
NODES=data/nve/eps/route1_seg_nodes_$BASE.jsonl FLOATS=data/nve/eps/route1_floats_v7B_3_5.json \
  OUTJ=data/nve/eps/route1_seg_engineB_$BASE.jsonl R1_CODE=$CODE ${=P14} -I -u scripts/_nve_v7_engine_gate_B.py
echo "engine gate rc $?"
echo "=== V7_PB_DONE $(date '+%F %T')"
