#!/bin/zsh
cd "${0:A:h}/../.." || exit 2
exec < /dev/null
for m in p1 p2; do
  .venv/bin/python -u scripts/_kt_jet_mn.py --mn $m --ranks 1-10 --points P1,P2 --threads 2 >> data/jet/mn_targets.out 2>&1
done
echo "ALL DONE $(date)" >> data/jet/mn_targets.out
