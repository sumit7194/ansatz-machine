# Rank-6 addendum: METHOD CHANGE to sampled dense rank (B1). The prediction is UNCHANGED (sealed 34d14b6)

Written 2026-10-10, before any rank-6 B1 run. The sparse exact solve was capped twice by memory (2026-10-05). B1
measures the same ansatz (TS δ=2, p = 4/5, rank 6, den L³, box 34×34, the four parity sectors) through a sampled dense
matrix (`scripts/_kt_sampled.py`): exact evaluations of {H, basis} mod p at ncols + 64 random points per sector, with
rank by rust/ktdense (u32, in place, ~3 GB).

- **Logic:** sampled nullity ≥ true nullity over GF(p) ≥ true nullity over Q. Sampled = floor therefore PROVES the null,
  and one prime suffices for a null. Any excess is INCONCLUSIVE (more points, then a second prime, then the exact
  route, then the Bridge).
- **Prediction (34d14b6, unchanged):** s0 16/16/0, s1 0/0/0, s2 0/0/0, s3 0/0/0.
- **Validation gate:** passed before launch; see data/sampled/validation.out. It covers Kerr r2/r3/r4 with Carter in
  the right sectors, TS r2/r3/r4 per sector, ZV r4, a planted duplicate column (nullity +1), FLINT == Rust, and a
  second prime.
- **Relation to the jet result:** the rank-6 prolongation bound (data/jet/targets.out) is ansatz-free and local. B1 is
  global but ansatz-bounded. They share no code; agreement is the two-implementation check.
