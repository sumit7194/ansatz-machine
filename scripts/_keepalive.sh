#!/bin/bash
# Keeps this session alive overnight so sister sessions can reach it, and leaves a durable
# machine-state trace. This box loses power in the daytime and has lost multi-hour runs; an
# hourly line means a morning reader can tell "cut at 03:40" from "still thinking".
LOG="$(cd "$(dirname "$0")/.." && pwd)/data/overnight_state.log"
# The LONG-LIVED loop records its own pid so the status writer can publish a token that outlives a
# single tick. Previously the writer published $PPID, which is the loop when the loop calls it and
# a TRANSIENT SHELL when anyone runs it by hand -- so every manual test poisoned the field with a
# pid that was dead milliseconds later, and a reader could not tell which kind of write it held.
WRITERPID=/Users/sumit/Github/.claude-coordination/.ansatz.writer.pid
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
  # REWRITTEN EVERY TICK, not once at start. Written once, the pidfile is a capture rather than a
  # measurement -- the same error as the token it feeds, one level down: anything that clobbers it
  # leaves the loop permanently unable to identify itself, with no way to recover. Verified by
  # clobbering it with an impostor pid and confirming the next tick restores the true token.
  echo $$ > "$WRITERPID"
  "$(dirname "$0")/_coord_status.sh"
  sleep 60
done
