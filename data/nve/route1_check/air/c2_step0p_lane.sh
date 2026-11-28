#!/bin/zsh
# C2 step 0' (C2_REGISTRATION.md, addendum C2-3), one lane. Lane A: the six drives (P2 then P1, R/5, R/10, R/20), then
# its half of the samples; lane B: the other half of the samples. Run under v7_job.sh (pause-only guard, nice 10).
#   usage: c2_step0p_lane.sh A|B
cd /Users/sumit/Github/conjecture_machine-check || exit 1
lane=$1
echo "lane $lane start $(date '+%F %T'); HEAD $(git rev-parse --short HEAD); driver sha256 $(shasum -a 256 scripts/c2_capd/build/c2_driver_id | cut -c1-16)"
export NVE_SPIN=3/5 R1_R0=1.35 R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel C2_VARIANT=_id C2_TOL=1e-15 C2_ORDER=20
P=.venv313/bin/python
envfor() {
  if [[ $1 == P1 ]]; then export BOX=P1 R1_KC=79/20 R1_HALF=1/20 R1_FLOATS=route1_floats_v7p_3_5.json
  else export BOX=P2 R1_KC=83/20 R1_HALF=1/20 R1_FLOATS=route1_floats_v7B_3_5.json; fi
}
if [[ $lane == A ]]; then
  for b in P2 P1; do for kd in 5 10 20; do
    envfor $b; C2_KDIV=$kd ${=P} -I -u scripts/_nve_c2_capd.py drive; echo "drive $b R/$kd rc $?"
  done; done
  sl=0/2
else
  sl=1/2
fi
for b in P2 P1; do for kd in 5 10 20; do
  envfor $b; SLICE=$sl C2_KDIV=$kd ${=P} -I -u scripts/_nve_c2_capd.py samples; echo "samples $b R/$kd slice $sl rc $?"
done; done
echo "lane $lane done $(date '+%F %T')"
