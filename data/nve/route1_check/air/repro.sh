#!/bin/zsh
# (a) reproduction of the spin-9/10 v4 certificate (c2dd39c) on the Air: proof stage from nothing (no rows or dqck
# file exists here), then the unchanged v4 verdict wrapper on the committed node file. Doubles as the Air identity test.
cd ~/GitHub/ansatz-air || exit 1
export NVE_SPIN=9/10 R1_R0=1.2639
echo "=== prove $(date '+%F %T')"
.venv/bin/python -I -u scripts/_nve_route1_segment_v4.py || exit 1
echo "=== verdict $(date '+%F %T')"
.venv/bin/python -I -u scripts/_nve_route1_v4_verdict.py || exit 1
echo "=== REPRO_DONE $(date '+%F %T')"
