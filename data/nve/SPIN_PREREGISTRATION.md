# Spin coverage of the branched-twist family: spins 3/10, 4/5, 9/10 (pre-registration, 2026-11-21)

**Ask.** The Bridge GO after §162 (T38 point 1e: K*(a) had been shown empty only at a = 0.6). It continues the current
line. E = 4/5 throughout.

**Spins and why.**
- 3/10, 4/5 and 9/10 cover low, mid and high spin.
- 19/20 was scanned and **dropped before any F**: in the half-plane region a branch cut crosses the working region,
  and the series ratio is 0.70 (`spin_geo.out`). It is not attempted here.

**Code.** `scripts/_nve_spin_scan.py` (`NVE_SPIN=<a> … run`). It reuses the validated machinery:
- the Laurent c0 and the §159 walker for region A;
- the exact-radicand engine `_nve_lower_hp.py` (§162) for region B.

Spin now enters only through `NVE_SPIN`, whose default 3/5 reproduces every earlier run. The family's constants are
spin-independent: checked symbolically, our radicand equals Neon's (8/(5a⁶(u² + 1)⁶))·B(u², k) at spins 3/5, 3/10
and 19/20.

## Regions (edges fixed from the geometry scan, before any F)
| spin | region A (circle picture) | region B (half-plane picture) |
|---|---|---|
| 3/10 | [−1/2, 4] × [−1/2, 1/2]i, circle R0 = 1.1492 | [3.95, 30/7 − 1e−12] × [−1/4, 1/4]i; centre Z0 = 1.9540, base 1.6540; 220 terms; ratio ≤ 0.6 |
| 4/5 | [−1/2, 4] × [−1/2, 1/2]i, R0 = 1.3382 | same box; Z0 = 1.6181, base 1.3047; 220 terms; ratio ≤ 0.6 |
| 9/10 | [−1/2, 3.85] × [−1/2, 1/2]i, R0 = 1.2639 | [3.8, 30/7 − 1e−12] × [−0.15, 0.15]i; Z0 = 1.4926, base 1.1494; **300 terms; ratio ≤ 0.7** (0.7³⁰⁰ ≈ 1e−46) |

**Rules behind those numbers:**
- R0 is midway between the largest inner radius (ρ_c or an extra) and the smallest outer |z|. The margins are 0.75,
  0.29 and 0.26.
- Z0 is Re(centroid of r+, p± at the endpoint).
- The base is Re(r+ at the endpoint) − 0.3, but at least a + 0.08.

## What is counted, and the verdict
- **Region A** (loops M0 = circle R0, M1 = capsule lasso around [r+, p+], based at R0): count F, tr M0 − 2, tr M0,
  tr M1, and tr M1 − s for each finite-subgroup trace s.
  - Required: F has 2 zeros (Kerr's double zero at 0); tr M0, tr M1 and every tr M1 − s have none.
  - That gives irreducible, not imprimitive and not finite at every k ≠ 0 in A.
- **Region B** (M1 lasso and Γ disc, half-plane, as §162): count F_h, tr M1, tr Γ, tr M1Γ, and tr M1 − s.
  - Required: all zero-free, with tr Γ or tr M1Γ zero-free.
- **The endpoint k = 30/7** is classified directly (non-VA required), with samples at 30/7 − 10^{−13, −14, −15}.
- **Verdict per spin:** NO EXCEPTIONAL k IN (0, 30/7 − 1e−12] AND AT 30/7, if A and B both pass, the endpoint is
  non-VA, and every control and guard holds. Otherwise VOID, UNDETERMINED, or EXCEPTIONAL CANDIDATES, as in the code.

## Controls and guards per spin (any failure → VOID)
- **A-Kerr:** k = 0 gives |F| ≤ 1e−25 and |tr M0 − 2| ≤ 1e−25.
- **A-C1:** on the circle |k| = 0.3, F and tr M0 − 2 each have exactly 2 zeros.
- **A-C2 (counter must-detect):** the count of F·(k − (2 + 0.2i)) is count + 1, and of F/(k − (2 + 0.2i)) is
  count − 1.
- **A-geo** at every sample:
  - outer |z| ≥ R0 + 0.1;
  - extras and ρ_c ≤ R0 − 0.1;
  - lasso clearance ≥ 0.3 × dist(p−, segment) and ≥ 0.05 from the rest.
- **A-step:** every 6th sample at steps 0.35, 0.2 and 0.12 agrees to a relative 1e−15. **A-arg:** |Δarg| ≤ π/4 after
  refinement.
- **B-repro:** engine vs Laurent c0 and c0′ (Laurent at raised order) at k = A's right edge and k = 30/7, at 6 points,
  ≤ 1e−40.
- **B-repro-F:** F_h at k = A's right edge, engine vs Laurent, with the same loops: ≤ 1e−20.
- **B-MF-trunc (must fail):** a 12-term series differs by ≥ 1e−30 in c0 and by ≥ 1e−15 in F_h.
- **P1 Kerr (must be imprimitive):** the half-plane classifier says imprimitive (VA) at k = 0.
- **P2 (planted non-VA member) at k = A's right edge:** the circle pair (region A machinery) and the half-plane
  classifier both say non-VA.
- **B-geo** on an interior 11 × 15 grid and every boundary sample:
  - engine cut guard;
  - series ratio ≤ the spin's limit;
  - lasso and disc clearances as in §162;
  - containment in the working disc (radius = max reach + 0.05).
- **B-count:** G1 and G2 have (1, 2) zeros in the working disc at 5 grid points.
- **B-step:** every 4th sample at three steps agrees to 1e−15. **B-arg:** as in A. **B-C2:** as in A.

## Scope
- First-order lower-axis NVE; E = 4/5; three spins; 50-digit floating point, not interval.
- At each spin, the open sliver (30/7 − 1e−12, 30/7) is sampled, not counted.
- The physical family is 0 ≤ k ≤ 30/7 (T38 grading 1c). Region A's k < 0 part is a complex-metric region, included
  only to enclose k = 0.
- Peak memory < 1 GB. Run sequentially, 1 core, nice 10, roughly 1–2 h per spin.

**Run 1 (chain PID 29686): CRASH at spin 3/10, no verdict.**
- Region A had completed and passed every registered check: F 2 zeros; tr M0, tr M1 and every T1 − s with 0; step
  8e−23; C2 OK; Kerr 6e−50; C1 (2, 2). Region B's geometry and counts were also clean (span 0.35, (1, 2)).
- The crash was in B-repro: the Laurent builder's ABSOLUTE 1e−40 thresholds (trimming the vanishing leading radicand
  coefficient at k = 30/7, and detecting the leading series power) failed at spin 3/10, where the residual is larger
  than 1e−40. That left a spurious root, ρ ~ 3e24.
