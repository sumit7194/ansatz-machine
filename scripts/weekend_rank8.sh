#!/usr/bin/env bash
# Weekend rank-8 queue: one job at a time, predictions sealed before anything runs.
#
# START IT (detached, so it survives the Claude session and a closed terminal):
#     nohup scripts/weekend_rank8.sh > data/anat/weekend/driver.log 2>&1 &
# TRY IT FIRST (gates + calibration only, launches nothing heavy):
#     scripts/weekend_rank8.sh --dry-run
#
# WHAT IT GUARANTEES, and why each guard exists:
#  1. PREDICTIONS.json must be committed and unmodified, or it refuses to start. A prediction
#     written after the output exists is not a prediction.
#  2. The checker is calibrated before any job: it must say MATCH on a known reproduction and
#     MISMATCH on a planted error. A scorer that has only ever said "match" has not been shown able
#     to say anything else.
#  3. ONE job at a time, and only once enough memory is free (MIN_GB, default 8). The machine has
#     16 GB and is shared with sister sessions; the last rank-8 run peaked at ~331M nonzeros, so two
#     at once is how a weekend ends in swap.
#  4. Resumable: a job whose .out already ends in "total ...s" is skipped, so a restart re-runs only
#     what did not finish.
#  5. Every PID it launches is written to data/anat/weekend/PIDS with its argv, so our processes can
#     be identified exactly -- never by pattern -- and nobody else's are touched.
#  6. Each job is scored automatically by scripts/_kt_weekend_check.py and the verdict is appended to
#     STATUS.md along with wall time and peak RSS. Nothing is committed: results are reviewed first.
#
# Live throttle for a single running job:   echo 2 > data/KT_THREADS.<pid>
set -u
cd "$(dirname "$0")/.." || exit 2

QUEUE="${QUEUE:-o3_r8_p0 l4_r8_p1 o3_r8_p1}"
THREADS="${THREADS:-4}"
MIN_GB="${MIN_GB:-8}"
DRY=0; [ "${1:-}" = "--dry-run" ] && DRY=1
W=data/anat/weekend
PRED=$W/PREDICTIONS.json
PY=.venv/bin/python
mkdir -p "$W"
log() { echo "[$(date '+%a %H:%M:%S')] $*" | tee -a "$W/STATUS.md"; }

avail_gb() {   # free + inactive + speculative + purgeable pages: what the OS can hand out without swapping
  vm_stat | awk -v ps="$(sysctl -n hw.pagesize)" '
    /Pages free/{f=$3} /Pages inactive/{i=$3} /Pages speculative/{s=$3} /Pages purgeable/{p=$3}
    END{gsub(/\./,"",f);gsub(/\./,"",i);gsub(/\./,"",s);gsub(/\./,"",p); printf "%d", (f+i+s+p)*ps/1073741824}'
}

log "=== weekend_rank8 start (dry-run=$DRY) queue: $QUEUE  threads=$THREADS  min_free=${MIN_GB}GB  driver pid $$"

# 1. sealed predictions
if ! git ls-files --error-unmatch "$PRED" >/dev/null 2>&1; then log "REFUSE: $PRED is not committed"; exit 3; fi
if ! git diff --quiet HEAD -- "$PRED"; then log "REFUSE: $PRED has uncommitted edits -- predictions must be sealed"; exit 3; fi
log "predictions sealed at commit $(git log -1 --format=%h -- "$PRED")"

# 2. calibrate the scorer in both directions
$PY scripts/_kt_weekend_check.py calib_repro_must_match > "$W/calib_match.txt" 2>&1; a=$?
$PY scripts/_kt_weekend_check.py calib_sabotage_must_miss > "$W/calib_miss.txt" 2>&1; b=$?
if [ $a -ne 0 ] || [ $b -ne 1 ]; then log "REFUSE: checker calibration failed (match exit $a want 0; sabotage exit $b want 1)"; exit 4; fi
log "checker calibrated: MATCH on the known reproduction, MISMATCH on the planted error"

for job in $QUEUE; do
  # out first: it has no spaces, and read hands the WHOLE remainder of the line to the last variable
  read -r out cmd < <($PY -c "
import json,sys; j={x['name']:x for x in json.load(open('$PRED'))['jobs']}.get('$job')
print((j or {}).get('out','-'), (j or {}).get('cmd','-'))")
  if [ "$cmd" = "-" ]; then log "SKIP $job: no such job (or no cmd) in $PRED"; continue; fi
  if [ -f "$out" ] && grep -q "^  total [0-9]*s" "$out"; then log "SKIP $job: already complete ($out)"; continue; fi

  # 3. memory gate
  while :; do
    g=$(avail_gb)
    [ "$g" -ge "$MIN_GB" ] && break
    [ $DRY -eq 1 ] && { log "(dry-run) $job would WAIT: ${g}GB free < ${MIN_GB}GB"; break; }
    log "$job waiting: ${g}GB free < ${MIN_GB}GB; rechecking in 10 min"; sleep 600
  done
  if [ $DRY -eq 1 ]; then log "(dry-run) would launch $job: $cmd -> $out  [${g}GB free]"; continue; fi

  log "LAUNCH $job: $cmd  [${g}GB free]"
  t0=$(date +%s)
  { KT_SOLVER=rust KT_THREADS=$THREADS /usr/bin/time -l $PY -u scripts/_kt_pole_reduced.py $cmd > "$out" 2>&1; } 2> "$out.time" &
  pid=$!
  echo "$pid $job $(date '+%F %T') KT_SOLVER=rust KT_THREADS=$THREADS scripts/_kt_pole_reduced.py $cmd" >> "$W/PIDS"
  wait $pid; rc=$?
  mins=$(( ($(date +%s) - t0) / 60 ))
  rss=$(awk '/maximum resident set size/{printf "%.1f GB", $1/1073741824}' "$out.time" 2>/dev/null)
  if [ $rc -ne 0 ] || ! grep -q "^  total [0-9]*s" "$out"; then
    log "FAILED $job: exit $rc after ${mins} min, peak ${rss:-?}; last lines:"; tail -5 "$out" | tee -a "$W/STATUS.md"
    continue
  fi
  $PY scripts/_kt_weekend_check.py "$job" > "$out.check" 2>&1; v=$?
  verdict=$([ $v -eq 0 ] && echo MATCH || ([ $v -eq 1 ] && echo MISMATCH || echo UNSCORABLE))
  log "DONE $job: ${mins} min, peak ${rss:-?}, verdict $verdict  (details: $out.check)"
done
log "=== queue finished"
