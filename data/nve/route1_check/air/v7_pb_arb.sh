#!/bin/zsh
cd /Users/sumit/Github/conjecture_machine-check || exit 1
NVE_SPIN=3/5 R1_R0=1.35 /Users/sumit/Github/conjecture_machine-check/.venv313/bin/python -I -u scripts/_nve_v7_pb.py arb
