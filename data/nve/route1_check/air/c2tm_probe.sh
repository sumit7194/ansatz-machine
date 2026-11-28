#!/bin/zsh
# C2-TM probe (C2_TM_REGISTRATION.md, "Probe"): one disc. usage: c2tm_probe.sh P2|P1 sub|whole. Under v7_job.sh.
cd /Users/sumit/Github/conjecture_machine-check || exit 1
B=$1; KIND=$2
if [[ $B == P2 ]]; then export R1_KC=83/20 R1_FLOATS=route1_floats_v7B_3_5.json; else export R1_KC=79/20 R1_FLOATS=route1_floats_v7p_3_5.json; fi
export BOX=$B KIND=$KIND NVE_SPIN=3/5 R1_R0=1.35 R1_HALF=1/20 R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel
echo "=== C2-TM probe $B $KIND HEAD $(git rev-parse --short HEAD) $(date '+%F %T')"
.venv313/bin/python -I -u scripts/_nve_c2tm_probe.py; echo "probe rc $?"
echo "=== C2TM_PROBE_DONE $B $KIND $(date '+%F %T')"
