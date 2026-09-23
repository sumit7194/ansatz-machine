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
