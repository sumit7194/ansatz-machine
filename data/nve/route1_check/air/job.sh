#!/bin/zsh
# Air job runner with a PAUSE-ONLY guard (fleet rule: no caps; pressure pauses, never kills).
#   usage: job.sh NAME command...      (run from ~/GitHub/ansatz-air; detached with nohup)
# The guard acts only on the process tree this script launched (the PID and its descendants, found with pgrep -P).
# Every 30 s: memory pressure level >= 4 (critical) or free disk < 5 GB -> SIGSTOP to the whole tree; recovered ->
# SIGCONT. Transitions are logged. Nothing is ever killed.
# (v2 of this file: v1 stopped only the top PID, i.e. the shell script, not its python child.)
cd ~/GitHub/ansatz-air || exit 1
name=$1; shift
log=logs/$name.log
glog=logs/guard_$name.log

tree() {
  local p=$1 c
  echo $p
  for c in $(pgrep -P $p); do tree $c; done
}

nice -n 15 "$@" >> $log 2>&1 &
pid=$!
echo $pid > logs/$name.pid
echo "$(date '+%F %T') started $name pid $pid: $*" >> $glog
stopped=0
while kill -0 $pid 2>/dev/null; do
  lvl=$(sysctl -n kern.memorystatus_vm_pressure_level)
  freegb=$(df -g ~ | awk 'NR==2{print $4}')
  if [[ lvl -ge 4 || freegb -lt 5 ]]; then
    if [[ stopped -eq 0 ]]; then
      pids=($(tree $pid))
      kill -STOP $pids; stopped=1
      echo "$(date '+%F %T') PAUSED pids $pids (pressure level $lvl, free $freegb GB)" >> $glog
    fi
  elif [[ stopped -eq 1 ]]; then
    kill -CONT $pids; stopped=0
    echo "$(date '+%F %T') RESUMED pids $pids (pressure level $lvl, free $freegb GB)" >> $glog
  fi
  sleep 30
done
wait $pid; rc=$?
echo "$(date '+%F %T') $name pid $pid exited rc $rc" >> $glog
echo "JOB_EXIT $rc" >> $log
