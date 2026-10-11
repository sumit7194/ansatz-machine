#!/bin/zsh
# High-precision probe: select -> gates -> base, load-gated, 2 workers, checkpointed (restart = resume).
cd "${0:A:h}/../../.." || exit 2
exec < /dev/null
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMBA_NUM_THREADS=1
while true; do
  l5=$(sysctl -n vm.loadavg | awk '{print $3}')
  memgb=$(vm_stat | awk '/page size of/ {ps=$8} /Pages free/ {f=$3} /Pages inactive/ {i=$3} END {gsub(/\./,"",f); gsub(/\./,"",i); printf "%.1f", (f+i)*ps/1073741824}')
  if (( l5 < 8.0 && memgb >= 3.0 )); then break; fi
  sleep 120
done
echo "[gate] start $(date) load5 $l5 mem ${memgb}GB" >> data/ts_chaos/hp/hp.out
P=.venv/bin/python
$P -u scripts/_hp_probe.py select 2 >> data/ts_chaos/hp/hp.out 2>&1 || { echo "select FAILED" >> data/ts_chaos/hp/hp.out; exit 1; }
$P -u scripts/_hp_probe.py gates 2 >> data/ts_chaos/hp/hp.out 2>&1 || { echo "gates FAILED" >> data/ts_chaos/hp/hp.out; exit 1; }
grep -q "VERDICT-gates G1-G3: ALL PASS" data/ts_chaos/hp/hp.out || { echo "STOP: a gate failed; base not run (prereg)" >> data/ts_chaos/hp/hp.out; exit 1; }
$P -u scripts/_hp_probe.py base 2 >> data/ts_chaos/hp/hp.out 2>&1
echo "ALL DONE (select, gates, base) $(date)" >> data/ts_chaos/hp/hp.out
