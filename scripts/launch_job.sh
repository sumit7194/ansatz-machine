#!/usr/bin/env bash
# Launch ONE sealed job from data/anat/weekend/PREDICTIONS.json, fully detached (survives a closed terminal
# and a closed Claude app).  Usage:  scripts/launch_job.sh <job-name> [threads]
# Starts: the driver (weekend_rank8.sh: sealed predictions, calibrated scorer, PID records, verdict),
#         the watchdog (whole-tree footprint every minute; SIGKILL the tree if free disk < 5 GB),
#         caffeinate tied to the driver (Mac stays awake exactly as long as the job runs).
# Generalises launch_job2.sh (kept for provenance of job 2).
set -u
cd "$(dirname "$0")/.." || exit 2
exec < /dev/null
job="${1:?usage: scripts/launch_job.sh <job-name> [threads]}"; threads="${2:-2}"
W=data/anat/weekend
out=$(.venv/bin/python -c "
import json; j={x['name']:x for x in json.load(open('$W/PREDICTIONS.json'))['jobs']}.get('$job')
print(j['out'] if j and j.get('cmd','-') != '-' else '')")
[ -n "$out" ] || { echo "REFUSE: no runnable job '$job' in $W/PREDICTIONS.json"; exit 3; }
# an unfinished .out from an earlier attempt would be treated as a fresh run's output: set it aside, never delete
if [ -f "$out" ] && ! grep -q "^  total [0-9]*s" "$out"; then mv -n "$out" "${out%.out}_INCOMPLETE_$(date +%Y%m%d-%H%M).out"; fi
THREADS=$threads QUEUE="$job" nohup scripts/weekend_rank8.sh > "$W/driver_$job.log" 2>&1 &
drv=$!
DISK_MIN_GB=5 INTERVAL=60 nohup scripts/job2_watchdog.sh "$drv" "$job" > "$W/watchdog_$job.log" 2>&1 &
wd=$!
nohup caffeinate -i -w "$drv" > /dev/null 2>&1 &
cf=$!
echo "launched $job: driver $drv, watchdog $wd, caffeinate $cf   ($(date '+%F %T'))"
echo "$drv $wd $cf $(date '+%F %T') launch_job.sh $job threads=$threads" >> "$W/PIDS_jobs"
