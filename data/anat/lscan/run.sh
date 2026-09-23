#!/usr/bin/env bash
cd "$(dirname "$0")/../../.." || exit 2
exec < /dev/null
for L in 1 3 5 2 4 6 7; do
  out=data/anat/lscan/r4_o$L.out
  KT_SOLVER=rust /usr/bin/time -l bash -c "exec .venv/bin/python -u scripts/_kt_pole_reduced.py --rank 4 --denpow 7 --margin 4 --slots o${L}tphi,o${L}rphi,o${L}yphi > '$out' 2>&1" 2> "$out.time"
  echo "l=$L exit=$? footprint=$(awk '/peak memory footprint/{printf "%.2f GB",$1/1073741824}' $out.time)"
done
echo "ALL DONE"
