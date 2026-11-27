#!/bin/zsh
# Top-of-reach check at spin 4/5 (seal: P4R_3_10_4_5_RESULT.md, section "Top check"; committed with this runner and its
# manifest before the run): floats at k_c 59/20, then v6 PROVE only on the production's last segment [29/10, 3], with
# exactly the driver's env_for() settings, so production reuses this checkpoint. No verdict. One process, nice 15.
cd ~/GitHub/ansatz-air || exit 1
export PY313=.venv313/bin/python PY314=.venv/bin/python NVE_SPIN=4/5 R1_R0=1.3382
./fp.sh top_4_5 $$ &
export R1_KC=59/20 R1_HALF=1/20 R1_FLOATS=route1_floats_prod_4_5.json R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel
echo "=== TOP 4/5 floats $(date '+%F %T')"
$PY314 -I -u scripts/_nve_route1_floats.py 59/20 || exit 1
echo "=== TOP 4/5 prove $(date '+%F %T')"
$PY313 -I -u scripts/_nve_route1_segment_v6.py prove
echo "=== TOP_DONE 4/5 rc $? $(date '+%F %T')"
