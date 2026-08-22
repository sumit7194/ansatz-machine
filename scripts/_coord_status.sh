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
N=$(pgrep -f "scripts/_kt_" 2>/dev/null | wc -l | tr -d ' ')
RSS=0
for p in $(pgrep -f "scripts/_kt_" 2>/dev/null); do
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
WRITER=$PPID
JOBS_CSV=$(pgrep -f "scripts/_kt_" 2>/dev/null | paste -sd, - )
printf '{"session":"ansatz","repo":"/Users/sumit/Github/conjecture_machine","state":"%s","heavy":%s,"writer_pid":%s,"job_pids":"%s","rss_total_mb":%s,"disk_free_gb":%s,"mem_free_gb":%s,"mem_available_gb":%s,"mem_rule":"free+speculative vs +inactive+purgeable; SCHEDULE ON mem_available_gb; page size read from hw.pagesize","stale_after_s":600,"detail":"%s","updated":"%s"}\n' \
  "$STATE" "$HEAVY" "$WRITER" "$JOBS_CSV" "$RSS" "${DISK:-0}" "${MEMFREE:-0}" "${MEMAVAIL:-0}" "$DETAIL" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  > "$COORD/ansatz.status.tmp"
mv "$COORD/ansatz.status.tmp" "$COORD/ansatz.status"
