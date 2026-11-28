#!/bin/zsh
# v7 stage V2, tests T1'-T4' at spin 3/5 on [1, 11/10] (registration V7_REGISTRATION.md): v7 prove, verdict with full
# controls, then the independent engine gate on every node. Run under air/v7_job.sh (pause-only guard, nice 10).
cd /Users/sumit/Github/conjecture_machine-check || exit 1
P13=/Users/sumit/Github/conjecture_machine-check/.venv313/bin/python
P14=/Users/sumit/Github/conjecture_machine/.venv/bin/python
export NVE_SPIN=3/5 R1_R0=1.35 R1_KC=21/20 R1_HALF=1/20 R1_FLOATS=route1_floats_v7t1_3_5.json R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel
CODE=$(${=P13} -I -c "import sys; sys.path.insert(0, 'scripts'); import _nve_route1_segment_v7 as S; print(S.CODE)")
BASE=v7_kc21o20h1o20_$CODE
echo "=== v7 T1 code $CODE base $BASE $(date '+%F %T')"
echo "=== prove $(date '+%F %T')"
${=P13} -I -u scripts/_nve_route1_segment_v7.py prove || exit 1
echo "=== verdict (full controls) $(date '+%F %T')"
R1_FULLCTL=1 ${=P13} -I -u scripts/_nve_route1_segment_v7.py verdict; echo "verdict rc $?"
echo "=== engine gate $(date '+%F %T')"
NODES=data/nve/eps/route1_seg_nodes_$BASE.jsonl FLOATS=data/nve/eps/route1_floats_v7t1_3_5.json \
  OUTJ=data/nve/eps/route1_seg_engine_$BASE.jsonl R1_CODE=$CODE ${=P14} -I -u scripts/_nve_route1_engine_gate.py
echo "engine gate rc $?"
echo "=== V7_T1_DONE $(date '+%F %T')"
