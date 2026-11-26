#!/bin/sh
# (a) reproduction of the spin-9/10 v4 certificate (c2dd39c) on a clean checkout, by a non-author of v4.
# The committed checkpoint files (rows, dqck) are moved aside first, so the proof stage recomputes every row
# and every per-step bound instead of reading them back. Then the unchanged v4 verdict wrapper runs on the
# committed node file (no new node evaluations). One process at a time, nice 15.
cd /Users/sumit/Github/conjecture_machine-check || exit 1
PY=/Users/sumit/Github/quantum/sims/.venv/bin/python
export NVE_SPIN=9/10 R1_R0=1.2639
date
nice -n 15 "$PY" -I -u scripts/_nve_route1_segment_v4.py || exit 1
date
nice -n 15 "$PY" -I -u scripts/_nve_route1_v4_verdict.py || exit 1
date
echo REPRO_DONE
