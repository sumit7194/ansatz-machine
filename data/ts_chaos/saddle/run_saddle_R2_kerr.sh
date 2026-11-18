#!/bin/zsh
# Addendum 2 step 1: Kerr control at R2 (slot granted by the Bridge 2026-11-18). Do not edit while running.
cd /Users/sumit/Github/conjecture_machine
nice -n 10 .venv/bin/python scripts/_ts_saddle.py run kerr 2 R2
echo "STEP1 DONE $(date)"
