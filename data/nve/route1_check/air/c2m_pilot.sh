#!/bin/zsh
# C2-M pilot (C2_M_REGISTRATION.md with addendum C2-M-1 and erratum C2-M-2), ONE attempt per box.
#   usage: c2m_pilot.sh P2|P3
# M3 (dry) -> the cover (lane B's sample process paused for the 2 cover workers) -> M1 -> the verdict with v6's
# full controls -> M2F, M2T0, M2T1, M4 -> the engine gate. Run under air/v7_job.sh (pause-only guard, nice 10).
cd /Users/sumit/Github/conjecture_machine-check || exit 1
B=$1
P13=/Users/sumit/Github/conjecture_machine-check/.venv313/bin/python
P14=/Users/sumit/Github/conjecture_machine/.venv/bin/python
if [[ $B == P2 ]]; then KC=83/20; HALF=1/20; else KC=59979/14000; HALF=1/2000; fi
export BOX=$B NVE_SPIN=3/5 R1_R0=1.35 R1_KC=$KC R1_HALF=$HALF R1_FLOATS=route1_floats_v7B_3_5.json R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel
read CODE BASE <<< $(${=P13} -I -c "import sys; sys.path.insert(0, 'scripts'); import _nve_c2m as M; print(M.CODE, M.BASE)" 2>/dev/null | tail -1)
[[ -n $CODE ]] || exit 1
echo "=== C2-M pilot $B k_c $KC half $HALF code $CODE base $BASE HEAD $(git rev-parse --short HEAD) $(date '+%F %T')"
echo "=== M3 (dry)"; ${=P13} -I -u scripts/_nve_c2m.py m3; echo "M3 rc $?"
LBK=$(pgrep -P 19860 2>/dev/null)
[[ -n $LBK ]] && kill -STOP $LBK && echo "$(date '+%F %T') PAUSE lane B child $LBK for the C2-M $B cover" >> data/nve/route1_check/v7/guard_c2_step0p_B.log
echo "=== cover $(date '+%F %T')"; ${=P13} -I -u scripts/_nve_c2m.py cover; echo "cover rc $?"
[[ -n $LBK ]] && kill -CONT $LBK && echo "$(date '+%F %T') RESUME lane B child $LBK" >> data/nve/route1_check/v7/guard_c2_step0p_B.log
echo "=== M1 $(date '+%F %T')"; ${=P13} -I -u scripts/_nve_c2m.py m1; echo "M1 rc $?"
echo "=== verdict (full controls) $(date '+%F %T')"; R1_FULLCTL=1 ${=P13} -I -u scripts/_nve_c2m.py verdict; echo "verdict rc $?"
for pl in M2F M2T0 M2T1 M4; do
  echo "=== control $pl $(date '+%F %T')"; C2M_PLANT=$pl R1_FULLCTL=1 ${=P13} -I -u scripts/_nve_c2m.py verdict; echo "control $pl rc $?"
done
echo "=== engine gate B $(date '+%F %T')"
NODES=data/nve/eps/route1_seg_nodes_$BASE.jsonl FLOATS=data/nve/eps/route1_floats_v7B_3_5.json \
  OUTJ=data/nve/eps/route1_seg_engineB_$BASE.jsonl R1_CODE=$CODE ${=P14} -I -u scripts/_nve_v7_engine_gate_B.py
echo "engine gate rc $?"
echo "=== C2M_PILOT_DONE $B $(date '+%F %T')"
