[Mon 00:58:15] === r6 queue start, driver 69758; prediction sealed at 34d14b6; hard stop 2026-10-05 09:30; parallel only if sector-0 peak <= 14 GB
[Mon 00:58:15]   hard-stop deadline: Mon 2026-10-05 09:30:00
[Mon 00:58:15]   launch prime 0 sector 0
[Mon 01:06:32] === r6 queue v3 start, driver 72830; ONE process at a time; no deadline; prediction sealed at 34d14b6
[Mon 01:06:32]   waiting for the running sector process (pid 69794) from the previous driver
[Mon 01:51:59] STOPPED: watchdog fired at 01:50:34 -- sector 0 (prime 0) tree 14.98 GB > 14 GB cap, 45 min into its Rust solve (ktsolve 12 GB and still growing, Python parent holding 3.0 GB). Sector 0 UNFINISHED; no rank-6 result. Per the Bridge's rule 3: stop and report, no relaunch.
