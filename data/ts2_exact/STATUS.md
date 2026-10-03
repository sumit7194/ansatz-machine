[Sun 02:23:12] === ts2_exact_queue start, driver pid 45876, threads 2; predictions sealed at 788dcc9
[Sun 02:23:20]   kerr_r2 p0: exit 0, 0.1 min, peak footprint 0.26 GB
[Sun 02:23:28]   kerr_r2 p1: exit 0, 0.1 min, peak footprint 0.26 GB
[Sun 02:23:28] G1 kerr_r2: exact/reducible/irreducible = (5, 4, 1) (both primes), predicted (5, 4, 1) -> MATCH
[Sun 02:23:40]   kerr_r3 p0: exit 0, 0.2 min, peak footprint 0.47 GB
[Sun 02:23:53]   kerr_r3 p1: exit 0, 0.2 min, peak footprint 0.47 GB
[Sun 02:23:53] G1 kerr_r3: exact/reducible/irreducible = (8, 6, 2) (both primes), predicted (8, 6, 2) -> MATCH
[Sun 02:24:30]   kerr_r4 p0: exit 0, 0.6 min, peak footprint 1.60 GB
[Sun 02:25:07]   kerr_r4 p1: exit 0, 0.6 min, peak footprint 1.60 GB
[Sun 02:25:07] G1 kerr_r4: exact/reducible/irreducible = (14, 9, 5) (both primes), predicted (14, 9, 5) -> MATCH
[Sun 02:26:11]   zv2_r4 p0: exit 0, 1.1 min, peak footprint 4.91 GB
[Sun 02:27:14]   zv2_r4 p1: exit 0, 1.1 min, peak footprint 4.91 GB
[Sun 02:27:14] G1 zv2_r4: exact/reducible/irreducible = (9, 9, 0) (both primes), predicted (9, 9, 0) -> MATCH
[Sun 02:27:14] --- gate G1 PASSED
[Sun 02:30:46]   ts_r2 p0: exit 0, 3.5 min, peak footprint 3.00 GB
[Sun 02:34:22]   ts_r2 p1: exit 0, 3.6 min, peak footprint 2.99 GB
[Sun 02:34:22] G2 ts_r2: exact/reducible/irreducible = (4, 4, 0) (both primes), predicted (4, 4, 0) -> MATCH
[Sun 02:39:15]   ts_r3 p0: exit 0, 4.9 min, peak footprint 6.73 GB
[Sun 02:44:13]   ts_r3 p1: exit 0, 5.0 min, peak footprint 6.53 GB
[Sun 02:44:13] G2 ts_r3: exact/reducible/irreducible = (6, 6, 0) (both primes), predicted (6, 6, 0) -> MATCH
[Sun 02:44:13] --- gate G2 PASSED
[Sun 02:48:20] STOPPED by me at G3 start: rank-4 operator projected ~125M nnz = ~30+ GB as Python dicts (cap 30 GB). Rebuilding the operator as streamed COO arrays; G1/G2 results stand.
