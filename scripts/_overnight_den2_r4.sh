#!/bin/bash
# Wait for the mod-p gate, and launch delta=2 rank 4 ONLY if it reproduced the known answer.
#
# The gate is not a formality. solve_kt_modp changes the numerical path -- rows are reduced mod p
# during assembly rather than held as exact rationals -- so it must return delta=1 rank 2 den^2 = 5,
# a rung whose answer is already known from the old path, before it is trusted on rank 4, whose
# answer is not known. If it returns anything else the correct outcome is NO RUN and a finding.
cd /Users/sumit/Github/conjecture_machine
G=data/kt_modp_verify.out
L=data/overnight_r4.log
say(){ echo "$(date '+%m-%d %H:%M:%S')  $*" >> "$L"; }

for _ in $(seq 1 180); do
  grep -q "den\^2: DIMENSION" "$G" 2>/dev/null && break
  grep -qE "PRIMES DISAGREE|Traceback|Killed" "$G" 2>/dev/null && break
  pgrep -f "scripts/_kt_zv_den2.py" >/dev/null || break
  sleep 20
done

V=$(grep -o "DIMENSION [0-9][0-9]*" "$G" 2>/dev/null | tail -1 | awk '{print $2}')
if [ "$V" != "5" ]; then
  say "GATE FAILED (returned '${V:-nothing}', known answer 5). NOT launching rank 4."
  say "That is the correct outcome: an unverified numerical path must not be used on an unknown rung."
  exit 0
fi
say "GATE PASSED: delta=1 rank 2 den^2 = 5 on the new path. Launching delta=2 rank 4, pre-registered 9."

.venv/bin/python scripts/_kt_zv_den2.py 2 4 --modp > data/kt_zvd2_d2_r4.out 2>&1
R=$(grep -o "DIMENSION [0-9][0-9]*" data/kt_zvd2_d2_r4.out 2>/dev/null | tail -1 | awk '{print $2}')
if [ -z "$R" ]; then say "rank 4 produced no DIMENSION line -- see data/kt_zvd2_d2_r4.out"
elif [ "$R" -lt 8 ]; then say "rank 4 = $R, BELOW den^1's 8 -- CONTAINMENT VIOLATED, run condemned"
elif [ "$R" = "9" ]; then say "PREREG PASS: delta=2 rank 4 den^2 = 9 as predicted. Six of six."
elif [ "$R" -gt 9 ]; then say "*** rank 4 = $R, ABOVE predicted 9 -- CANDIDATE IRREDUCIBLE KILLING TENSOR ***"
else say "PREREG FAIL: rank 4 = $R, predicted 9 (den^1 was 8) -- investigate"; fi
