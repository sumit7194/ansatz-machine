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
if [ "$N" -gt 0 ]; then STATE=running; DETAIL="symbolic Killing-tensor search (${N} proc), single-threaded"
else STATE=idle; DETAIL=""; fi
HEAVY=false; [ "$RSS" -gt 2048 ] && HEAVY=true      # derived from measured RSS, never hand-set
printf '{"session":"ansatz","repo":"/Users/sumit/Github/conjecture_machine","state":"%s","heavy":%s,"pid":%s,"rss_total_mb":%s,"disk_free_gb":%s,"stale_after_s":600,"detail":"%s","updated":"%s"}\n' \
  "$STATE" "$HEAVY" "$$" "$RSS" "${DISK:-0}" "$DETAIL" "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  > "$COORD/ansatz.status.tmp"
mv "$COORD/ansatz.status.tmp" "$COORD/ansatz.status"
