#!/bin/zsh
# Probe (a) (seal: PROBE_A_SEAL.md, committed with this runner before it runs): V.laurent at k = 3 .. 3.9, spins 3/5, 9/10.
cd ~/GitHub/ansatz-air || exit 1
for s in 3/5 9/10; do
  echo "=== probe (a) spin $s $(date '+%F %T') $(.venv313/bin/python -V)"
  NVE_SPIN=$s .venv313/bin/python -I -u scripts/_nve_route1_laurent_probe.py || exit 1
done
echo "=== PROBEA_DONE $(date '+%F %T')"
