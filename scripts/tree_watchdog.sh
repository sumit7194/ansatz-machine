#!/usr/bin/env bash
# Whole-tree watchdog (successor of job2_watchdog.sh, which is left untouched because instances of it may be running --
# bash reads scripts from disk, memory rule 118). Every INTERVAL s: log the WHOLE process tree's footprint (top MEM,
# rule 116 -- never the parent's RSS), free disk, swap and memory_pressure. KILL the tree (children first) and report if
#   free disk < DISK_MIN_GB (default 5)   or   tree footprint > FOOT_MAX_GB (default 0 = off; the Bridge's cap is 30).
# Swap and memory pressure are LOGGED, never triggers (quantum's false-positive kills, 955b4c0).
# Usage: tree_watchdog.sh <root_pid> [label]
set -u
root="$1"; label="${2:-job}"; min="${DISK_MIN_GB:-5}"; iv="${INTERVAL:-60}"; fmax="${FOOT_MAX_GB:-0}"
inbox=/Users/sumit/Github/.claude-coordination/inbox/bridge
tree() { local p=$1; echo "$p"; for k in $(pgrep -P "$p"); do tree "$k"; done; }
tomb() { case "$1" in *G) echo "${1%G}*1024" | bc;; *M) echo "${1%M}";; *K) echo "${1%K}/1024" | bc -l;; *B) echo 0;; *) echo 0;; esac; }
echo "[$(date '+%a %H:%M:%S')] watchdog up: root $root ($label), kill if free disk < ${min} GB or tree > ${fmax} GB (0=off), every ${iv}s"
peak=0
while kill -0 "$root" 2>/dev/null; do
  tot=0; line=""
  for p in $(tree "$root"); do
    read -r mem cm < <(top -l 1 -pid "$p" -stats mem,cmprs 2>/dev/null | tail -1)
    [ -z "${mem:-}" ] && continue
    mb=$(tomb "$mem"); tot=$(echo "$tot + $mb" | bc -l); line="$line $p:$mem/$cm"
  done
  free=$(df -g /System/Volumes/Data | awk 'NR==2{print $4}')
  sw=$(sysctl -n vm.swapusage | awk '{print $3}')
  # LOGGED, never a trigger. quantum's watchdog killed three healthy runs on "free swap < 512 MB" while 77-87% of
  # memory was free: macOS grows swap on demand (2026-10, quantum 955b4c0). Ours never triggered on swap; it also
  # does not kill on memory pressure, because our rank-8 runs lean on compression by design (28 GB tree on 16 GB,
  # finished cleanly). The only kill trigger here is the disk floor.
  mp=$(memory_pressure -Q 2>/dev/null | awk -F': ' '/free percentage/{print $2}')
  peak=$(echo "if ($tot > $peak) $tot else $peak" | bc -l)
  printf "[%s] tree %.2f GB (peak %.2f)  free disk %s GB  swap used %s  mem free %s |%s\n" "$(date '+%H:%M:%S')" \
    "$(echo "$tot/1024" | bc -l)" "$(echo "$peak/1024" | bc -l)" "$free" "$sw" "${mp:-?}" "$line"
  over=0; [ "$fmax" != "0" ] && over=$(echo "$tot/1024 > $fmax" | bc -l)
  if [ "$free" -lt "$min" ] || [ "$over" = "1" ]; then
    why="free disk ${free} GB < ${min} GB"; [ "$over" = "1" ] && why="tree footprint $(printf %.2f "$(echo "$tot/1024" | bc -l)") GB > ${fmax} GB"
    echo "[$(date '+%a %H:%M:%S')] WATCHDOG FIRED: $why -- killing tree of $root"
    for p in $(tree "$root" | tail -r); do kill -KILL "$p" 2>/dev/null; done
    mkdir -p "$inbox"; printf "WATCHDOG FIRED (%s): %s; killed the tree of %s at %s. Peak tree footprint %.2f GB.\n" \
      "$label" "$why" "$root" "$(date)" "$(echo "$peak/1024" | bc -l)" > "$inbox/$(date +%F)_ansatz_watchdog_$label.md"
    exit 3
  fi
  sleep "$iv"
done
printf "[%s] root %s exited; watchdog done. peak tree footprint %.2f GB\n" "$(date '+%a %H:%M:%S')" "$root" "$(echo "$peak/1024" | bc -l)"
