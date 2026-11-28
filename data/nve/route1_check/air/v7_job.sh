#!/bin/zsh
# Mac mini variant of air/job.sh for the v7 stages (registration V7_REGISTRATION.md): the same PAUSE-ONLY
# guard (memory pressure level >= 4 or free disk < 5 GB -> SIGSTOP the whole tree; recovered -> SIGCONT; nothing is
# ever killed), at nice 10, run from the check worktree root, logs in data/nve/route1_check/v7/.
#   usage: stopc_job.sh NAME command...
cd /Users/sumit/Github/conjecture_machine-b2fix || exit 1
L=data/nve/route1_check/v7; mkdir -p $L
name=$1; shift
log=$L/$name.log
glog=$L/guard_$name.log
tree() {
  local p=$1 c
  echo $p
  for c in $(pgrep -P $p); do tree $c; done
}
nice -n 10 "$@" >> $log 2>&1 &
pid=$!
echo $pid > $L/$name.pid
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
