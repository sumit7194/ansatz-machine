#!/usr/bin/env bash
cd "$(dirname "$0")/../../.." || exit 2
exec < /dev/null
run() { tag=$1; shift; L=$1; shift; out=data/anat/lscan/r4_o${L}_$tag.out
  KT_SOLVER=rust /usr/bin/time -l bash -c "exec .venv/bin/python -u scripts/_kt_pole_reduced.py --rank 4 $* --slots o${L}tphi,o${L}rphi,o${L}yphi > '$out' 2>&1" 2> "$out.time"
  echo "l=$L $tag exit=$? footprint=$(awk '/peak memory footprint/{printf "%.2f GB",$1/1073741824}' $out.time)"; }
run m8 2 --denpow 7 --margin 8
run p1 2 --denpow 7 --margin 4 --prime 1
for L in 6 7; do run m8 $L --denpow 7 --margin 8; run d9 $L --denpow 9 --margin 4; done
echo "ALL DONE"
