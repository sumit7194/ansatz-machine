#!/bin/zsh
# Saddle test (SADDLE_PREREGISTRATION.md): Kerr negative control, then TS. 2 workers, nice 10, checkpointed;
# _ts_saddle.py stops itself on the disk/memory/swap guard; rerunning resumes from the jsonl checkpoints.
cd "${0:A:h}/../../.." || exit 2
exec < /dev/null
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMBA_NUM_THREADS=1
nice -n 10 .venv/bin/python -u scripts/_ts_saddle.py run kerr 2 >> data/ts_chaos/saddle/saddle.out 2>&1
nice -n 10 .venv/bin/python -u scripts/_ts_saddle.py run ts 2 >> data/ts_chaos/saddle/saddle.out 2>&1
echo "ALL DONE (kerr, ts) $(date)" >> data/ts_chaos/saddle/saddle.out
