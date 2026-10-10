#!/bin/zsh
# Start the p-sweep jets only when the box has room: 5-min load < 8 AND free+inactive memory >= 3 GB (Bridge, 2026-10-11).
cd "${0:A:h}/../.." || exit 2
exec < /dev/null
while true; do
  l5=$(sysctl -n vm.loadavg | awk '{print $3}')
  memgb=$(vm_stat | awk '/page size of/ {ps=$8} /Pages free/ {f=$3} /Pages inactive/ {i=$3} END {gsub(/\./,"",f); gsub(/\./,"",i); printf "%.1f", (f+i)*ps/1073741824}')
  if (( l5 < 8.0 && memgb >= 3.0 )); then break; fi
  sleep 120
done
echo "[gate] starting at $(date), load5 $l5, free+inactive ${memgb} GB" >> data/jet/psweep.out
exec data/jet/run_psweep.sh
