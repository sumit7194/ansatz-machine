#!/bin/zsh
# C2-TM controls T3-T5 (C2_TM_REGISTRATION.md) on one box, sequentially. Run under air/v7_job.sh (pause-only, nice 10).
cd /Users/sumit/Github/conjecture_machine-check || exit 1
B=$1
if [[ $B == P2 ]]; then export R1_KC=83/20 R1_FLOATS=route1_floats_v7B_3_5.json; else export R1_KC=79/20 R1_FLOATS=route1_floats_v7p_3_5.json; fi
export BOX=$B NVE_SPIN=3/5 R1_R0=1.35 R1_HALF=1/20 R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel
echo "=== C2-TM controls $B HEAD $(git rev-parse --short HEAD) $(date '+%F %T')"
for t in T3 T4 T5; do .venv313/bin/python -I -u scripts/_nve_c2tm_controls.py $t; echo "control $t rc $?"; done
echo "=== C2TM_CONTROLS_DONE $B $(date '+%F %T')"
