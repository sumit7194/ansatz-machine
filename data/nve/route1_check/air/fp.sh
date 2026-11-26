#!/bin/zsh
# Footprint log for the record (the Bridge, 2026-11-27): every 600 s, `footprint -p` of each process in the tree of
# PID (this runner's OWN processes only; nothing else is inspected), one line each; at the end, the peak per process.
#   usage: fp.sh NAME PID     (started in the background by a runner, with PID = the runner's own $$)
cd ~/GitHub/ansatz-air || exit 1
name=$1; top=$2; log=logs/fp_$name.log
tree() { local p=$1 c; echo $p; for c in $(pgrep -P $p); do tree $c; done; }
typeset -A peak cmd
while kill -0 $top 2>/dev/null; do
  for p in $(tree $top); do
    fpl="$(footprint -p $p 2>/dev/null | grep -m1 'Footprint:')"
    [[ -z "$fpl" ]] && continue
    print -r -- "$(date '+%F %T') $fpl" >> $log
    num="$(print -r -- "$fpl" | sed -E 's/.*Footprint: ([0-9.]+) (KB|MB|GB).*/\1/')"
    unit="$(print -r -- "$fpl" | sed -E 's/.*Footprint: ([0-9.]+) (KB|MB|GB).*/\2/')"
    (( mbv = num ))
    [[ "$unit" == KB ]] && (( mbv = num / 1024.0 ))
    [[ "$unit" == GB ]] && (( mbv = num * 1024.0 ))
    if [[ -z "${peak[$p]}" ]] || (( mbv > peak[$p] )); then
      peak[$p]=$mbv
      cmd[$p]="${fpl%%:*}"
    fi
  done
  sleep 600
done
for p in ${(k)peak}; do print -r -- "$(date '+%F %T') PEAK ${cmd[$p]} ${peak[$p]} MB" >> $log; done
