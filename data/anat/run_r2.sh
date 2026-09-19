#!/bin/bash
# Anatomy of the Carter obstruction at rank 2: which pieces of the sGB correction kill it?
cd "$(dirname "$0")/../.." || exit 1
for pieces in "" static rot l0 l2 rot,l0,l2 static,l0,l2 static,rot,l2 static,rot,l0; do
  tag=${pieces:-none}; tag=${tag//,/-}
  KT_SOLVER=rust KT_THREADS=2 KT_CKDIR=data/anat KT_SGB_PIECES="$pieces" \
    .venv/bin/python -u scripts/_kt_double.py --rank 2 --denpow 6 --margin 6 --control --sgb \
    > data/anat/r2_$tag.out 2>&1 < /dev/null
  echo "$tag: $(grep -E 'zeta chi\^[0-9] level' data/anat/r2_$tag.out | sed -E 's/.*level: ([0-9]+) of ([0-9]+).*/\1\/\2/' | tr '\n' ' ') $(grep -E 'Traceback|Error' data/anat/r2_$tag.out | head -1)"
done
