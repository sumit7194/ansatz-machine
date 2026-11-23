# Reference claim for family (ii), the branched twist on Kerr's mass profile

**This is THE reference text.** Outreach and digests quote it verbatim or point to it. Any change is a new dated
version in this file, with the reason. Edits up to now were agreed with the Bridge.

# VERSION 2 (2026-11-22): CURRENT. Amended 2026-11-24 (v2.1), status wording only
**v2.1 (2026-11-24):** the Proposition 2 status line below had fallen behind MRS §4b, so the repo contradicted itself.
It said "citations still being checked", while §4b said "CHECKED". It now says what is true: our own majorant proof,
checked by its author and a numerical control, not yet independently checked. Found by the Bridge's layer-4 reader.
The claim and every number are unchanged.

**Why v2 exists:** Neon T51, a hostile referee read of v1. It is graded in `data/nve/T51_GRADING.md`. v2 changes how the
claim is presented, not what it says:
- the status comes first;
- the conventions are stated;
- the scope adds "not black holes; off-axis regularity unchecked; null geodesics untested";
- a_c moves out of the main sentence.
None of the numbers change.

## Status (read this first)
- **A numerical result, not a theorem.** Over (0, 30/7 − 10⁻¹²] it rests on 50-digit floating-point argument-principle
  counts.
- **Interval arithmetic certifies only the end sliver:** the last ~10⁻¹⁰ of the range at spins 0.6, 0.8 and 0.9, and
  only the last 7.4 × 10⁻¹⁵ at spin 0.3.
- **Three degenerate cases were resolved post hoc, in floating point.**
- **One link in the applicability argument (Proposition 2, the off-axis metric near the orbit) rests on a majorant proof written here (MRS_SECTION.md §4b), checked by its author and by a numerical control, NOT yet independently checked.**
  It is stated on compact sets where the axis data are holomorphic and f0 ≠ 0. On the lower axis that means f0⁻ ≠ 0
  and e₋ has no poles (f0² + c0² ≠ 0).

## The claim (one sentence)
Numerically (50-digit floating point, interval-certified only at the top of the range), for the stationary axisymmetric
vacuum fields whose upper-axis Ernst data have Kerr's real part and the branched twist
(c0″)² = 8B(u², k)/(5a⁶(u² + 1)⁶), with u = z/a and B(w, k) = (90 − 21k)w² − (60 − 18k)w + (10 − k), and whose data
are real on both outer axis segments exactly for 0 ≤ k ≤ 30/7 (k = 0 being Kerr), the first-order normal
variational equation along the L_z = 0 timelike geodesic on the lower outer axis at energy E = 0.8 has a
Zariski-dense (SL₂) monodromy group for every real k ∈ (0, 30/7] at each tested spin a ∈ {0.3, 0.6, 0.8, 0.9}; by
Morales–Ramis–Simó the geodesic flow of each such field then admits no complete set of first integrals in
involution meromorphic near that complexified orbit.

## Conventions
- **Units and particle.** M = 1. μ = 1 (timelike; E is the energy per unit mass).
- **The coordinate z is the Weyl coordinate shifted by M** (z = z_Weyl + M), so that Kerr's upper-axis data are
  e₊ = (z − ia − 2)/(z − ia), with real part f0 = 1 − 2z/(z² + a²).
  - The rod endpoints are z = 1 ± √(1 − a²).
  - The lower outer axis is z < 1 − √(1 − a²).
- **Normalisation of c0:** c0, c0′ → 0 as z → +∞ (asymptotically flat, no NUT charge). The branch of √B is analytic off
  a tree through u = 1 and positive at u → +∞. At k = 0 this is Kerr's c0 = −2a/(z² + a²).
- **Lower-axis data:** e₋ = 1/e₊. This is a general property of asymptotically flat data, derived in
  `MRS_SECTION.md` §5a, and it does NOT need equatorial reflection symmetry.
- **"Real on both outer axis segments"** is an axis statement only (`MRS_SECTION.md` §5c). For k < 0, c0″ is imaginary
  on part of the lower outer axis at every spin.

## Evidence, with its grade
| piece | method | grade |
|---|---|---|
| (0, 30/7 − 10⁻¹²] at each spin | argument-principle counts over complex k-rectangles | 50-digit floating point |
| no zeros split off k = 0 | F = O(k²) structurally (`MRS_SECTION.md` §5d), plus the counts | exact, given the counts |
| k = 30/7 | direct classification | floating point; interval-certified at 0.3 (S4) and at the other spins (S3/T48b) |
| end sliver (30/7 − δ0, 30/7] | Zariski-density certificate | **interval arithmetic**: δ0 = 1.37e−11, 2.4e−10, 3.6e−10, 7.4e−15 at spins 0.6, 0.8, 0.9, 0.3 |
| spin 0.3, (30/7 − 10⁻¹², 30/7 − 7.4e−15] | samples, all non-VA | floating point only |
| spin 0.8, k ≈ 4.0082 (test pair degenerates) | independent pair of monodromies | floating point, post hoc |
| spin 0.9, one extra zero of F | located; non-real, so off the physical range | floating point, post hoc |

