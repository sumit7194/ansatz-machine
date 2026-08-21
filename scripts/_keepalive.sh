#!/bin/bash
# Keeps this session alive overnight so sister sessions can reach it, and leaves a durable
# machine-state trace. This box loses power in the daytime and has lost multi-hour runs; an
# hourly line means a morning reader can tell "cut at 03:40" from "still thinking".
LOG="$(cd "$(dirname "$0")/.." && pwd)/data/overnight_state.log"
for i in $(seq 1 600); do
  FREE=$(vm_stat | awk '/Pages free/{printf "%.1f", $3*16384/1073741824}')
  LOAD=$(uptime | sed 's/.*averages*: //' | awk '{print $1}')
  JOBS=$(pgrep -f "scripts/_kt_" 2>/dev/null | wc -l | tr -d " ")   # -c does not exist on macOS pgrep
  echo "$(date '+%m-%d %H:%M:%S')  free=${FREE}GB load=${LOAD} kt_jobs=${JOBS}" >> "$LOG"
  # refresh the coordination status so a stale file never misleads a sister session about
  # whether this box is busy -- a status file that outlives its process is worse than none
  "$(dirname "$0")/_coord_status.sh"
  sleep 60
done
