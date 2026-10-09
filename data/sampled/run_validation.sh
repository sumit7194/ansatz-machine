#!/bin/zsh
cd "${0:A:h}/../.." || exit 2
exec < /dev/null
O=data/sampled/validation.out
run() { .venv/bin/python -u scripts/_kt_sampled.py "$@" >> $O 2>&1; }
for s in 0 1 2 3; do run --metric ts2kerr:4/5 --rank 3 --denpow 1 --sector $s; done
run --metric ts2kerr:4/5 --rank 2 --denpow 1 --sector 0
for s in 0 1 2 3; do run --metric ts2kerr:4/5 --rank 4 --denpow 2 --sector $s; done
for s in 0 1 2 3; do run --metric ts2:4/5 --rank 2 --denpow 1 --sector $s; done
for s in 0 1 2 3; do run --metric ts2:4/5 --rank 3 --denpow 1 --sector $s; done
for s in 0 1 2 3; do run --metric ts2:4/5 --rank 4 --denpow 2 --sector $s; done
run --metric zv:2 --rank 4 --denpow 2 --sector 0
run --metric ts2:4/5 --rank 4 --denpow 2 --sector 0 --plant
run --metric ts2:4/5 --rank 4 --denpow 2 --sector 1 --plant
run --metric ts2:4/5 --rank 4 --denpow 2 --sector 0 --engine flint
run --metric ts2:4/5 --rank 4 --denpow 2 --sector 0 --prime 1
echo "ALL DONE $(date)" >> $O
