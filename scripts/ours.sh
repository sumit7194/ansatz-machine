#!/bin/bash
# ours.sh — the process ledger: which PIDs are OURS, with evidence.
#
# WHY THIS EXISTS. Several projects run long Python jobs on this machine at once
# (conjecture_machine, BlackHole/primordial_blackhole_search, the bridge). We must only ever
# signal processes we launched ourselves. Name-matching is NOT safe: `pkill -f <pattern>` has
# previously killed a sibling project's gate, and on another occasion the killer's own shell,
# because the pattern matched more than intended. So attribution here is by ANCESTRY and CWD —
# facts about the process — never by strings in its command line.
#
# The ledger (data/our_pids.txt) records the LAUNCHERS we start. Every descendant of a tracked
# launcher is ours by descent; that is how a per-battery child PID (which no file could
# enumerate in advance, since the gate spawns them one at a time) becomes attributable.
#
# USAGE
#   ours.sh track <pid> <label>   record a launcher we just started
#   ours.sh tree                  every tracked launcher + its live descendants
#   ours.sh whose <pid>           OURS / NOT OURS / UNKNOWN, with the evidence
#   ours.sh all                   every python process on the box, attributed
#   ours.sh prune                 drop dead launchers from the ledger
#
# This script NEVER sends a signal. Killing stays a deliberate, separate act.

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LEDGER="$ROOT/data/our_pids.txt"
mkdir -p "$ROOT/data"; touch "$LEDGER"

# Boot generation: PIDs are only meaningful within one boot. After a reboot PID 1186 may
# belong to a stranger -- observed for real: a post-reboot boot-storm process briefly occupied
# a tracked PID and the ledger reported it [LIVE]. Entries are stamped with the boot time and
# any entry from an earlier boot is STALE, never "ours".
_boot()    { sysctl -n kern.boottime 2>/dev/null | sed 's/.*sec = \([0-9]*\).*/\1/'; }
_cwd_of()  { lsof -a -p "$1" -d cwd -Fn 2>/dev/null | grep '^n' | head -1 | cut -c2-; }
_cmd_of()  { ps -o command= -p "$1" 2>/dev/null | head -1; }
_ppid_of() { ps -o ppid= -p "$1" 2>/dev/null | tr -d ' '; }
_etime_of(){ ps -o etime= -p "$1" 2>/dev/null | tr -d ' '; }
_alive()   { ps -p "$1" >/dev/null 2>&1; }

# Only entries from the CURRENT boot may be treated as ours.
_tracked() {
  local b; b="$(_boot)"
  awk -v boot="$b" 'NF{
        e=""; for(i=1;i<=NF;i++) if ($i ~ /^boot=/) { e=substr($i,6) }
        if (e=="" || e==boot) print $1
      }' "$LEDGER" 2>/dev/null
}

# entries written before the current boot (their PIDs may now belong to anyone)
_is_stale() {
  local b; b="$(_boot)"
  awk -v pid="$1" -v boot="$b" 'NF && $1==pid {
        e=""; for(i=1;i<=NF;i++) if ($i ~ /^boot=/) { e=substr($i,6) }
        if (e!="" && e!=boot) { print "stale"; exit }
      }' "$LEDGER" 2>/dev/null
}

# Walk ancestry toward PID 1; echo the first tracked ancestor found (including self).
_tracked_ancestor() {
  local p="$1" hops=0 t
  while [ -n "$p" ] && [ "$p" != "0" ] && [ "$p" != "1" ] && [ "$hops" -lt 40 ]; do
    for t in $(_tracked); do
      if [ "$p" = "$t" ]; then echo "$t"; return 0; fi
    done
    p="$(_ppid_of "$p")"
    hops=$((hops + 1))
  done
  return 1
}

_ancestry_chain() {
  local p="$1" chain="$1" hops=0
  while [ "$hops" -lt 20 ]; do
    p="$(_ppid_of "$p")"
    if [ -z "$p" ] || [ "$p" = "0" ]; then break; fi
    chain="$chain <- $p"
    if [ "$p" = "1" ]; then break; fi
    hops=$((hops + 1))
  done
  echo "$chain"
}

# Every live descendant of a pid (breadth-first).
_descendants() {
  local frontier="$1" next p kid
  while [ -n "$frontier" ]; do
    next=""
    for p in $frontier; do
      for kid in $(pgrep -P "$p" 2>/dev/null); do
        echo "$kid"
        next="$next $kid"
      done
    done
    frontier="$next"
  done
}

