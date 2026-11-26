#!/bin/zsh
# Pilot P1: the spin-3/5 v4 verdict at its own n = 12 (seal: data/nve/route1_check/P1_SEAL.md, dfa8d48).
# Runs under .venv313 (Python 3.13.18, the committed run's packages): the registration now pins the Python minor version.
# Refuses to start if its node file exists, so no node is read back from an earlier run.
cd ~/GitHub/ansatz-air || exit 1
[[ -e data/nve/eps/route1_seg_nodes_arb_v4cert.jsonl ]] && { echo "REFUSE: node file exists"; exit 1; }
echo "=== P1 $(date '+%F %T') $(.venv313/bin/python -V)"
NVE_SPIN=3/5 R1_R0=1.35 .venv313/bin/python -I -u scripts/_nve_route1_v4_verdict.py || exit 1
echo "=== P1_DONE $(date '+%F %T')"