- Fixed with RELATIVE thresholds (1e−35 × scale) in `_nve_lower_kc.py` and `_nve_lower_hp.py`. Checked at spins 3/5,
  3/10, 4/5 and 9/10, k ∈ {0.1, 4, 30/7} (ρ_c correct). At spin 3/5 it reproduces the original `_nve_lower.c0_laurent`
  to ≤ 1e−50.
- No criterion changed. The chain was stopped by me and is rerun from the start as run 2 (log of run 1:
  `spin_run_3_10_crash1.out`).

## Spin 4/5 (run 2): registered verdict **EXCEPTIONAL CANDIDATES**, resolved POST HOC as no exception (labelled)
**Region A passes in full:**
- F has 2 zeros (the Kerr double zero); tr M0, tr M1 and every T1 − s have none.
- Step agreement 4.6e−22; C2 and C1 OK; Kerr |F| 1e−50.

**Region B:** F_h, T1 and all T1 − s have no zeros, but **count(TΓ) = count(T1Γ) = 1**, so the registered rule ("TΓ or
T1Γ zero-free") failed. Every control passed: B-repro 7e−52; repro-F 1.5e−48; MF-trunc fired; P2 non-VA by both
pictures; P1 Kerr imprimitive; steps agree to 3e−21; geometry and counts clean. The endpoint is non-VA.

**Post-hoc diagnosis (scripts `_nve_spin_locate.py` and `_nve_spin_kstar.py`; outputs `spin_locate_4_5.out` and
`spin_kstar_4_5.out`):**
- **The registered rule had a DESIGN FLAW: T1Γ is not independent.**
  - M1 encloses {r+, p+} and Γ encloses {r+, p+, p−}, so M1Γ⁻¹ encircles the single simple point p−. Its trace is
    identically 0.
  - So the Fricke identity gives **tr(M1Γ) = tr M1 · tr Γ identically**.
  - Check at the endpoint: (−1.49828 + 2.04609i)(−0.030099) = 0.045097 − 0.061585i, equal to T1Γ.
  - Hence count(T1Γ) = count(T1) + count(TΓ), so 0 + 1. Every zero of TΓ is a zero of T1Γ, and there the half-plane pair
    is genuinely imprimitive (two order-4 elements generate a dihedral group).
  - The rule could therefore never exclude imprimitivity where TΓ = 0. At spin 3/5 (§162) and 3/10, TΓ has no zeros,
    so those verdicts are unaffected.
- **The common zero:** k* = 4.008164511150082 (real). There T1Γ ≈ 2.5e−43, TΓ ≈ 5e−23 (the secant tolerance), and
  F_h = −10.17 − 5.69i ≠ 0.
  - My bisection for TΓ alone had a reversed-bracket bug and stopped after one step. The secant on T1Γ is the reliable
    locator.
- **At k* the GROUP is not imprimitive.** The independent circle pair (M0 = circle R0, M1 lasso; Laurent c0; ρ_c 0.906
  < R0 − 0.1) gives:
  - F = 15.59 + 8.72i; tr M0 = 1.459; tr M1 = −1.0541 + 2.6989i (non-real, at distance 2.70 from S).
  - So it is Zariski-dense at k* and at k* ± 0.002. The lasso trace equals the half-plane T1 at k*, as it must.
- **Conclusion (post hoc, labelled):** no exceptional k at spin 4/5, E = 4/5, in (0, 30/7 − 1e−12] ∪ {30/7}. The
  half-plane pair degenerates only at k*, where the full group is SL₂ by the circle pair.

**Lesson:** a classifier's trace triple must consist of INDEPENDENT functions on the region. Check the Fricke
relations (here M1Γ⁻¹ is a single-point loop) before registering. Spin 9/10 runs under the same rule. If TΓ has zeros
there, they are resolved the same way, with an independent pair at each zero.
