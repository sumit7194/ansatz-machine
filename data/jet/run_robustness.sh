#!/bin/zsh
# Bridge's checks (02:35): more points INSIDE the physical domain (x>1, |y|<1), one deeper prolongation, second prime.
cd "${0:A:h}/../.." || exit 2
exec < /dev/null
O=data/jet/robustness.out
for spec in "ts2:4/5" "ts2:3/5"; do for d in $(seq 1 10); do for pt in 5/4,1/2 2,1/5; do
  .venv/bin/python -u scripts/_kt_jet.py --metric $spec --rank $d --point $pt >> $O 2>&1; done; done; done
for d in 4 6 8; do .venv/bin/python -u scripts/_kt_jet.py --metric ts2:4/5 --rank $d --M $((d+1)) --point 3,1/3 >> $O 2>&1; done
for d in 6 8 10; do .venv/bin/python -u scripts/_kt_jet.py --metric ts2:4/5 --rank $d --point 3,1/3 --prime 1 >> $O 2>&1; done
.venv/bin/python -u scripts/_kt_jet.py --metric kerr:1:1/2 --rank 4 --M 5 --point 3,1/3 >> $O 2>&1
echo "ALL DONE $(date)" >> $O
