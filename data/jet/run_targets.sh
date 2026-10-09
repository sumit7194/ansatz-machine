#!/bin/zsh
# New territory per data/jet/PREREGISTRATION.md (sealed f3a1d3b): TS p=4/5 ranks 1..10, TS p=3/5 ranks 8..10, two points.
cd "${0:A:h}/../.." || exit 2
exec < /dev/null
O=data/jet
for spec in "ts2:4/5" "ts2:3/5"; do
  lo=1; [ $spec = "ts2:3/5" ] && lo=8
  for d in $(seq $lo 10); do for pt in 1/2,2 3,1/3; do
    .venv/bin/python -u scripts/_kt_jet.py --metric $spec --rank $d --point $pt >> $O/targets.out 2>&1
  done; done
done
echo "ALL DONE $(date)" >> $O/targets.out
