#!/bin/zsh
# Edge-link TS runs (slot granted 2026-11-18): T-BANDS then T-SWITCH', one at a time. Do not edit while running.
cd /Users/sumit/Github/conjecture_machine
nice -n 10 .venv/bin/python scripts/_ts_edge.py tbands ts
nice -n 10 .venv/bin/python scripts/_ts_edge.py tswitch ts
echo "EDGE TS DONE $(date)"
