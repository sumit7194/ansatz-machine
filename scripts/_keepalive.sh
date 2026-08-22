#!/bin/bash
# Keeps this session alive overnight so sister sessions can reach it, and leaves a durable
# machine-state trace. This box loses power in the daytime and has lost multi-hour runs; an
# hourly line means a morning reader can tell "cut at 03:40" from "still thinking".
LOG="$(cd "$(dirname "$0")/.." && pwd)/data/overnight_state.log"
for i in $(seq 1 600); do
  # "Pages free" ALONE understated headroom ~12x for two days in this very log -- macOS parks
  # reclaimable memory in `inactive`, and a morning reader reconstructing a power cut was being
  # shown 0.4 GB on a machine with 7 GB available. Our own rule, broken in our own durable trace,
  # because the rule got encoded in machine_state.sh and this line was never revisited. Page size
  # is read, not typed: 16384 here, and a hardcoded 4096 would understate by a further 4x.
  PGSZ=$(sysctl -n hw.pagesize)
  FREE=$(vm_stat | awk -v z="$PGSZ" '/Pages free/{f=$3} /Pages inactive/{i=$3} /Pages speculative/{s=$3} END{gsub(/\./,"",f); gsub(/\./,"",i); gsub(/\./,"",s); printf "%.1f", (f+i+s)*z/1073741824}')
  LOAD=$(uptime | sed 's/.*averages*: //' | awk '{print $1}')
  JOBS=$(pgrep -f "scripts/_kt_" 2>/dev/null | wc -l | tr -d " ")   # -c does not exist on macOS pgrep
  echo "$(date '+%m-%d %H:%M:%S')  avail=${FREE}GB load=${LOAD} kt_jobs=${JOBS}" >> "$LOG"
  # refresh the coordination status so a stale file never misleads a sister session about
  # whether this box is busy -- a status file that outlives its process is worse than none
  "$(dirname "$0")/_coord_status.sh"
  sleep 60
done
