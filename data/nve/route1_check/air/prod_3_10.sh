#!/bin/zsh
# Route (i) production, spin 3/10 (seal: PROD_SEAL.md, committed with this runner and its manifest before launch).
# One process at a time (the driver waits on one child), nice 15 under job.sh; footprint logged every 600 s (fp.sh).
cd ~/GitHub/ansatz-air || exit 1
export PY313=.venv313/bin/python PY314=.venv/bin/python NVE_SPIN=3/10 R1_R0=1.1492 PROD_TOP=3 PROD_EPS=2.79e-3 PROD_DMAX=2
./fp.sh prod_3_10 $$ &
echo "=== PROD 3/10 $(date '+%F %T')"
$PY313 -I -u scripts/_nve_route1_production.py
echo "=== PROD_3_10 rc $? $(date '+%F %T')"
