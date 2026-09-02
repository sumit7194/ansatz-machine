#!/bin/bash
# Overnight chain: validate the perturbation solver, then use it. Each stage GATES the next --
# a stage that fails stops the chain rather than letting a later result rest on it.
cd /Users/sumit/Github/conjecture_machine
L=data/kt_overnight.log
say(){ echo "$(date '+%m-%d %H:%M:%S')  $*" >> "$L"; }
say "=== OVERNIGHT CHAIN START ==="

# ---- STAGE A: the discriminating control. A generic stationary axisymmetric perturbation must
# KILL Carter, leaving only the reducible floor of 4. If this returns 5, the solver cannot detect
# a broken symmetry and every sGB verdict it could ever print would be worthless.
# A0 first: the SAME control at denpow 1 (810 columns instead of 1690) runs in ~20 min rather
# than ~4.5 h. Last night's failure was a mis-specified control that took 4.5 h to surface; a
# cheap version of the same question first means a bad control costs minutes.
say "STAGE A0: fast version of the control at denpow 1 (cheap failure first)"
s=$(date +%s)
.venv/bin/python scripts/_kt_perturb.py --rank 2 --denpow 1 --selftest --only 2 \
  > data/kt_perturb_selftest_d1.out 2>&1
A0=$(grep -c "SELFTEST PASSED" data/kt_perturb_selftest_d1.out)
say "  stage A0: PASSED=$A0  ($(( $(date +%s) - s ))s)  $(grep -oE 'background [0-9]+, surviving [0-9]+, expected [0-9]+ -> [A-Z]+' data/kt_perturb_selftest_d1.out | tail -1)"
if [ "$A0" != "1" ]; then
  grep -E "NOT REPRESENTABLE|surviving" data/kt_perturb_selftest_d1.out | while read -r l; do say "    $l"; done
  say "  CHAIN STOPPED at A0: the cheap control already fails, so the expensive one would too."
  say "=== OVERNIGHT CHAIN END (blocked at A0) ==="
  exit 1
fi

say "STAGE A: same control at denpow 2 (the setting real runs use)"
s=$(date +%s)
.venv/bin/python scripts/_kt_perturb.py --rank 2 --denpow 2 --selftest --only 2 \
  > data/kt_perturb_selftest.out 2>&1
A=$(grep -c "SELFTEST PASSED" data/kt_perturb_selftest.out)
say "  stage A: SELFTEST PASSED=$A  ($(( $(date +%s) - s ))s)"
grep -oE "background [0-9]+, surviving [0-9]+, expected [0-9]+ -> [A-Z]+" data/kt_perturb_selftest.out \
  | while read -r line; do say "    $line"; done
if [ "$A" != "1" ]; then
  say "  CHAIN STOPPED: the solver is not validated, so nothing downstream would mean anything."
  say "=== OVERNIGHT CHAIN END (blocked at A) ==="
  exit 1
fi

# ---- STAGE B: positive control on REAL sGB data. The static (chi^0) solution is still
# spherically symmetric, so every background tensor must survive. Tests the verified metric
# through the validated solver.
say "STAGE B: static sGB (chi^0) must preserve EVERYTHING (spherical symmetry intact)"
s=$(date +%s)
# denpow 4, NOT 2. The sGB correction's g^rr entry has denominator 15*x^7 while
# L = x^2 (x-2)(y^2-1) reaches only x^4 at L^2 and x^6 at L^3, so H1 is not representable below
# L^4. At denpow 2 the run "passed" while silently testing nothing -- the ansatz could not even
# hold Lsq, and a spherically symmetric perturbation preserves everything in ANY ansatz.
.venv/bin/python scripts/_kt_perturb.py --rank 2 --denpow 4 --sgb-static \
  > data/kt_perturb_sgbstatic.out 2>&1
B=$(grep -c "CONTROL PASSED" data/kt_perturb_sgbstatic.out)
say "  stage B: CONTROL PASSED=$B  ($(( $(date +%s) - s ))s)  $(grep -oE 'background [0-9]+, surviving [0-9]+' data/kt_perturb_sgbstatic.out | tail -1)"
if [ "$B" != "1" ]; then
  say "  CHAIN STOPPED at B: either the pipeline or the transcribed metric is wrong."
  say "=== OVERNIGHT CHAIN END (blocked at B) ==="
  exit 1
fi

# ---- STAGE C: derive the O(chi) rotating correction from the field equations, so the open
# question can be asked on a metric no one hand-transcribed.
say "STAGE C: derive the O(zeta chi) sGB correction from the field equations"
s=$(date +%s)
.venv/bin/python scripts/_kt_sgb_derive.py --nterms 8 > data/kt_sgb_derive.out 2>&1
C=$(grep -cE "MATCHES our derivation" data/kt_sgb_derive.out)
say "  stage C: derivation matched a published reading=$C  ($(( $(date +%s) - s ))s)"
grep -E "W\(r\) =|MATCHES|differs|NO SOLUTION" data/kt_sgb_derive.out | while read -r line; do say "    $line"; done
say "=== OVERNIGHT CHAIN END ==="
