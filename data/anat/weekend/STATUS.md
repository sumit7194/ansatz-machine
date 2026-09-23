[Tue 23:21:54] === weekend_rank8 start (dry-run=1) queue: o3_r8_p0 l4_r8_p1 o3_r8_p1  threads=4  min_free=8GB  driver pid 92928
[Tue 23:21:54] predictions sealed at commit c1b6fab
[Tue 23:21:54] checker calibrated: MATCH on the known reproduction, MISMATCH on the planted error
[Tue 23:21:54] (dry-run) o3_r8_p0 would WAIT: 5GB free < 8GB
[Tue 23:21:54] (dry-run) would launch o3_r8_p0: --rank 8 --denpow 7 --margin 4 --prime 0 --slots o3tphi,o3rphi,o3yphi -> data/anat/weekend/reduced_r8_o3_p0.out  [5GB free]
[Tue 23:21:54] (dry-run) l4_r8_p1 would WAIT: 5GB free < 8GB
[Tue 23:21:54] (dry-run) would launch l4_r8_p1: --rank 8 --denpow 7 --margin 4 --prime 1 --axial-controls 0 --slots l4tt,l4rr,l4ang -> data/anat/weekend/reduced_r8_l4_p1.out  [5GB free]
[Tue 23:21:54] (dry-run) o3_r8_p1 would WAIT: 5GB free < 8GB
[Tue 23:21:54] (dry-run) would launch o3_r8_p1: --rank 8 --denpow 7 --margin 4 --prime 1 --slots o3tphi,o3rphi,o3yphi -> data/anat/weekend/reduced_r8_o3_p1.out  [5GB free]
[Tue 23:21:54] === queue finished
[Wed 12:44:40] === weekend_rank8 start (dry-run=0) queue: o3_r8_p0 l4_r8_p1 o3_r8_p1  threads=4  min_free=8GB  driver pid 96750
[Wed 12:44:41] predictions sealed at commit c1b6fab
[Wed 12:44:41] checker calibrated: MATCH on the known reproduction, MISMATCH on the planted error
[Wed 12:44:41] LAUNCH o3_r8_p0: --rank 8 --denpow 7 --margin 4 --prime 0 --slots o3tphi,o3rphi,o3yphi  [8GB free]
[Wed 12:44:46]   o3_r8_p0: subshell 96778, python 96781  (throttle live: echo 2 > data/KT_THREADS.96781)
[Wed 14:56:21] === weekend_rank8 start (dry-run=0) queue: o3_r8_p0 l4_r8_p1 o3_r8_p1  threads=4  min_free=8GB  driver pid 7417
[Wed 14:56:21] predictions sealed at commit e21267f
[Wed 14:56:21] checker calibrated: MATCH on the known reproduction, MISMATCH on the planted error
[Wed 14:56:21] LAUNCH o3_r8_p0: --rank 8 --denpow 7 --margin 4 --prime 0 --slots o3tphi,o3rphi,o3yphi  [11GB free]
[Wed 14:56:26]   o3_r8_p0: subshell 7446, python 7449  (throttle live: echo 2 > data/KT_THREADS.7449)
[Wed 17:56:07] DONE o3_r8_p0: 179 min, peak ?, verdict MISMATCH  (details: data/anat/weekend/reduced_r8_o3_p0.out.check)
[Wed 17:56:07] LAUNCH l4_r8_p1:   [10GB free]
[Wed 17:56:37]   l4_r8_p1: subshell 20703, python NOT FOUND  (throttle live: echo 2 > data/KT_THREADS.<pid>)
[Wed 17:56:37] FAILED l4_r8_p1: exit 1 after 0 min, peak ?; last lines:
[Wed 17:56:37] LAUNCH o3_r8_p1:   [10GB free]
[Wed 17:57:07]   o3_r8_p1: subshell 20802, python NOT FOUND  (throttle live: echo 2 > data/KT_THREADS.<pid>)
[Wed 17:57:07] FAILED o3_r8_p1: exit 1 after 0 min, peak ?; last lines:
[Wed 17:57:07] === queue finished
[Wed 17:58:41] === weekend_rank8 start (dry-run=1) queue: o3_r8_p0_m6 l4_r8_p1 o3_r8_p1_m6  threads=4  min_free=8GB  driver pid 21041
[Wed 17:58:41] predictions sealed at commit a3821dc
[Wed 17:58:41] checker calibrated: MATCH on the known reproduction, MISMATCH on the planted error
[Wed 17:58:41] (dry-run) would launch o3_r8_p0_m6: --rank 8 --denpow 7 --margin 6 --prime 0 --slots o3tphi,o3rphi,o3yphi -> data/anat/weekend/reduced_r8_o3_p0_m6.out  [10GB free]
[Wed 17:58:41] (dry-run) would launch l4_r8_p1: --rank 8 --denpow 7 --margin 6 --prime 1 --axial-controls 0 --slots l4tt,l4rr,l4ang -> data/anat/weekend/reduced_r8_l4_p1.out  [10GB free]
[Wed 17:58:41] (dry-run) would launch o3_r8_p1_m6: --rank 8 --denpow 7 --margin 6 --prime 1 --slots o3tphi,o3rphi,o3yphi -> data/anat/weekend/reduced_r8_o3_p1_m6.out  [10GB free]
[Wed 17:58:41] === queue finished
[Wed 17:59:37] === weekend_rank8 start (dry-run=0) queue: o3_r8_p0_m6 l4_r8_p1 o3_r8_p1_m6  threads=4  min_free=8GB  driver pid 21187
[Wed 17:59:37] predictions sealed at commit a3821dc
[Wed 17:59:37] checker calibrated: MATCH on the known reproduction, MISMATCH on the planted error
[Wed 17:59:37] LAUNCH o3_r8_p0_m6: --rank 8 --denpow 7 --margin 6 --prime 0 --slots o3tphi,o3rphi,o3yphi  [10GB free]
[Wed 17:59:42]   o3_r8_p0_m6: subshell 21218, python 21220  (throttle live: echo 2 > data/KT_THREADS.21220)
[Wed 23:02:57] DONE o3_r8_p0_m6: 303 min, peak 9.4 GB, verdict MISMATCH  (details: data/anat/weekend/reduced_r8_o3_p0_m6.out.check)
[Wed 23:02:57] LAUNCH l4_r8_p1: --rank 8 --denpow 7 --margin 6 --prime 1 --axial-controls 0 --slots l4tt,l4rr,l4ang  [8GB free]
[Wed 23:03:02]   l4_r8_p1: subshell 55296, python 55298  (throttle live: echo 2 > data/KT_THREADS.55298)
[Wed 23:03:16] ANNOTATION (manual, ansatz-machine): the 17:56:07 line 'DONE o3_r8_p0 ... verdict MISMATCH' was logged from a CRASHED scorer (Python died in init_sys_streams, EBADF: the driver had lost stdin), whose exit 1 collided with the old MISMATCH code -- that line is NOT a verdict. Scored properly afterwards, the run is ALSO a MISMATCH for a real reason: random kept 24 < floor 25 (margin-4 box too narrow at rank 8), so it is invalid; every physics field incl. the bet matched. Superseded by o3_r8_p0_m6. Crash-vs-verdict path fixed in a3821dc (MISMATCH exit 10 + VERDICT-line check).
[Thu 00:25:59] FAILED l4_r8_p1: exit 1 after 83 min, peak 7.3 GB; last lines:
rank 8, L^7, box 27x28: 133980 unknowns, 55 Schwarzschild products (by Q power {0: 25, 1: 16, 2: 9, 3: 4, 4: 1}), prime 1 [45s]
  1210 sources built [86s]
    [eps chi^2 timing] lcm+compare 502.1s | clear 1832.0s = RESCALED 133980 operator columns as arrays, nnz 7,386,764 -> 567,818,793, by q (728 terms, 133.2s) + cleared 1210 sources; new denominator factor (x - 2)**27*(y - 1)**25*(y + 1)**25
[Thu 00:25:59] SKIP o3_r8_p1_m6: no such job (or no cmd) in data/anat/weekend/PREDICTIONS.json
[Thu 00:25:59] === queue finished
[Thu 00:26:46] ANNOTATION (manual): l4_r8_p1 was KILLED at 00:26 on a fleet memory/disk hold (whole-tree footprint ~23 GB, 21 GB of it compressed in the ktsolve child; swap 12.9/13.3 GB, data disk 95-96%). Not a physics failure; rerun later. L^8 pair held.
