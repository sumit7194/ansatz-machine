# Reference claim for family (ii), the branched twist on Kerr's mass profile (2026-11-22)

**This is THE reference text.** Outreach and digests quote it verbatim or point to it. Any change is a new dated
version in this file, with the reason. Edits up to now were agreed with the Bridge.

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
