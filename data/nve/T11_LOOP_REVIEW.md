# Second reading of a relayed all-spin loop construction (Neon T11 + T14, via the Bridge), 2026-11-21

A reading task for the Bridge. Sources: the Bridge's summaries `neon_work/onlykerr/T11_GENERALIZE_SUMMARY.md` and
`T14_UA_SUMMARY.md`. Both are relayed and unverified here. The full proof text was not available; only the summaries
were read. One small numerical check supports the gap stated in (3): `scripts/_nve_t11_check.py`, with output in
`data/nve/t11_check.out`.

Notation:
- f0 = n/g, with n = z² − 2z + a² and g = z² + a² (M = 1).
- G2 = n² + c0²g². Its outer zeros are the poles of P, called p±.
- G1 = E²G2 − ng. Its outer zeros are the zeros of P, called r±.

## Facts used, derived here at k = 0
- G2 = (z² + a²)((z − 2)² + a²), so p± = 2 ± ia.
- G1 = (z² + a²)·Q(z), with Q = (E² − 1)z² − (4E² − 2)z + E²(4 + a²) − a².
- r± = [(2E² − 1) ± √(1 − a²(E² − 1)²)]/(E² − 1). The discriminant is 4[1 − a²(E² − 1)²].
- As a result:
  - For 1 < E < √(1 + 1/a), r± are real, and both are ≥ 2.
  - At E = √(1 + 1/a) they collide at 2 + a.
  - Above that they are complex, with Re = 2 + 1/(E² − 1) and |r±|² = 4 + a² + 4/(E² − 1).
  - So **E > √(1 + 1/a) is only the threshold at which r± become complex.** The half-plane containment Re r± > a
    already holds for every E > 1.
- For E < 1, r− is real and negative. At spin 0.6 and E = 0.8, r− ≈ −3.49.
  - r− → −∞ as E → 1⁻.
  - r− → the inner horizon 1 − √(1 − a²) as E → 0.
  - It crosses the circle |z| = R where E² = (R² + 2R + a²)/((R + 2)² + a²). At spin 0.6 that is E ≈ 0.625 for
    R = √(1 + a²), and E ≈ 0.649 for R = 1.35.
- ∞ is an ordinary point of the NVE when E ≠ 1, because q = O(z⁻⁴) there.
- As E → ∞, r± → p± at distance ≈ 1/(E² − 1). Each zero–pole pair annihilates, so q → 0 away from p±.

## Verdict on the four claims
1. **γ̃0 ≃ the inner loop: correct for E > 1, with condition (3) below.**
   - On the sphere, with ∞ ordinary, a curve separating the inner set from {p±, r±} is the inner loop reversed. A
     trace in SL₂ does not see orientation.
   - The threshold E > √(1 + 1/a) is unnecessary (see the facts above).
   - **It fails for E < 1.** r− lies in Re z < 0, outside the inner circle. A loop in Re z > a around {p±, r+} then
     differs from the inner loop by the loop around r−.
2. **γ1 around {p+, p−}, avoiding r±: fine at every finite E > 1.**
   - A dumbbell shape works: it crosses the axis left of 2, with r± ≥ 2 when real and close to p± when complex.
   - **Caveat:** γ1 is pinched as E → ∞, since |r± − p±| ~ 1/E². Its matrices are therefore not uniform at large E.
     Any large-E asymptotic step should use γ̃0, whose monodromy → I analytically in 1/E², and not γ1.
