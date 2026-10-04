#!/bin/zsh
# TS delta=2 p=4/5 RANK 6, one parity sector per process (Bridge GO 2026-10-04; prediction sealed in
# data/ts2_exact/R6_PREDICTION.md). Templates come from the exact cache (data/ts2_exact/r6/templates_p{0,1}.npz,
# built once by _kt_templates_cache.py, selftest == _kt_opfast). ADAPTIVE, per the Bridge's caps:
#   prime 0: sector 0 ALONE; its measured peak footprint decides the rest -- <= PAR_MAX_GB (14): two sectors at a time
#            (2-slot scheduler), else one at a time. Then prime 1 the same way.
# Each sector's matrix file is a temp file the prover deletes after its nullspace + guard; results saved per sector.
# Any sector irreducible > 0 -> stop the other running sector, run that sector's second prime, STOP.
# HARD STOP at $STOP_AT (13:30): the whole tree is killed; finished sectors stand, unfinished are labelled.
cd "${0:A:h}/.." || exit 2
exec < /dev/null
O=data/ts2_exact/r6; mkdir -p $O
STOP_AT="${STOP_AT:-13:30}"; PAR_MAX_GB="${PAR_MAX_GB:-14}"; TPL=$O/templates
log() { echo "[$(date '+%a %H:%M:%S')] $*" | tee -a $O/STATUS.md; }
git diff --quiet HEAD -- data/ts2_exact/R6_PREDICTION.md && git ls-files --error-unmatch data/ts2_exact/R6_PREDICTION.md >/dev/null 2>&1 \
  || { log "REFUSE: R6_PREDICTION.md not committed (sealed)"; exit 4; }
[ -f ${TPL}_p0.npz ] && [ -f ${TPL}_p1.npz ] || { log "REFUSE: template cache missing"; exit 4; }
log "=== r6 queue start, driver $$; prediction sealed at $(git log -1 --format=%h -- data/ts2_exact/R6_PREDICTION.md); hard stop $STOP_AT; parallel only if sector-0 peak <= ${PAR_MAX_GB} GB"
DEADLINE=$(date -j -f '%H:%M:%S' "$STOP_AT:00" +%s); [ $DEADLINE -le $(date +%s) ] && DEADLINE=$((DEADLINE + 86400))   # NEXT $STOP_AT
log "  hard-stop deadline: $(date -r $DEADLINE '+%a %F %T')"
( deadline=$DEADLINE; while [ $(date +%s) -lt $deadline ]; do sleep 30; kill -0 $$ 2>/dev/null || exit 0; done
  me=$(cat $O/timer.pid 2>/dev/null)
  echo "[$(date '+%a %H:%M:%S')] HARD STOP $STOP_AT reached -- killing the r6 tree; unfinished sectors are labelled" >> $O/STATUS.md
  tree() { echo $1; for k in $(pgrep -P $1); do tree $k; done; }
  for p in $(tree $$ | tail -r); do [ "$p" != "$$" ] && [ "$p" != "$me" ] && kill -KILL $p 2>/dev/null; done
  kill -KILL $$ 2>/dev/null ) &
echo $! > $O/timer.pid
start() {  # $1 prime, $2 sector -> runs in background, echoes nothing; pid in $O/run_p$1_s$2.pid
  local o=$O/r6_p$1_s$2.out
  log "  launch prime $1 sector $2"
  ( KT_SOLVER=rust KT_THREADS=1 /usr/bin/time -l .venv/bin/python -u scripts/_kt_exact_sector.py --metric ts2:4/5 --rank 6 \
      --denpow 3 --prime $1 --sectors $2 --outdir $O --templates-cache $TPL > $o 2> $o.time
    log "  done prime $1 sector $2: exit $? -- $(grep -h 'SECTOR [0-9]:' $o | sed 's/^ *//') -- peak $(awk '/peak memory footprint/{printf "%.2f GB",$1/1073741824}' $o.time)" ) &
  echo $! > $O/run_p$1_s$2.pid
}
irr() { grep -h '"irreducible"' $O/ts24o5_r6_d3_b34x34_p$1_s$2.json 2>/dev/null | sed 's/.*"irreducible": \([0-9-]*\).*/\1/'; }
peak_gb() { awk '/peak memory footprint/{printf "%d", $1/1073741824 + 0.999}' $O/r6_p$1_s$2.out.time 2>/dev/null; }
positive() {  # $1 prime, $2 sector
  log "  POSITIVE: prime $1 sector $2 irreducible $(irr $1 $2)"
  for f in $O/run_p*_s*.pid; do kill -0 $(cat $f) 2>/dev/null && { log "  stopping running $(basename $f .pid) (partial, labelled)"; pkill -KILL -P $(cat $f); kill -KILL $(cat $f); }; done
  if [ $1 = 0 ]; then start 1 $2; wait $(cat $O/run_p1_s$2.pid); fi
  log "STOP: irreducible content in sector $2 (prime 0: $(irr 0 $2); prime 1: $(irr 1 $2)); no claim -- to the Bridge"
  echo "ansatz r6: POSITIVE in sector $2 (p0: $(irr 0 $2); p1: $(irr 1 $2)). STOPPED, no claim. See $O/STATUS.md" \
    > /Users/sumit/Github/.claude-coordination/inbox/bridge/$(date +%F)_ansatz_r6_POSITIVE.md
  exit 0
}
check() { local v=$(irr $1 $2); [ -z "$v" ] && { log "  prime $1 sector $2: NO RESULT (crash/condemned/killed) -- unfinished"; return 1; }; [ "$v" != "0" ] && positive $1 $2; return 0; }
for P in 0 1; do
  start $P 0; wait $(cat $O/run_p${P}_s0.pid); check $P 0
  pk=$(peak_gb $P 0); slots=1; [ -n "$pk" ] && [ $pk -le $PAR_MAX_GB ] && slots=2
  log "  prime $P sector 0 peak ${pk:-?} GB -> ${slots} sector(s) at a time for sectors 1-3"
  queue=(1 2 3); running=()
  while [ ${#queue} -gt 0 ] || [ ${#running} -gt 0 ]; do
    while [ ${#running} -lt $slots ] && [ ${#queue} -gt 0 ]; do s=${queue[1]}; queue=(${queue[2,-1]}); start $P $s; running+=($s); done
    sleep 20
    for s in $running; do kill -0 $(cat $O/run_p${P}_s$s.pid) 2>/dev/null || { running=(${running:#$s}); check $P $s; }; done
  done
  log "--- prime $P complete: s0=$(irr $P 0) s1=$(irr $P 1) s2=$(irr $P 2) s3=$(irr $P 3)"
done
log "=== r6 queue finished"
