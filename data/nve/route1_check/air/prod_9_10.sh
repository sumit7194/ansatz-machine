#!/bin/zsh
# Route (i) production, spin 9/10 (seal: PROD_SEAL.md, committed with this runner and its manifest before launch).
# One process at a time (the driver waits on one child), nice 15 under job.sh; footprint logged every 600 s (fp.sh).
cd ~/GitHub/ansatz-air || exit 1
export PY313=.venv313/bin/python PY314=.venv/bin/python NVE_SPIN=9/10 R1_R0=1.2639 PROD_TOP=2 PROD_EPS=1.06e-4 PROD_DMAX=2
./fp.sh prod_9_10 $$ &
echo "=== PROD 9/10 $(date '+%F %T')"
$PY313 -I -u scripts/_nve_route1_production.py
echo "=== PROD_9_10 rc $? $(date '+%F %T')"
