#!/bin/zsh
# TS2 p-sweep jet runs (pre-registration 13fe05e): Kerr control d=1..4 at PA, then TS d=1..8 at PA and PB, per p.
cd "${0:A:h}/../.." || exit 2
exec < /dev/null
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
J=".venv/bin/python -u scripts/_kt_jet.py --threads 2"
for p in 5/13 12/13 8/17 15/17 20/29 21/29 7/25 24/25; do
  for d in 1 2 3 4; do $J --metric ts2kerr:$p --rank $d --point 3,1/3 >> data/jet/psweep.out 2>&1; done
  for pt in 3,1/3 17/10,3/5; do
    for d in 1 2 3 4 5 6 7 8; do $J --metric ts2:$p --rank $d --point $pt >> data/jet/psweep.out 2>&1; done
  done
done
echo "ALL DONE $(date)" >> data/jet/psweep.out
