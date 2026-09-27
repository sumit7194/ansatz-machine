# Hidden symmetries of the scalar–Gauss–Bonnet black hole, ranks 2–8: a summary

*For readers outside the repo. All checks were run by AI sessions (Claude); no human has reproduced them.
Sources: RESULTS.md §128–§137 (sGB itself) and §141–§146 (the rank-8 deformation map).*

We tested exactly which of Kerr's Killing tensors survive in the slowly rotating scalar–Gauss–Bonnet (sGB)
black hole, a metric truncated at first order in the coupling ζ and second order in spin χ. We derived that
metric ourselves and checked it against Ayzenberg–Yunes (2014). The method works order by order: it solves for
corrections whose coefficients are bounded-degree polynomials in (r, cos θ) over a fixed power L⁶–L⁸ of the
metric's denominator. The linear system is solved exactly modulo two primes, and the reducible span is
subtracted. At ranks 2–6 only products of p_t, p_φ and H survive. Carter dies at rank 2, reproducing the
known result, and no irreducible Killing tensor appears at ranks 3, 4, 5 or 6 within this scope. At rank 8 we
studied a generic family of O(χ²) deformations of Kerr, not sGB itself. There, every survivor is a power of
one rational Carter-like integral, and the rank where it first appears measures that integral's pole order.
Checks:
- counts agree on both primes;
- the solver recovers Carter on Kerr;
- a spin-tower control must reproduce Kerr's Killing counts;
- gauge and random-deformation controls behave;
- predictions were sealed before the rank-8 runs.

Prior art: Vollmer (2016, arXiv:1602.08968) proved exact non-existence to valence 7 for Tomimatsu–Sato and 11
for Zipoy–Voorhees. For sGB, direct Killing-tensor searches we found stop at rank 2 (Owen, Yunes & Witek).
Rank ≥ 3 for sGB was **not found in our sweep**.

**What it is NOT**
- Not a statement about all ranks, or about symmetries non-analytic in the coupling. It is perturbative
  (analytic in ζ, rooted on Kerr), for sGB itself only up to rank 6, and relative to the stated ansatz.
- Not a statement about the physical black hole beyond the O(ζ)·O(χ²) truncation, or about real orbits
  (EMRIs).
- Not new symmetries at rank 8. Those directions belong to a generic deformation family, not to sGB, and
  every one is functionally dependent.

---
*Scope details, for a checking reader.* Ansätze and boxes per rank: rank 2–3 at L⁶, rank 4–5 at L⁷ (rank 4
box 27×24), rank 6 at L⁸ (box 30×28). Coverage was guarded by representability checks on the complete reducible
floor. Ranks 4 (Carter²) and 6 (Carter³) are the independent tests; ranks 3 and 5 follow largely from the
lower ones. Rank-8 map: first order in the deformation, O(χ²), polar ℓ = 2 and ℓ = 4 and axial ℓ = 3 slots,
radial profiles r⁻¹…r⁻⁶ (widening to r⁻⁸ at ranks 4 and 6 left the counts unchanged). There the pole order saturates at 2 for ℓ = 2.
