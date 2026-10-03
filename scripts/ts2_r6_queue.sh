#!/bin/zsh
# TS delta=2 p=4/5 RANK 6, per parity sector (Bridge GO 2026-10-04; prediction sealed in data/ts2_exact/R6_PREDICTION.md).
# Prime 0 first: two processes in parallel (sectors 0,1 | 2,3; each sector is ONE Rust block, so ~1 thread each), then
# prime 1 the same way. Each sector's matrix file is a temp file the prover deletes after its nullspace + guard; the
# nullspace and hashes are saved per sector (json + npz). Any sector irreducible > 0 -> its second prime, then STOP.
# HARD STOP at $STOP_AT (default 13:30 today): the whole tree is killed; finished sectors stand, unfinished are labelled.
cd "${0:A:h}/.." || exit 2
exec < /dev/null
O=data/ts2_exact/r6; mkdir -p $O
STOP_AT="${STOP_AT:-13:30}"
log() { echo "[$(date '+%a %H:%M:%S')] $*" | tee -a $O/STATUS.md; }
git diff --quiet HEAD -- data/ts2_exact/R6_PREDICTION.md || { log "REFUSE: R6_PREDICTION.md not committed/sealed"; exit 4; }
log "=== r6 queue start, driver $$; prediction sealed at $(git log -1 --format=%h -- data/ts2_exact/R6_PREDICTION.md); hard stop $STOP_AT"
( deadline=$(date -j -f '%H:%M' "$STOP_AT" +%s); while [ $(date +%s) -lt $deadline ]; do sleep 30; kill -0 $$ 2>/dev/null || exit 0; done
  me=$(cat $O/timer.pid 2>/dev/null)
  echo "[$(date '+%a %H:%M:%S')] HARD STOP $STOP_AT reached -- killing the r6 tree" >> $O/STATUS.md
  tree() { echo $1; for k in $(pgrep -P $1); do tree $k; done; }
  for p in $(tree $$ | tail -r); do [ "$p" != "$$" ] && [ "$p" != "$me" ] && kill -KILL $p 2>/dev/null; done
  kill -KILL $$ 2>/dev/null ) &
echo $! > $O/timer.pid
run() {  # $1 prime, $2 sectors
  local o=$O/r6_p$1_s${2//,/}.out
  log "  launch prime $1 sectors $2 -> $o"
  KT_SOLVER=rust KT_THREADS=2 /usr/bin/time -l .venv/bin/python -u scripts/_kt_exact_sector.py --metric ts2:4/5 --rank 6 \
    --denpow 3 --prime $1 --sectors $2 --outdir $O > $o 2> $o.time
  log "  done prime $1 sectors $2: exit $? -- $(grep -h 'SECTOR [0-9]:' $o | sed 's/^ *//' | tr '\n' ' ')"
}
irr() { grep -h '"irreducible"' $O/ts24o5_r6_d3_b34x34_p$1_s$2.json 2>/dev/null | sed 's/.*"irreducible": \([0-9-]*\).*/\1/'; }
for P in 0 1; do
  run $P 0,1 & a=$!; run $P 2,3 & b=$!; wait $a $b
  for s in 0 1 2 3; do
    v=$(irr $P $s)
    if [ -z "$v" ]; then log "  prime $P sector $s: NO RESULT (crash, condemned, or hard stop) -- labelled unfinished"; continue; fi
    if [ "$v" != "0" ]; then
      log "  POSITIVE: prime $P sector $s irreducible $v"
      [ $P = 0 ] && run 1 $s
      log "STOP: irreducible content in sector $s; no claim -- to the Bridge for an independent check"
      echo "ansatz r6: POSITIVE in sector $s (prime $P: $v; prime 1: $(irr 1 $s)). STOPPED. See $O/STATUS.md" > /Users/sumit/Github/.claude-coordination/inbox/bridge/$(date +%F)_ansatz_r6_POSITIVE.md
      exit 0
    fi
  done
  log "--- prime $P complete: $(for s in 0 1 2 3; do echo -n "s$s=$(irr $P $s) "; done)"
done
log "=== r6 queue finished"
