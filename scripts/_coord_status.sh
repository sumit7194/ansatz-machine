#!/bin/bash
# Advertise this session's state to the sister-session coordination directory.
#
# THE BUG THIS REPLACES, worth recording because it is catalogue rule 7 in my own tooling:
# the previous version probed with `pgrep -fc "_kt_"`. macOS pgrep has NO -c flag, so that is a
# USAGE ERROR (exit 2), and the `|| echo 0` fallback turned it into "zero jobs running". The status
# file therefore advertised `idle` for the entire duration of a live run, and a sister session
# caught it before I did. "Command failed" and "found nothing" produced the same output -- the
# exact failure mode I had sent to two other sessions hours earlier.
# Fix: count with `pgrep -f ... | wc -l`, which cannot confuse an error for an empty result, and
# publish pid + stale_after_s so READERS can expire this file (blackhole's rule: a status older
# than its window, or whose pid is gone, is UNKNOWN and must fail OPEN -- never treated as busy).
COORD=/Users/sumit/Github/.claude-coordination
[ -d "$COORD" ] || exit 0
# THE PROBE MATCHED THE OBSERVER until 2026-08-22. `pgrep -f` matches any command line
# CONTAINING the pattern, so a shell, editor, grep or tool call that merely MENTIONS
# scripts/_kt_... registered as a Killing-tensor job. Reproduced: with one prover running, a
# `bash -c 'while :; do sleep 1; done  # scripts/_kt_zv_den2.py' ` made this file advertise
# "2 proc". That is a PHANTOM JOB ON AN IDLE BOX, which under our coordination protocol is this
# session telling a sister not to launch -- the false-STOP direction, which costs someone else
# their run and produces no symptom here. (bridge hit the identical bug; quantum's finding that
# pgrep skips the CALLER'S ANCESTORS is why it never showed up when tested from a shell -- the
# writer runs from the keepalive, a different process tree, where nothing is exempt.)
# Fix: keep a pid only if the kernel says the executable really is python.
PIDS=""
for p in $(pgrep -f "scripts/_kt_" 2>/dev/null); do
  case "$(ps -o comm= -p "$p" 2>/dev/null)" in *[Pp]ython*) PIDS="$PIDS $p";; esac
done
N=$(echo $PIDS | wc -w | tr -d ' ')
RSS=0
for p in $PIDS; do
  r=$(ps -o rss= -p "$p" 2>/dev/null | tr -d ' '); RSS=$((RSS + ${r:-0}))
done
RSS=$((RSS / 1024))
DISK=$(df -g / | tail -1 | awk '{print $4}')
# WE PUBLISHED NO MEMORY VIEW AT ALL until 2026-08-22 -- only rss_total_mb and disk. A sister
# sizing a launch against this file got our footprint and no read on the machine. quantum
# published the opposite error (free+speculative only, understating headroom 12x, a false STOP).
# Both fields are published here, labelled, with the rule in the file so no reader has to guess
# which one they are holding. Page size READ, never typed.
PGSZ=$(sysctl -n hw.pagesize)
eval "$(vm_stat | awk -v z="$PGSZ" '
  /Pages free/{f=$3} /Pages inactive/{i=$3} /Pages speculative/{s=$3} /Pages purgeable/{p=$3}
  END{gsub(/\./,"",f);gsub(/\./,"",i);gsub(/\./,"",s);gsub(/\./,"",p);
      printf "MEMFREE=%.2f; MEMAVAIL=%.2f\n", (f+s)*z/1073741824, (f+i+s+p)*z/1073741824}')"
PO1=$(vm_stat | awk '/Pageouts/{gsub(/\./,"",$NF); print $NF}')
if [ "$N" -gt 0 ]; then STATE=running; DETAIL="symbolic Killing-tensor search (${N} proc), single-threaded"
else STATE=idle; DETAIL=""; fi
HEAVY=false; [ "$RSS" -gt 2048 ] && HEAVY=true      # derived from measured RSS, never hand-set
# THE `pid` FIELD WAS DEAD BY CONSTRUCTION UNTIL 2026-08-22. It published `$$` -- the PID of THIS
# script, which exits milliseconds later. The field exists so a reader can apply blackhole's rule
# ("a status whose pid is gone is UNKNOWN, fail open"), and it therefore made every read of this
# file resolve to UNKNOWN, forever. A liveness field that is guaranteed dead is worse than absent:
# absent is visible, always-dead looks like a working mechanism failing safe. Found by checking
# `ps` against the field rather than reading the code, after quantum reported the mirror bug
# (a status that never existed at all, so nothing could go stale).
# Now published: writer_pid = the long-lived process that invoked this (the keepalive), and
# job_pids = the actual measured jobs. Both checkable by a reader; neither is this script.
# TOKEN RE-DERIVED AND VERIFIED EVERY TICK, never captured once. `updated` is a claim about every
# other field and the token is one of them -- a token captured at startup is not a measurement, it
# is a constant that happened to be true when written. Verified ALIVE *and* still the keepalive,
# because a bare liveness check certifies any unrelated process that inherited a recycled pid.
# `null` is the honest answer when no loop is running: it means "no automatic heartbeat, trust
# `updated` and nothing else" rather than advertising a token that cannot be confirmed.
WRITER=null
PIDFILE=/Users/sumit/Github/.claude-coordination/.ansatz.writer.pid
if [ -r "$PIDFILE" ]; then
  w=$(cat "$PIDFILE" 2>/dev/null)
  case "$w" in ''|*[!0-9]*) w="";; esac
  if [ -n "$w" ] && ps -p "$w" >/dev/null 2>&1; then
    case "$(ps -o args= -p "$w" 2>/dev/null)" in *_keepalive.sh*) WRITER=$w;; esac
  fi
fi
JOBS_CSV=$(echo $PIDS | tr ' ' ',')   # emitted inside [] as a JSON list, not a string
printf '{"session":"ansatz","repo":"/Users/sumit/Github/conjecture_machine","state":"%s","heavy":%s,"writer_pid":%s,"writer_cmd_match":"_keepalive.sh","job_pids":[%s],"rss_total_mb":%s,"disk_free_gb":%s,"rss_referent":"RESIDENT set summed over live job pids, sampled now. NOT a peak and NOT a projection. A rank step allocates a second full matrix per prime, so this number can DOUBLE after a result line appears.","mem_free_gb":%s,"mem_available_gb":%s,"mem_rule":"free+speculative vs +inactive+purgeable; SCHEDULE ON mem_available_gb; page size read from hw.pagesize","stale_after_s":600,"detail":"%s","updated":"%s"}\n' \
  "$STATE" "$HEAVY" "$WRITER" "$JOBS_CSV" "$RSS" "${DISK:-0}" "${MEMFREE:-0}" "${MEMAVAIL:-0}" "$DETAIL" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  > "$COORD/ansatz.status.tmp"
mv "$COORD/ansatz.status.tmp" "$COORD/ansatz.status"
