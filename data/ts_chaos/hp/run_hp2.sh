#!/bin/zsh
# HP probe part 2: crossover integrations + analysis, then G4 (mpmath). Load-gated, 2 workers, checkpointed.
cd "${0:A:h}/../../.." || exit 2
exec < /dev/null
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 VECLIB_MAXIMUM_THREADS=1 NUMBA_NUM_THREADS=1
while true; do
  l5=$(sysctl -n vm.loadavg | awk '{print $3}')
  memgb=$(vm_stat | awk '/page size of/ {ps=$8} /Pages free/ {f=$3} /Pages inactive/ {i=$3} END {gsub(/\./,"",f); gsub(/\./,"",i); printf "%.1f", (f+i)*ps/1073741824}')
  if (( l5 < 8.0 && memgb >= 3.0 )); then break; fi
  sleep 120
done
echo "[gate] part 2 start $(date) load5 $l5" >> data/ts_chaos/hp/hp.out
P=.venv/bin/python
$P -u scripts/_hp_cross.py run 2 >> data/ts_chaos/hp/hp.out 2>&1 && $P -u scripts/_hp_cross.py analyse >> data/ts_chaos/hp/hp.out 2>&1
$P -u scripts/_hp_g4.py >> data/ts_chaos/hp/hp.out 2>&1
echo "ALL DONE (cross, G4) $(date)" >> data/ts_chaos/hp/hp.out