## Scope: what is NOT claimed
- **Not black holes.** By uniqueness (Chruściel–Costa), no k ≠ 0 member is a regular vacuum black hole.
- **Nothing off the axis is checked.** Horizons, the rod, naked singularities and CTCs are all unexamined.
- **Spins and energies.**
  - Only the four spins listed. Spins below 0.3 are untested, and the obstruction weakens roughly like a⁷–a⁸ toward
    low spin.
  - Energies other than 0.8 are tested only at spin 0.6, on the end sliver (E = 1.5, interval, δ0 = 1.9e−9).
- **Null geodesics are not tested.**
- **The class of integrals excluded.** Integrals that are real-analytic on the physical exterior but do not continue
  meromorphically near the complexified orbit are not excluded.
- **Not a statement about all spins.** At the intermediate spin a_c ≈ 0.858446, the endpoint test pair degenerates.
  It was settled by an independent pair in two implementations, but it is not a tested spin.

## Related result: rational axis data (SEPARATE from the family (ii) claim; added 2026-11-22 at the Bridge's request)
**Statement.** Take a stationary axisymmetric vacuum field with a regular outer axis segment whose axis function
f0 = −g_tt|axis is RATIONAL of degree d ≥ 3. Then at generic energy E (E² ≠ 0, E²/μ² not a critical value of f0 and
≠ f0(∞)), the first-order normal variational equation along the L_z = 0 timelike geodesic on that axis has
differential Galois group SL(2, C). So the geodesic flow has no complete set of first integrals in involution
meromorphic near that complexified orbit.
- **Only deg f0 ≤ 2 can pass this first-order test.** We do NOT claim that deg f0 ≤ 2 fields are integrable:
  sufficiency is graded only ~80–85%.
- **This covers equatorially symmetric non-Kerr members.**
  - Zipoy–Voorhees δ = 3 (deg 3) was tested numerically in §158.
  - Tomimatsu–Sato δ = 2 has deg f0 = 4; that is an algebra check only (`ts2_axis_deg.out`), and TS's
    non-integrability itself is a sibling result, relayed.
  - Zipoy–Voorhees δ = 2 is deg 2 and NOT covered here (see §124/§126 and Maciejewski–Przybylska–Stachowiak 2013).
**Grade.**
- **Checked by hand:** Kovacic cases 1–3 against Kovacic's ORIGINAL conditions (J. Symb. Comput. 2 (1986),
  pp. 11–12, 18, 22–23); case 3 also excluded by an independent monodromy argument; the count
  s + 2h ≥ d + 2 ≥ 5.
- **Consistent with 9 numerical runs** (§158).
- **Sources:** `NOTES2_KOVACIC_CHECK.md`, RESULTS §158 and its addendum, `NVE_PREREGISTRATION.md`.
**Caveats.**
- Generic E only: an explicit degree-3 f0 is solvable at one special E, where three zeros merge (M3, §158).
- From the axis normal form to Morales–Ramis, it relies on Lemma 1–2 (verified by the Bridge, V21; relayed) and on
  the covering/gauge step (Lemma C, `MRS_SECTION.md` §1).
- **Markakis 2014 context:** his conjecture concerns equatorially symmetric fields. This result speaks to it only
  within rational axis data, at first order, at generic E, and only in the "non-Kerr ⇒ obstructed" direction for
  d ≥ 3.

## Prior art closest to these claims (read at source; see `MRS_SECTION.md` §6)
- **Ramond 2026 (arXiv:2607.27129).** Undeformed Kerr, with a tidally deformed orbiting body at O(ε). It proves that
  no first-order deformation of Carter's constant exists, up to rank 4. It names Morales–Ramis as future work.
  Complementary: a different system and a different class of integrals.
- **Destounis–Kokkotas 2023 (arXiv:2305.18522).** Hartle–Thorne at O(Ω²). Numerical chaos only. Complementary.
- **Maciejewski–Przybylska–Stachowiak 2013.** Static Zipoy–Voorhees δ = 2, by Morales–Ramis. The closest method.
- **Markakis 2014.** Newtonian, equatorially symmetric. Family (ii) lies outside its class.
- **Kruglikov–Matveev 2016.** Generic metrics; context only.

## Plain version
For one bound orbit up and down the lower axis, our computation finds no twist value in the physical range that makes
these Kerr-mass, twisted spacetimes integrable in the meromorphic sense. This holds at four spins and one energy. It is
a careful numerical result: only the very end of the range is proved in interval arithmetic. These are not black
holes, and we have not looked off the axis.