# Verdict for one pid, printed as a single word plus detail. Never signals anything.
_verdict() {
  local pid="$1" cwd="$2" anc="$3"
  if [ -n "$anc" ]; then
    echo "OURS (descends from tracked launcher $anc)"
    return
  fi
  case "$cwd" in
    "$ROOT"*) echo "PROBABLY OURS (cwd is this repo, but not descended from a tracked launcher)" ;;
    "")       echo "UNKNOWN (cwd unreadable) — DO NOT TOUCH" ;;
    *)        echo "NOT OURS (cwd belongs to another project) — DO NOT TOUCH" ;;
  esac
}

cmd="${1:-tree}"

case "$cmd" in

  track)
    pid="$2"; label="${3:-unlabelled}"
    if [ -z "$pid" ]; then echo "usage: ours.sh track <pid> <label>"; exit 1; fi
    if ! _alive "$pid"; then echo "refusing: pid $pid is not alive"; exit 1; fi
    cwd="$(_cwd_of "$pid")"
    case "$cwd" in
      "$ROOT"*) ;;
      *) echo "WARNING: pid $pid cwd is '${cwd:-<unreadable>}', outside $ROOT." ;;
    esac
    echo "$pid $label started=$(date +%Y-%m-%dT%H:%M:%S) boot=$(_boot) cwd=${cwd:-?}" >> "$LEDGER"
    echo "tracked: $pid ($label)"
    ;;

  tree)
    echo "OUR TRACKED LAUNCHERS AND THEIR LIVE DESCENDANTS"
    echo "ledger: $LEDGER"
    any=0
    while read -r pid label rest; do
      if [ -z "$pid" ]; then continue; fi
      if _alive "$pid"; then
        any=1
        printf "\n  [LIVE] %s  %s  (%s)\n" "$pid" "$label" "$(_etime_of "$pid")"
        printf "         %s\n" "$(_cmd_of "$pid" | cut -c1-100)"
        for d in $(_descendants "$pid"); do
          printf "     └─ %s  %s  %s\n" "$d" "$(_etime_of "$d")" "$(_cmd_of "$d" | cut -c1-88)"
        done
      elif [ -n "$(_is_stale "$pid")" ]; then
        printf "  [STALE - previous boot, PID may now belong to anyone] %s  %s\n" "$pid" "$label"
      else
        printf "  [dead] %s  %s\n" "$pid" "$label"
      fi
    done < "$LEDGER"
    if [ "$any" = 0 ]; then echo "  (no live tracked launchers)"; fi
    ;;

  whose)
    pid="$2"
    if [ -z "$pid" ]; then echo "usage: ours.sh whose <pid>"; exit 1; fi
    if ! _alive "$pid"; then
      echo "pid $pid: NOT RUNNING (already exited)"
      echo "  Note: short-lived children are normal — our gate spawns one python per battery."
      exit 0
    fi
    cwd="$(_cwd_of "$pid")"
    anc="$(_tracked_ancestor "$pid")"
    if [ -n "$(_is_stale "$pid")" ]; then
      echo "pid $pid"
      echo "  VERDICT : STALE LEDGER ENTRY (written before the current boot)."
      echo "            This PID was ours in a PREVIOUS boot; it may now belong to any"
      echo "            process. DO NOT TOUCH. Run 'ours.sh prune' to clear it."
      exit 0
    fi
    echo "pid $pid"
    echo "  command : $(_cmd_of "$pid" | cut -c1-120)"
    echo "  cwd     : ${cwd:-<unreadable>}"
    echo "  elapsed : $(_etime_of "$pid")"
    echo "  ancestry: $(_ancestry_chain "$pid")"
    echo "  VERDICT : $(_verdict "$pid" "$cwd" "$anc")"
    ;;

  all)
    echo "ALL PYTHON PROCESSES, ATTRIBUTED"
    found=0
    for p in $(pgrep -f "python" 2>/dev/null); do
      found=1
      cwd="$(_cwd_of "$p")"
      anc="$(_tracked_ancestor "$p")"
      printf "  %-7s %s\n" "$p" "$(_verdict "$p" "$cwd" "$anc")"
      printf "          cwd: %s\n" "${cwd:-?}"
      printf "          %s\n" "$(_cmd_of "$p" | cut -c1-92)"
    done
    if [ "$found" = 0 ]; then echo "  (no python processes running)"; fi
    ;;

  prune)
    tmp="$(mktemp)"; n=0
    while read -r pid rest; do
      if [ -z "$pid" ]; then continue; fi
      if _alive "$pid"; then
        echo "$pid $rest" >> "$tmp"
      else
        n=$((n + 1))
      fi
    done < "$LEDGER"
    mv "$tmp" "$LEDGER"
    echo "pruned $n dead launcher(s); $(wc -l < "$LEDGER" | tr -d ' ') remain"
    ;;

  *)
    sed -n '2,25p' "$0" | sed 's/^# \{0,1\}//'
    ;;
esac

exit 0
