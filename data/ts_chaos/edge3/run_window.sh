#!/bin/zsh
# Edge-link v3 TS window run (Sumit's direct go 2026-11-19). Resumable from the history checkpoint. Do not edit while running.
cd /Users/sumit/Github/conjecture_machine
nice -n 10 .venv/bin/python scripts/_ts_edge3.py window
echo "V3 WINDOW DONE $(date)"
