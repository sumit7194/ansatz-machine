#!/bin/zsh
# P4-r small-k radius probe at spin 4/5 (seal: P4R_3_10_4_5_SEAL.md, committed with this runner and its manifest before
# the run). Air, one process at a time, nice 15 under job.sh; footprint logged every 600 s (fp.sh). Writes the floats
# entries into the production floats file (as P4-r did for 3/5 and 9/10) and nothing else but its log.
cd ~/GitHub/ansatz-air || exit 1
export PY313=.venv313/bin/python PY314=.venv/bin/python NVE_SPIN=4/5 R1_R0=1.3382
./fp.sh p4r_4_5 $$ &
echo "=== P4R 4/5 floats $(date '+%F %T')"
env R1_FLOATS=route1_floats_prod_4_5.json $PY314 -I -u scripts/_nve_route1_floats.py 1/1280 3/2560 3/1280 3/40 || exit 1
echo "=== P4R 4/5 probe $(date '+%F %T')"
env R1_FLOATS=route1_floats_prod_4_5.json $PY313 -I -u scripts/_nve_route1_radius_probe.py 1/1280 3/2560 3/1280 3/40
echo "=== P4R_DONE 4/5 rc $? $(date '+%F %T')"
