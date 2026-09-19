#!/bin/bash
# Pause or resume one of THIS repo's Killing-tensor runs, together with its Rust solver child.
#
#   scripts/kt_pause.sh <pid> stop     # freeze: no CPU; memory stays (and can be swapped out)
#   scripts/kt_pause.sh <pid> cont     # carry on exactly where it was
#
# Refuses anything that is not a scripts/_kt_double.py process whose working directory is this
# repo -- other projects' Python processes run on this machine too, and must never be signalled.
set -u
pid="${1:?usage: kt_pause.sh <pid> stop|cont}"
act="${2:?usage: kt_pause.sh <pid> stop|cont}"
repo="$(cd "$(dirname "$0")/.." && pwd)"
cmd="$(ps -o command= -p "$pid" 2>/dev/null)" || { echo "no process $pid"; exit 1; }
cwd="$(lsof -a -p "$pid" -d cwd -Fn 2>/dev/null | sed -n 's/^n//p' | tail -1)"
case "$cmd" in *scripts/_kt_double.py*) ;; *) echo "refusing: $pid is not a _kt_double.py run"; exit 1;; esac
[ "$cwd" = "$repo" ] || { echo "refusing: $pid runs in '$cwd', not this repo"; exit 1; }
kids="$(pgrep -P "$pid" | tr '\n' ' ')"
case "$act" in
  stop) kill -STOP "$pid"; for k in $kids; do kill -STOP "$k"; done
        echo "paused $pid${kids:+ and children $kids}";;
  cont) for k in $kids; do kill -CONT "$k"; done; kill -CONT "$pid"
        echo "resumed $pid${kids:+ and children $kids}";;
  *) echo "action must be stop or cont"; exit 1;;
esac
ps -o pid=,state=,etime=,command= -p "$pid" $kids 2>/dev/null | cut -c1-110
