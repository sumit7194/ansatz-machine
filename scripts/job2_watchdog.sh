#!/usr/bin/env bash
# Watchdog for one rank-8 job: every minute, log the WHOLE process tree's footprint (top MEM + CMPRS, rule 116 --
# never the parent's RSS) and free disk; if free disk < DISK_MIN_GB, SIGKILL the tree (children first) and report.
# Usage: job2_watchdog.sh <root_pid> [label]      env: DISK_MIN_GB (default 5), INTERVAL (default 60)
set -u
root="$1"; label="${2:-job}"; min="${DISK_MIN_GB:-5}"; iv="${INTERVAL:-60}"
inbox=/Users/sumit/Github/.claude-coordination/inbox/bridge
tree() { local p=$1; echo "$p"; for k in $(pgrep -P "$p"); do tree "$k"; done; }
tomb() { case "$1" in *G) echo "${1%G}*1024" | bc;; *M) echo "${1%M}";; *K) echo "${1%K}/1024" | bc -l;; *B) echo 0;; *) echo 0;; esac; }
echo "[$(date '+%a %H:%M:%S')] watchdog up: root $root ($label), kill if free disk < ${min} GB, every ${iv}s"
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
  peak=$(echo "if ($tot > $peak) $tot else $peak" | bc -l)
  printf "[%s] tree %.2f GB (peak %.2f)  free disk %s GB  swap used %s |%s\n" "$(date '+%H:%M:%S')" \
    "$(echo "$tot/1024" | bc -l)" "$(echo "$peak/1024" | bc -l)" "$free" "$sw" "$line"
  if [ "$free" -lt "$min" ]; then
    echo "[$(date '+%a %H:%M:%S')] WATCHDOG FIRED: free disk ${free} GB < ${min} GB -- killing tree of $root"
    for p in $(tree "$root" | tail -r); do kill -KILL "$p" 2>/dev/null; done
    mkdir -p "$inbox"; printf "WATCHDOG FIRED (%s): free disk %s GB < %s GB; killed the tree of %s at %s. Peak tree footprint %.2f GB.\n" \
      "$label" "$free" "$min" "$root" "$(date)" "$(echo "$peak/1024" | bc -l)" > "$inbox/$(date +%F)_ansatz_watchdog_$label.md"
    exit 3
  fi
  sleep "$iv"
done
printf "[%s] root %s exited; watchdog done. peak tree footprint %.2f GB\n" "$(date '+%a %H:%M:%S')" "$root" "$(echo "$peak/1024" | bc -l)"
