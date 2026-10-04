#!/bin/zsh
# r6 continuation (Bridge pre-authorisation 2026-10-05): after the lean sector-0/prime-0 run (WAIT_PID) finishes UNDER
# the caps, run p0 sectors 1,2,3 then p1 sectors 0..3, one lean process at a time, each with its OWN watchdog
# (tree <= 15 GB, memory_pressure free >= 8%, disk >= 6 GB). A capped sector is labelled UNFINISHED and skipped.
# Irreducible > 0 -> that sector's other prime -> STOP. No deadline: runs until the user's call.
cd "${0:A:h}/.." || exit 2
exec < /dev/null
O=data/ts2_exact/r6; TPL=$O/templates
log() { echo "[$(date '+%a %H:%M:%S')] $*" | tee -a $O/STATUS.md; }
irr() { grep -h '"irreducible"' $O/ts24o5_r6_d3_b34x34_p$1_s$2.json 2>/dev/null | sed 's/.*"irreducible": \([0-9-]*\).*/\1/'; }
log "=== r6 lean continuation, driver $$; waiting for sector 0 prime 0 (pid ${WAIT_PID:-none})"
[ -n "${WAIT_PID:-}" ] && while kill -0 $WAIT_PID 2>/dev/null; do sleep 30; done
[ -n "$(irr 0 0)" ] || { log "STOP: sector 0 prime 0 has no result (capped or failed) -- continuation not authorised"; exit 3; }
run() {
  local o=$O/lean_p$1_s$2.out
  log "  launch prime $1 sector $2 (lean)"
  KT_THREADS=1 /usr/bin/time -l zsh scripts/lean_sector.sh ts2:4/5 6 3 $1 $2 $O $TPL > $o 2> $o.time &
  local r=$!
  FOOT_MAX_GB=15 MP_MIN=8 DISK_MIN_GB=6 INTERVAL=60 zsh scripts/tree_watchdog2.sh "$r" r6p$1s$2 > $O/watchdog_p$1_s$2.log 2>&1 &
  local w=$!
  wait $r; wait $w 2>/dev/null
  rm -f $O/ts24o5_r6_d3_b34x34_p$1_s$2.ktm $O/ts24o5_r6_d3_b34x34_p$1_s$2.ktm.kts   # a killed run leaves its matrix behind
  if [ -n "$(irr $1 $2)" ]; then log "  done prime $1 sector $2: $(grep -h 'SECTOR [0-9]:' $o | sed 's/^ *//') -- tree peak $(grep -o 'peak [0-9.]*' $O/watchdog_p$1_s$2.log | tail -1)"
  else log "  prime $1 sector $2: UNFINISHED ($(grep -h FIRED $O/watchdog_p$1_s$2.log || echo 'no result')) -- skipped"; fi
}
positive() { log "  POSITIVE: prime $1 sector $2 irreducible $(irr $1 $2)"; o=$((1-$1)); [ -z "$(irr $o $2)" ] && run $o $2
  log "STOP: irreducible content in sector $2 (p0: $(irr 0 $2); p1: $(irr 1 $2)); no claim -- to the Bridge"
  echo "ansatz r6: POSITIVE in sector $2 (p0: $(irr 0 $2); p1: $(irr 1 $2)). STOPPED, no claim." > /Users/sumit/Github/.claude-coordination/inbox/bridge/$(date +%F)_ansatz_r6_POSITIVE.md; exit 0; }
[ "$(irr 0 0)" != "0" ] && positive 0 0
for P in 0 1; do for S in 0 1 2 3; do
  [ -n "$(irr $P $S)" ] || run $P $S
  v=$(irr $P $S); [ -n "$v" ] && [ "$v" != "0" ] && positive $P $S
done; log "--- prime $P pass done: s0=$(irr $P 0) s1=$(irr $P 1) s2=$(irr $P 2) s3=$(irr $P 3) (empty = unfinished)"; done
log "=== r6 lean continuation finished"
