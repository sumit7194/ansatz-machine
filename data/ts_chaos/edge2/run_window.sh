#!/bin/zsh
# Edge-link v2' TS window run (slot granted 2026-11-19, overnight). Resumable from the history checkpoint. Do not edit while running.
cd /Users/sumit/Github/conjecture_machine
nice -n 10 .venv/bin/python scripts/_ts_edge2.py window
echo "WINDOW DONE $(date)"
