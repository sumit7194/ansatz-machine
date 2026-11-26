#!/bin/sh
# Pilot P1: the spin-3/5 v4 verdict at its own n = 12 (seal: data/nve/route1_check/P1_SEAL.md).
cd /Users/sumit/Github/conjecture_machine-check || exit 1
NVE_SPIN=3/5 R1_R0=1.35 nice -n 15 /Users/sumit/Github/quantum/sims/.venv/bin/python -I -u scripts/_nve_route1_v4_verdict.py || exit 1
echo P1_DONE
