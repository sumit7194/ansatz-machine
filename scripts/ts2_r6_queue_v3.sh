#!/bin/zsh
# TS delta=2 p=4/5 RANK 6 -- v3: ONE sector process at a time (16 GiB box; Bridge/user 2026-10-05), NO deadline (the
# user stops it in the morning). Skips sectors already finished (json present). If WAIT_PID is given (a sector process
# left running by the previous driver), waits for it first so no sector work is lost. Prime 0 sectors 0..3, then prime 1.
# Any sector irreducible > 0 -> that sector's second prime -> STOP (no claim; to the Bridge). Prediction sealed 34d14b6.
# (v2, ts2_r6_queue.sh, is left untouched: a running zsh reads its script from disk -- rule 118.)
cd "${0:A:h}/.." || exit 2
exec < /dev/null
O=data/ts2_exact/r6; TPL=$O/templates
log() { echo "[$(date '+%a %H:%M:%S')] $*" | tee -a $O/STATUS.md; }
git diff --quiet HEAD -- data/ts2_exact/R6_PREDICTION.md || { log "REFUSE: R6_PREDICTION.md modified"; exit 4; }
log "=== r6 queue v3 start, driver $$; ONE process at a time; no deadline; prediction sealed at $(git log -1 --format=%h -- data/ts2_exact/R6_PREDICTION.md)"
irr() { grep -h '"irreducible"' $O/ts24o5_r6_d3_b34x34_p$1_s$2.json 2>/dev/null | sed 's/.*"irreducible": \([0-9-]*\).*/\1/'; }
if [ -n "${WAIT_PID:-}" ]; then log "  waiting for the running sector process (pid $WAIT_PID) from the previous driver"; while kill -0 $WAIT_PID 2>/dev/null; do sleep 20; done; fi
run() {
  local o=$O/r6_p$1_s$2.out
  log "  launch prime $1 sector $2"
  KT_SOLVER=rust KT_THREADS=1 /usr/bin/time -l .venv/bin/python -u scripts/_kt_exact_sector.py --metric ts2:4/5 --rank 6 \
    --denpow 3 --prime $1 --sectors $2 --outdir $O --templates-cache $TPL > $o 2> $o.time
  log "  done prime $1 sector $2: exit $? -- $(grep -h 'SECTOR [0-9]:' $o | sed 's/^ *//') -- peak $(awk '/peak memory footprint/{printf "%.2f GB",$1/1073741824}' $o.time)"
}
for P in 0 1; do
  for S in 0 1 2 3; do
    [ -n "$(irr $P $S)" ] || run $P $S
    v=$(irr $P $S)
    if [ -z "$v" ]; then log "  prime $P sector $S: NO RESULT (crash/condemned/killed) -- unfinished; STOP"; exit 3; fi
    if [ "$v" != "0" ]; then
      log "  POSITIVE: prime $P sector $S irreducible $v"
      [ $P = 0 ] && [ -z "$(irr 1 $S)" ] && run 1 $S
      log "STOP: irreducible content in sector $S (p0: $(irr 0 $S); p1: $(irr 1 $S)); no claim -- to the Bridge"
      echo "ansatz r6: POSITIVE in sector $S (p0: $(irr 0 $S); p1: $(irr 1 $S)). STOPPED, no claim." > /Users/sumit/Github/.claude-coordination/inbox/bridge/$(date +%F)_ansatz_r6_POSITIVE.md
      exit 0
    fi
  done
  log "--- prime $P complete: s0=$(irr $P 0) s1=$(irr $P 1) s2=$(irr $P 2) s3=$(irr $P 3)"
done
log "=== r6 queue finished"
