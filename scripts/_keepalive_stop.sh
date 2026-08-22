#!/bin/bash
# Stop OUR keepalive, and only ours.
#
# WHY THIS EXISTS. On 2026-08-22 this session ran `pkill -f _keepalive.sh` twice while restarting
# its own heartbeat. The bridge's loop is named `bridge_keepalive.sh`, which CONTAINS the substring
# `_keepalive.sh`, so both of our cleanups killed their heartbeat as collateral. They spent the day
# diagnosing four "mystery deaths" -- catchable signal, rc=0, no schedule, immune to nohup/disown/
# setsid -- because none of those defend against being killed by name, and nothing on their side
# could ever have pointed here. quantum identified it by noticing their own loop survives only
# because its name lacks the string.
#
#   A PROCESS-NAME PATTERN IS NOT A PRIVATE NAMESPACE ON A SHARED MACHINE.
#   `pkill -f <word>` IS A BROADCAST.
#
# This also violated a standing instruction for this repo: only ever signal processes we launched
# ourselves, verified by our own ledger -- never by name matching. See memory `vm-pkill-self-match`,
# where the same class of error killed a sister session's gate a week ago. Twice now.
#
# Kill BY PID from our own pidfile, and verify identity before signalling, because a recycled pid
# is dangerous in exactly the same way when killing as when trusting.
PIDFILE=/Users/sumit/Github/.claude-coordination/.ansatz.writer.pid
[ -r "$PIDFILE" ] || { echo "no pidfile; nothing of ours to stop"; exit 0; }
PID=$(cat "$PIDFILE" 2>/dev/null)
case "$PID" in ''|*[!0-9]*) echo "pidfile does not contain a pid"; exit 0;; esac
ps -p "$PID" >/dev/null 2>&1 || { echo "pid $PID not running"; exit 0; }
CMD=$(ps -o args= -p "$PID" 2>/dev/null)
case "$CMD" in
  *conjecture_machine/scripts/_keepalive.sh*|*scripts/_keepalive.sh*)
    kill "$PID" && echo "stopped OUR keepalive, pid $PID" ;;
  *)
    echo "REFUSING: pid $PID is not our keepalive -- it is: $CMD" ; exit 1 ;;
esac
