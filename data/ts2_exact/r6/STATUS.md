[Mon 00:58:15] === r6 queue start, driver 69758; prediction sealed at 34d14b6; hard stop 2026-10-05 09:30; parallel only if sector-0 peak <= 14 GB
[Mon 00:58:15]   hard-stop deadline: Mon 2026-10-05 09:30:00
[Mon 00:58:15]   launch prime 0 sector 0
[Mon 01:06:32] === r6 queue v3 start, driver 72830; ONE process at a time; no deadline; prediction sealed at 34d14b6
[Mon 01:06:32]   waiting for the running sector process (pid 69794) from the previous driver
[Mon 01:51:59] STOPPED: watchdog fired at 01:50:34 -- sector 0 (prime 0) tree 14.98 GB > 14 GB cap, 45 min into its Rust solve (ktsolve 12 GB and still growing, Python parent holding 3.0 GB). Sector 0 UNFINISHED; no rank-6 result. Per the Bridge's rule 3: stop and report, no relaunch.
[Mon 02:13:01] === RELAUNCH sector 0 prime 0 via LEAN launch (Bridge lever (a)); watchdog: tree <= 15 GB, memory_pressure free >= 8%, disk >= 6 GB; no deadline
[Mon 02:13:53] === r6 lean continuation, driver 92041; waiting for sector 0 prime 0 (pid 91741)
[Mon 03:24:55] STOP: sector 0 prime 0 has no result (capped or failed) -- continuation not authorised
[Mon 03:26:16] STOPPED for the night: lean sector 0 prime 0 capped at 03:24:45 -- ktsolve ALONE reached 15.00 GB after 65 min of solving. Sector 0 UNFINISHED (second attempt). No retry tonight per the Bridge; lever (b) is daytime design work.
