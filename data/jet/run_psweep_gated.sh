#!/bin/zsh
# Start the p-sweep jets only when the box has a free core: 5-minute load average below 8 (10 cores; Bridge-agreed).
cd "${0:A:h}/../.." || exit 2
exec < /dev/null
while true; do
  l5=$(sysctl -n vm.loadavg | awk '{print $3}')
  if (( l5 < 8.0 )); then break; fi
  sleep 120
done
echo "[gate] starting at $(date), load5 $l5" >> data/jet/psweep.out
exec data/jet/run_psweep.sh
