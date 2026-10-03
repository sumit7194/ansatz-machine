#!/bin/zsh
# Sector path vs full path, both primes: TS r2, r3, r4 and Kerr r4 (Bridge gate 2). Two streams in parallel, 2 threads each.
cd "$(dirname "$0")/../../.." || exit 2
exec < /dev/null
V=data/ts2_exact/val
sectors() { for c in "ts2:4/5 2 1 ts_r2" "ts2:4/5 3 1 ts_r3" "ts2kerr:4/5 4 2 kerr_r4" "ts2:4/5 4 2 ts_r4"; do
  set -- ${=c}; for p in 0 1; do
    o=$V/sec_$4_p$p.out; grep -q VERDICT $o 2>/dev/null && continue
    KT_SOLVER=rust KT_THREADS=2 /usr/bin/time -l .venv/bin/python -u scripts/_kt_exact_sector.py --metric $1 --rank $2 --denpow $3 --prime $p --outdir $V > $o 2> $o.time
  done; done; echo "sectors done $(date)" >> $V/DONE; }
fulls() { for c in "ts2:4/5 2 1 ts_r2" "ts2:4/5 3 1 ts_r3" "ts2kerr:4/5 4 2 kerr_r4" "ts2:4/5 4 2 ts_r4"; do
  set -- ${=c}; for p in 0 1; do
    o=$V/full_$4_p$p.out; grep -q VERDICT $o 2>/dev/null && continue
    KT_SOLVER=rust KT_THREADS=2 /usr/bin/time -l .venv/bin/python -u scripts/_kt_exact_op.py --metric $1 --rank $2 --denpow $3 --prime $p > $o 2> $o.time
  done; done; echo "fulls done $(date)" >> $V/DONE; }
sectors & fulls & wait
echo "ALL DONE $(date)" >> $V/DONE
