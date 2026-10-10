#!/bin/zsh
cd "${0:A:h}/../.." || exit 2
exec < /dev/null
for s in kerr35 ts45 ts35 kerr45; do
  .venv/bin/python -u scripts/_ts_chaos_confirm.py data/ts_chaos/bscan_${s}_v2.json 7 >> data/ts_chaos/confirm_A5.out 2>&1
done
echo "ALL DONE $(date)" >> data/ts_chaos/confirm_A5.out
