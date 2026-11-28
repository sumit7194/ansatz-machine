#!/bin/zsh
# C2-M production: ONE segment (C2_PROD_REGISTRATION.md), the pilot's sequence (air/c2m_pilot.sh) with two changes:
#  (1) the runner defect is fixed: if the cover did not end with every cell accepted (stop set, or no leaves), the
#      later stages are SKIPPED (Pend ran them on an empty cover);
#  (2) the pilot's pause of the old lane-B child is removed (that process is long gone; its PID could be anyone's).
#   usage: c2m_segment.sh LABEL KC HALF
cd /Users/sumit/Github/conjecture_machine-check || exit 1
LBL=$1; KC=$2; HALF=$3
P13=/Users/sumit/Github/conjecture_machine-check/.venv313/bin/python
P14=/Users/sumit/Github/conjecture_machine/.venv/bin/python
export C2M_LABEL=$LBL
export BOX=P2 NVE_SPIN=3/5 R1_R0=1.35 R1_KC=$KC R1_HALF=$HALF R1_FLOATS=route1_floats_v7B_3_5.json R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel
read CODE BASE <<< $(${=P13} -I -c "import sys; sys.path.insert(0, 'scripts'); import _nve_c2m as M; print(M.CODE, M.BASE)" 2>/dev/null | tail -1)
[[ -n $CODE ]] || { echo "=== $LBL: the code hash could not be computed"; exit 1; }
echo "=== C2-M segment $LBL k_c $KC half $HALF code $CODE base $BASE HEAD $(git rev-parse --short HEAD) $(date '+%F %T')"
# the registration: an entry whose geometry guard failed is recorded and its segment is NOT run (glance F2)
GEO=$(${=P13} -I -c "import json; d = json.load(open('data/nve/eps/route1_floats_v7B_3_5.json')); print(1 if d['$KC']['geometry_ok'] is True else 0)" 2>/dev/null)
if [[ $GEO != 1 ]]; then
  echo "=== GEOMETRY NOT OK (or no floats entry) for $KC: the segment is not run $(date '+%F %T')"
  echo "=== C2M_SEGMENT_DONE $LBL NOT_RUN $(date '+%F %T')"
  exit 4
fi
COVJ=data/nve/route1_check/c2/c2m_${LBL}_cover.json
rm -f $COVJ                                  # glance F3: a stale cover file can never be read as this run's
echo "=== M3 (dry)"; ${=P13} -I -u scripts/_nve_c2m.py m3; echo "M3 rc $?"
rm -f $COVJ                                  # (M3 is dry and writes no cover; cleared again before the real one)
echo "=== cover $(date '+%F %T')"; ${=P13} -I -u scripts/_nve_c2m.py cover; echo "cover rc $?"
OK=$(${=P13} -I -c "import json; d = json.load(open('$COVJ')); print(1 if d['stop'] is None and d['n_leaves'] > 0 and d['code'] == '$CODE' else 0)" 2>/dev/null)
if [[ $OK != 1 ]]; then
  echo "=== COVER NOT ACCEPTED: the later stages are skipped $(date '+%F %T')"
  echo "=== C2M_SEGMENT_DONE $LBL STOPPED $(date '+%F %T')"
  exit 3
fi
echo "=== M1 $(date '+%F %T')"; ${=P13} -I -u scripts/_nve_c2m.py m1; echo "M1 rc $?"
echo "=== verdict (full controls) $(date '+%F %T')"; R1_FULLCTL=1 ${=P13} -I -u scripts/_nve_c2m.py verdict; echo "verdict rc $?"
for pl in M2F M2T0 M2T1 M4; do
  echo "=== control $pl $(date '+%F %T')"; C2M_PLANT=$pl R1_FULLCTL=1 ${=P13} -I -u scripts/_nve_c2m.py verdict; echo "control $pl rc $?"
done
echo "=== engine gate B $(date '+%F %T')"
NODES=data/nve/eps/route1_seg_nodes_$BASE.jsonl FLOATS=data/nve/eps/route1_floats_v7B_3_5.json \
  OUTJ=data/nve/eps/route1_seg_engineB_$BASE.jsonl R1_CODE=$CODE ${=P14} -I -u scripts/_nve_v7_engine_gate_B.py
echo "engine gate rc $?"
echo "=== C2M_SEGMENT_DONE $LBL $(date '+%F %T')"