3. **Analyticity "as long as p±(k) stay in Re z > a": incomplete as stated.**
   - The isotopy also needs r±(k, E), the zeros of G1, to stay in the half-plane. T14's Re H > 0 certifies G2 ≠ 0 on
     Re z = 1 only.
   - **Measured** (spin 0.6, c0 from T14's own ray formula, count over Re z > 1 closed by |z − 1| = 40):
     - k ∈ {−50, −22.59, −5, 0, 0.1, 2, 4, 4.2} × E ∈ {1.05, 1.3, 2, 3, 10};
     - see `t11_check.out` for the counts.
     - The "minrel" line margins printed there do not change with k. The far ends of the line, where c0 is
       negligible, set them, so they are not informative about how close a zero comes to the line.
   - **Side result:** T14's ray formula matches our independent Laurent c0 to all printed digits, at k ∈ {0, 1/10, 4,
     −5}, three points each.
   - **On collisions** (r+ = r−, or r = p):
     - They do not break analyticity of the inner trace, since both points lie on the same side of the separation.
     - They can relabel a transported γ1. It is still a group element, so the irreducibility conclusion survives;
       only the geometric description does not.
4. **Large E → generic E (gap C): closable by an argument, for E > E_min(a), including bound orbits.**
   - tr(g_in) − 2 = c(E)k² + O(k³), and c(E) uses only the k = 0 geometry, which is in closed form.
   - The inner trace depends only on the separation class. So c(E) is analytic in E wherever no k = 0 singular point
     crosses the inner circle. The events along the way:
     - **r± colliding:** both are on the same side, so the collision is harmless.
     - **r_large passing through ∞ at E = 1:** continuing around E² = 1 in complex E pushes one point around ∞. That
       loop encloses everything else, so it is trivial on the sphere, and there is no monodromy.
     - **r− entering the inner circle:** this happens only at E < E_min (≈ 0.625 at spin 0.6).
   - Hence c(E) is analytic on a connected domain containing (E_min, ∞). If the leading large-E coefficient (∝ I₊(a)?)
     is nonzero, then c(E) ≢ 0, and c(E) ≠ 0 except on a discrete set of E.
   - **Consistency:**
     - our measured c(0.7), c(0.8), c(0.9) are all ≠ 0 (§159);
     - c(E) → 0 as E → ∞, and our |c| decreases with E. So the large-E statement must concern the leading 1/E²
       coefficient of c, not c itself. Whether I₊ is that coefficient needs checking against the full text.
   - **Scope that stays open:** for E < 1 at large |k|, the k-continuation needs a separating curve that passes between
     the inner set and r− on the left. Re z = 1 does not provide one, and T14's circle certificate fails at
     k ≈ −22.59. Below E_min, nothing is covered.

## Also noted: the group step
F(k) = tr[M1, M0] − 2 ≠ 0 gives irreducibility, not non-VA, because irreducible imprimitive (dihedral) groups are VA.
The proof also needs:
- two of tr M0, tr M1, tr M1M0 to be ≢ 0, which rules out imprimitivity;
- an element of infinite order.

All of these are analytic in k, so they hold generically. They should be stated. §159's two-loop certificate does this
numerically.

## Addendum (2026-11-21): the same zero count at spins 0.3 and 0.9
`scripts/_nve_t11_check.py 3/10` and `9/10` give counts identical to spin 0.6 at all 8 × 6 (k, E): 2 zeros and 2 poles of
P in Re z > 1 for E > 1, and 1 zero at E = 0.8. Outputs: `t11_check_spin3_10.out` and `t11_check_spin9_10.out`.
Note that Re z > 1 is narrower than Re z > a when spin < 1. At spin 0.9 the strip 0.9 < Re z < 1 is not covered by this
count.

## Correction (2026-11-21, from grading Neon T38; `T38_GRADING.md`)
- **"For k < 0 the negative-B interval lies inside the horizon": wrong.** It lies in |z| < a. On the lower side that
  includes the physical lower outer axis z < 1 − √(1 − a²), where c0 then becomes complex. With regularity on both
  outer axes, k < 0 is not a physical member of the family.
- **"k = 30/7 gives a NUT charge" (accepted from the relayed summary): wrong.** At k = 30/7 the angular-momentum term
  vanishes (it is ∝ √(90 − 21k)) and c0 ~ z⁻³. That is a real, asymptotically flat J = 0 member, and it is not covered.
