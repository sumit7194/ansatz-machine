#!/bin/zsh
# C2 step 0'' (addendum C2-4 (c), with errata E1, E2): the six drives ONCE (P2 then P1; R/5, R/10, R/20), with the C2-3
# bar, settings and grids unchanged; then the judge wherever the samples are complete. Lane B's sample process is
# paused for the drives (the 2-core limit) and resumed after. Run under v7_job.sh (pause-only guard, nice 10).
cd /Users/sumit/Github/conjecture_machine-check || exit 1
echo "step0pp start $(date '+%F %T'); HEAD $(git rev-parse --short HEAD); driver sha256 $(shasum -a 256 scripts/c2_capd/build/c2_driver_v2 | cut -c1-16)"
LBK=$(pgrep -P 19860)
[[ -n $LBK ]] && kill -STOP $LBK && echo "$(date '+%F %T') PAUSE lane B child $LBK for step 0'' drives" >> data/nve/route1_check/v7/guard_c2_step0p_B.log
export NVE_SPIN=3/5 R1_R0=1.35 R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel C2_STAGE=step0pp C2_VARIANT=_v2 C2_TOL=1e-15 C2_ORDER=20
P=.venv313/bin/python
envfor() {
  if [[ $1 == P1 ]]; then export BOX=P1 R1_KC=79/20 R1_HALF=1/20 R1_FLOATS=route1_floats_v7p_3_5.json
  else export BOX=P2 R1_KC=83/20 R1_HALF=1/20 R1_FLOATS=route1_floats_v7B_3_5.json; fi
}
for b in P2 P1; do for kd in 5 10 20; do
  envfor $b; C2_KDIV=$kd ${=P} -I -u scripts/_nve_c2_capd.py drive; echo "drive $b R/$kd rc $?"
done; done
[[ -n $LBK ]] && kill -CONT $LBK && echo "$(date '+%F %T') RESUME lane B child $LBK" >> data/nve/route1_check/v7/guard_c2_step0p_B.log
for b in P2 P1; do for kd in 5 10 20; do
  envfor $b
  n=$(wc -l < data/nve/route1_check/c2/step0p_${b}_k${kd}_samples.jsonl 2>/dev/null || echo 0)
  if [[ $n -ge 81 ]]; then C2_KDIV=$kd ${=P} -I -u scripts/_nve_c2_capd.py judge; echo "judge $b R/$kd rc $?"
  else echo "judge $b R/$kd deferred (samples $n/81)"; fi
done; done
echo "step0pp done $(date '+%F %T')"
