#!/bin/zsh
cd "${0:A:h}/../.." || exit 2
exec < /dev/null
for s in kerr45 ts45 ts35 kerr35; do
  .venv/bin/python -u scripts/_ts_chaos_scan.py --system $s --workers 7 >> data/ts_chaos/scans.out 2>&1
done
echo "ALL DONE $(date)" >> data/ts_chaos/scans.out
