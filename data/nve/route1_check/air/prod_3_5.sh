#!/bin/zsh
# Route (i) production, spin 3/5 (seal: PROD_SEAL.md, committed with this runner and its manifest before launch).
# One process at a time (the driver waits on one child), nice 15 under job.sh; footprint logged every 600 s (fp.sh).
cd ~/GitHub/ansatz-air || exit 1
export PY313=.venv313/bin/python PY314=.venv/bin/python NVE_SPIN=3/5 R1_R0=1.35 PROD_TOP=3 PROD_EPS=1.92e-3 PROD_DMAX=2
./fp.sh prod_3_5 $$ &
echo "=== PROD 3/5 $(date '+%F %T')"
$PY313 -I -u scripts/_nve_route1_production.py
echo "=== PROD_3_5 rc $? $(date '+%F %T')"
