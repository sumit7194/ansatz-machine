#!/bin/zsh
# P4 T-tests, core B, after the Bridge's read and its S1-S7 fixes (seal: P4_SEAL.md, committed with this runner and its
# manifest before the run). Spin 9/10. Footprint logged every 600 s (fp.sh).
cd ~/GitHub/ansatz-air || exit 1
export PY313=.venv313/bin/python PY314=.venv/bin/python NVE_SPIN=9/10 R1_R0=1.2639
./fp.sh t6b $$ &
typeset -a OUT
t() { local nm=$1; shift; echo "=== $nm $(date '+%F %T')"; "$@"; local rc=$?; OUT+=("$nm rc=$rc"); echo "=== $nm rc $rc"; }
t P4r-floats-9/10 env R1_FLOATS=route1_floats_prod_9_10.json $PY314 -I -u scripts/_nve_route1_floats.py 3/20480 3/2560 3/320 3/40
t P4r-9/10 env R1_FLOATS=route1_floats_prod_9_10.json $PY313 -I -u scripts/_nve_route1_radius_probe.py 3/20480 3/2560 3/320 3/40
# U4b: pilot, the TOP dyadic segment at spin 9/10 ([1/20, 1/10], where P4-r predicts it is feasible), full controls;
# then the S4 file check
t U4b $PY313 -I -u scripts/_nve_route1_production.py pilot 1/20 1/10 Fk2
t FK2FILES-U4b env R1_KC=3/40 R1_HALF=1/40 R1_FLOATS=route1_floats_prod_9_10.json R1_RHOS=4 R1_MODE=Fk2 R1_TOLMODE=rel \
  $PY313 -I -u scripts/_nve_route1_t6.py fk2files
echo "=== T6B SUMMARY: ${(j:; :)OUT}"
echo "=== T6B_DONE $(date '+%F %T')"
