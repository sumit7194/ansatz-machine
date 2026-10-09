#!/bin/zsh
# Full-size engine sabotage (Bridge 01:45 guard 2): after the r6 sectors, r6 s0 with a planted duplicate column -> must be 17.
cd "${0:A:h}/../.." || exit 2
exec < /dev/null
while kill -0 $1 2>/dev/null; do sleep 30; done
/usr/bin/time -l .venv/bin/python -u scripts/_kt_sampled.py --metric ts2:4/5 --rank 6 --denpow 3 --sector 0 --plant --threads 8 >> data/sampled/r6_plant.out 2>> data/sampled/r6_plant.out.time
echo "ALL DONE $(date)" >> data/sampled/r6_plant.out
