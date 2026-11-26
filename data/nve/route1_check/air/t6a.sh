#!/bin/zsh
# P4 T-tests, core A, after the Bridge's read and its S1-S7 fixes (seal: P4_SEAL.md, committed with this runner and its
# manifest before the run). Air, one process at a time, nice 15 under job.sh; footprint logged every 600 s (fp.sh).
# A failing test does not stop the battery; the summary line lists every outcome.
cd ~/GitHub/ansatz-air || exit 1
E=data/nve/eps
export PY313=.venv313/bin/python PY314=.venv/bin/python
./fp.sh t6a $$ &
typeset -a OUT
t() { local nm=$1; shift; echo "=== $nm $(date '+%F %T')"; "$@"; local rc=$?; OUT+=("$nm rc=$rc"); echo "=== $nm rc $rc"; }
t U5 $PY313 -I -u scripts/_nve_route1_production_test.py
t SYNTH env NVE_SPIN=3/5 R1_R0=1.35 $PY313 -I -u scripts/_nve_route1_t6.py synth
# P4-r at spin 3/5: floats at two dyadic centres (into the production floats file), then the radius and trace probe
export NVE_SPIN=3/5 R1_R0=1.35
t P4r-floats-3/5 env R1_FLOATS=route1_floats_prod_3_5.json $PY314 -I -u scripts/_nve_route1_floats.py 3/1280 3/40
t P4r-3/5 env R1_FLOATS=route1_floats_prod_3_5.json $PY313 -I -u scripts/_nve_route1_radius_probe.py 3/1280 3/40
# U1: v6 on [1, 1.1] with v5's settings, full controls; then the engine gate (both directions), u1 and u6
export R1_KC=21/20 R1_HALF=1/20 R1_FLOATS=route1_floats.json R1_RHOS=3,4,5,6.5 R1_MODE=F R1_TOLMODE=abs R1_FULLCTL=1
t U1-prove $PY313 -I -u scripts/_nve_route1_segment_v6.py prove
t U1-verdict $PY313 -I -u scripts/_nve_route1_segment_v6.py verdict
t GATE $PY313 -I -u scripts/_nve_route1_t6.py gate
t U1 $PY313 -I -u scripts/_nve_route1_t6.py u1
t U6 $PY313 -I -u scripts/_nve_route1_t6.py u6
# U3: F/k^2 on [1, 1.1], the production tolerance, rho 4, full controls; then the S4 file check
export R1_RHOS=4 R1_MODE=Fk2 R1_TOLMODE=rel
t U3-prove $PY313 -I -u scripts/_nve_route1_segment_v6.py prove
t U3-verdict $PY313 -I -u scripts/_nve_route1_segment_v6.py verdict
t U3 $PY313 -I -u scripts/_nve_route1_t6.py u3
t FK2FILES-U3 $PY313 -I -u scripts/_nve_route1_t6.py fk2files
# U7: a moved-segment known answer: v6 at k_c = 2 (rho 4, v5's absolute tolerance, P3's floats) against P3's row
unset R1_FULLCTL
export R1_KC=2 R1_HALF=1/20 R1_FLOATS=route1_floats_p3_3_5.json R1_RHOS=4 R1_MODE=F R1_TOLMODE=abs
t U7-prove $PY313 -I -u scripts/_nve_route1_segment_v6.py prove
t U7-verdict $PY313 -I -u scripts/_nve_route1_segment_v6.py verdict
t U7 $PY313 -I -u scripts/_nve_route1_t6.py u7
unset R1_KC R1_HALF R1_FLOATS R1_RHOS R1_MODE R1_TOLMODE R1_FULLCTL
# U4a: pilot, the lowest dyadic segment at spin 3/5, through the production stages (floats, prove, verdict with the
# full controls, engine gate); then the S4 file check
t U4a $PY313 -I -u scripts/_nve_route1_production.py pilot 1/640 1/320 Fk2
t FK2FILES-U4a env R1_KC=3/1280 R1_HALF=1/1280 R1_FLOATS=route1_floats_prod_3_5.json R1_RHOS=4 R1_MODE=Fk2 R1_TOLMODE=rel \
  $PY313 -I -u scripts/_nve_route1_t6.py fk2files
echo "=== T6A SUMMARY: ${(j:; :)OUT}"
echo "=== T6A_DONE $(date '+%F %T')"