## Sources for each number
(As in v1, below. Also: `T51_GRADING.md`, `MRS_SECTION.md` §5–§5e, `t51_axis_check.out`.)

---

# VERSION 1 (eed501f, 2026-11-22): SUPERSEDED by v2 above (same content, presentation fixed)
## The claim (one sentence)
For Kerr's mass profile with the branched twist (c0″)² = 8B(u², k)/(5a⁶(u² + 1)⁶), with u = z/a and
B(w, k) = (90 − 21k)w² − (60 − 18k)w + (10 − k), whose members regular on both outer axes are exactly 0 ≤ k ≤ 30/7
(k = 0 being Kerr), the first-order normal variational equation along the L_z = 0 timelike geodesic on the lower outer
axis at energy E = 0.8 has a Zariski-dense (SL₂) monodromy group, so that by Morales–Ramis the geodesic flow admits no
complete set of first integrals in involution meromorphic near that complexified orbit, for every real
k ∈ (0, 30/7] at each tested spin a ∈ {0.3, 0.6, 0.8, 0.9}; this rests on 50-digit floating-point argument-principle
counts over complex k-rectangles covering (0, 30/7 − 10⁻¹²] together with a direct classification at k = 30/7, on an
interval-arithmetic certificate of the end sliver (30/7 − δ0, 30/7] with δ0 = 1.37 × 10⁻¹¹, 2.4 × 10⁻¹⁰ and
3.6 × 10⁻¹⁰ at spins 0.6, 0.8 and 0.9 but only δ0 = 7.4 × 10⁻¹⁵ at spin 0.3 (the rest of that sliver resting on
floating point), and on three floating-point resolutions of degenerate cases: at spin 0.8 the primary test pair
degenerates at k ≈ 4.0082, which is settled post hoc by an independent pair of monodromies; at spin 0.9 one extra
zero of the irreducibility function, located post hoc, is non-real and so outside the physical parameter range; and
at the intermediate spin a_c ≈ 0.858446 (not one of the tested spins) the endpoint test pair degenerates, which is
located and settled by an independent pair in two independent implementations of the same loop invariants; the
obstruction weakens roughly like a⁷–a⁸ toward low spin, spins below 0.3 are not tested, energies other than 0.8 are
tested only at spin 0.6 on the end sliver (E = 1.5, interval certificate, δ0 = 1.9 × 10⁻⁹), and integrals that are
real-analytic on the physical exterior but do not continue meromorphically near the complexified orbit are not
excluded.

## Plain version
At energy 0.8 and the four spins tested, no twist value in the physical range makes this lower-axis orbit integrable
(in the meromorphic, Liouville sense). The end of the range is proved in interval arithmetic except at the lowest
spin. The effect gets much weaker as the spin drops.

## Sources for each number
| item | source |
|---|---|
| family, physical range 0 ≤ k ≤ 30/7 | `data/nve/T38_GRADING.md` (1c, 1d); T11 / T14 relayed |
| counts on (0, 4.05] at spin 0.6 | `data/nve/GAPB_PREREGISTRATION.md`, RESULTS §159 |
| counts on [3.95, 30/7 − 1e−12] at spin 0.6 | `data/nve/WINDOW_PREREGISTRATION.md`, RESULTS §162 |
| endpoint at spin 0.6 | `data/nve/K307_PREREGISTRATION.md`, RESULTS §161 (under post-unblinding amendment A1) |
| counts and endpoint at spins 0.3, 0.8, 0.9 | `data/nve/SPIN_PREREGISTRATION.md`, RESULTS §163 |
| δ0 = 1.37e−11 (spin 0.6, E 0.8) and 1.90e−9 (E 1.5) | `data/nve/t48b_fixed/out_fixed.txt` (Neon T48b, code read and patched here) |
| δ0 at spins 0.8 and 0.9 (S3) and 0.3 (S4) | `data/nve/t48b_spin/`, `data/nve/t48b_s4/` |
| k* (spin 0.8) | `spin_locate_4_5.out`, `spin_kstar_4_5.out` (post hoc) |
| extra zero (spin 0.9) | `spin_locateA_9_10.out` (post hoc) |
| a_c and its circle pair | `ac_secant.out`, `ac_circle.out`; Neon T50 (blind) |
| a⁷–a⁸ scaling | `endpoint_scaling.out`; Neon T50 (blind), agreeing to 15 digits |

## Still to do before any talk test (from the Bridge)
- The MRS applicability section: the T49 draft plus our check (`data/nve/T48_T49_CHECK.md`).
- Citations checked at source: Morales-Ruiz–Ramis–Simó 2007; Casale 2009; Beig–Simon.
