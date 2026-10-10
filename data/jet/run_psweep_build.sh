#!/bin/zsh
# Build + vacuum-verify the 8 new TS2 metrics and their Kerr controls, sequentially, one core.
cd "${0:A:h}/../.." || exit 2
exec < /dev/null
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1
for t in 2/3 3/5 3/7 2/5 1/4 1/5 1/7 3/4; do
  tag="t${t/\//o}"
  .venv/bin/python -u scripts/_ts2_build.py --t $t > data/sealed/TS2_for_quantum/ts2_build_${tag}.out 2>&1
  tail -1 data/sealed/TS2_for_quantum/ts2_build_${tag}.out | sed "s|^|[$tag TS] |" >> data/jet/psweep_build.out
done
.venv/bin/python -u scripts/_ts2_kerr_control.py 2/3 3/5 3/7 2/5 1/4 1/5 1/7 3/4 >> data/jet/psweep_build.out 2>&1
echo "ALL DONE $(date)" >> data/jet/psweep_build.out
