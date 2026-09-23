#!/usr/bin/env bash
# Launch job 2 (section-143 second-prime reproduction, l4_r8_p1) ONLY on The Bridge's "go job 2".
# Driver: weekend_rank8.sh (sealed predictions, calibrated scorer, PID records, verdict from the VERDICT line).
# THREADS=2 (was 4): fewer Rust blocks in memory at once -> lower peak; the result is identical (RREF is unique),
# only wall time grows.  Watchdog: whole-tree footprint logged every minute; SIGKILL the tree if free disk < 5 GB.
set -u
cd "$(dirname "$0")/.." || exit 2
exec < /dev/null
W=data/anat/weekend; out=$W/reduced_r8_l4_p1.out
if [ -f "$out" ] && ! grep -q "^  total [0-9]*s" "$out"; then mv -n "$out" "$W/reduced_r8_l4_p1_KILLED_2026-09-24.out"; fi
THREADS=2 QUEUE="l4_r8_p1" nohup scripts/weekend_rank8.sh > "$W/driver_job2.log" 2>&1 &
drv=$!
DISK_MIN_GB=5 INTERVAL=60 nohup scripts/job2_watchdog.sh "$drv" job2 > "$W/watchdog_job2.log" 2>&1 &
wd=$!
echo "launched: driver $drv, watchdog $wd   ($(date '+%F %T'))"
echo "$drv $wd $(date '+%F %T') launch_job2.sh" >> "$W/PIDS_job2"
