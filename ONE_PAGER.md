# Twisted Kerr-mass vacuum fields: an axis orbit that is not integrable

**Question.** Kerr's geodesics are integrable because of a hidden constant, the Carter constant. How rigid is that?
If a stationary axisymmetric vacuum field keeps exactly Kerr's mass profile along its symmetry axis and changes only
its rotation (twist) profile, does the integrability survive?

**Setting.**
- Ernst axis data e₊(z) = f0(z) + i c0(z), with Kerr's f0 = 1 − 2z/(z² + a²) (M = 1; z is the Weyl coordinate
  shifted by M).
- A branched twist (c0″)² = 8B(u², k)/(5a⁶(u² + 1)⁶), with u = z/a and
  B(w, k) = (90 − 21k)w² − (60 − 18k)w + (10 − k).
- k = 0 is Kerr. The data are real on both outer axis segments exactly for 0 ≤ k ≤ 30/7. At k = 30/7 the angular
  momentum vanishes while the mass quadrupole stays Kerr's.
- The members are exact vacuum fields near the axis. They are not black holes (by uniqueness), and nothing off the
  axis is checked.

**Method.** Morales–Ramis(–Simó) theory.
- Take the L_z = 0 timelike geodesic on the lower outer axis, at energy E = 0.8.
- Its first-order normal variational equation is a linear ODE in the axis coordinate.
- If its monodromy group is Zariski-dense in SL(2, C), the geodesic flow has no complete set of first integrals in
  involution meromorphic near that complexified orbit.
- The upper axis is blind to the twist at this order. The lower axis sees it through e₋ = 1/e₊, a general property
  of asymptotically flat data (Meinel–Neugebauer 1995, Eq. 35).

**Result (numerical; interval-certified only at the top of the range).**
- For every real k in (0, 30/7], at each tested spin a ∈ {0.3, 0.6, 0.8, 0.9}, the monodromy group is Zariski-dense.
- How this was established:
  - argument-principle zero counts of trace invariants over complex k-rectangles, at 50 digits;
  - k = 0 handled structurally (the test function vanishes to exactly second order there);
  - an interval-arithmetic certificate on the last ~10⁻¹⁰ of the range (only 7.4 × 10⁻¹⁵ at spin 0.3);
  - three degenerate cases resolved post hoc (two by an independent pair of loops, one by locating a non-real zero).
- The obstruction weakens roughly like a⁷–a⁸ toward low spin.
- **Near Kerr, rigorous relative to the applicability chain** (claim v3).
  - The k² coefficient of the trace test has a closed form from Kerr's solutions.
  - Its nonvanishing is interval-certified at each tested spin. So the group is Zariski-dense for all small enough
    k > 0 (Statement A).
  - The interval is unquantified. The coefficient vanishes at the untested spin ≈ 0.908.

**Related result (rational axis data).**
- Any such field whose axis function f0 is rational of degree ≥ 3 has Galois group SL(2, C) for the axis
  variational equation, at generic energy.
- So only degree ≤ 2 can pass this first-order test. Degree ≤ 2 is NOT claimed integrable.
- This was checked by hand against Kovacic's original conditions.
- It covers equatorially symmetric non-Kerr fields such as Zipoy–Voorhees δ = 3 and Tomimatsu–Sato δ = 2 (deg 4).

**What is not claimed.**
- No other energies, except one interval check at E = 1.5 for spin 0.6.
- No spins below 0.3.
- No null geodesics.
- No integrals that are only real-analytic on the physical exterior.
- The family is not equatorially symmetric, so it lies outside Markakis's (2014) Newtonian-motivated conjecture.

**Closest prior work.**
- Maciejewski–Przybylska–Stachowiak 2013 (static Zipoy–Voorhees, Morales–Ramis).
- Ramond 2026 (tidal deformation of Carter's constant, at first order; it names Morales–Ramis as open).
- Destounis–Kokkotas 2023 (Hartle–Thorne; numerical).

**Checks.**
- Pre-registered runs, with failed runs kept.
- Two hostile referee rounds, answered point by point.
- Every link of the applicability argument is checked or cited at source, including our own convergence proof (not yet independently checked) for
  the off-axis metric.

**How it was made.** Developed with substantial assistance from Anthropic's Claude, which wrote and ran most of the
code, checked the literature and drafted the documents. The hostile referee reads were by Google's Gemini. The author chose the questions, directed and reviewed the
work, and takes responsibility for it. No professional review yet; corrections are welcome.

Sumit Pal (independent researcher) · code, data and full write-up: `ONLY_KERR.md` in github.com/sumit7194/ansatz-machine
