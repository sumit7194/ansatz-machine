#!/bin/zsh
# B1 at rank 6 (R6_ADDENDUM_sampled.md): TS p=4/5, den L^3, sectors 0..3, prime 0. One process at a time.
cd "${0:A:h}/../.." || exit 2
exec < /dev/null
O=data/sampled/r6.out
for s in 0 1 2 3; do
  /usr/bin/time -l .venv/bin/python -u scripts/_kt_sampled.py --metric ts2:4/5 --rank 6 --denpow 3 --sector $s --threads 8 >> $O 2>> $O.time
done
echo "ALL DONE $(date)" >> $O
