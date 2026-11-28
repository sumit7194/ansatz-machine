# Why the region-B certificate at 3/5 would matter, and what it would not do (re-gate (C), for the value gate)
**Office ansatz-machine, 2026-11-28. A note for the spend decision; it certifies nothing.**

## What the full region-B certificate at spin 3/5 would establish
- **The certified fact.** For EVERY real k in [4.0, 30/7 − δ0], with δ0 = 7.4e−15 at 3/5:
  - F ≠ 0;
  - tr M0 ≠ 0;
  - tr M1 is not in [−2, 2].
  These hold for the NVE's monodromy along the lower axis.
- **What follows, through the applicability chain.** The identity component of the NVE's differential Galois group is non-abelian, so by Morales–Ramis there is no additional meromorphic first integral at that k. That is the same inference the certified stretches of route (i) already make.
- **Combined coverage at 3/5.**

  | stretch | how it is covered |
  |---|---|
  | (0, ε_a] | Statement A |
  | [1/640, 3] | route (i), done |
  | **[4.0, 30/7 − δ0]** | **this certificate** |
  | [30/7 − δ0, 30/7] | the interval-certified end sliver |

  Rigorous coverage of (0, 30/7] would rise from about 70% to about 77% at that one spin. The remaining 23% is region A.
- **The hard end.** It would be the first rigorous statement in the top part of the range, near 30/7. That is where the floating-point counts are least comfortable: the outer branch point approaches, and the 50-digit node precision is tested against small |F|.

## What it would NOT do
- **It would not make the claim a theorem, even at 3/5.** Region A, [3, 4], has no route (CAPD was refused on the circle, the C2-TM probe failed, and C2-L does not apply there). So "no gap at 3/5" still could not be said. The claim's one-sentence status, "a numerical result, not a theorem", would be unchanged.
- **Other spins are not covered.** 3/10, 4/5 and 9/10 would each need their own production, roughly 4x the cost for all four, and the near-30/7 question is open at each.
- **It inherits the applicability chain's grade:** Lemma K, Proposition 2's majorant proof (author-checked, not independently checked) and the conventions. It is not stronger than that chain.
- **It inherits the claim's scope:** not black holes; off-axis regularity unchecked; null geodesics untested. It says nothing about EMRI orbits or any physical object.
- **It would not change any published number.** It moves part of the range from the numerical grade to the certified grade.

## Who would care
- **Differential-Galois / integrability specialists.** Computer-assisted Morales–Ramis non-integrability over a continuous parameter range, with every k covered, is uncommon. Most such results are at isolated parameter values or rest on numerical monodromy. This is the audience for whom the grade change is the result.
- **Referees of the preprint.** The top of the range is where a hostile reader would press, because it is numerical exactly where the problem is hardest. A certified top answers that, but only partly while [3, 4] is still open.
- **Bumpy-black-hole / EMRI modellers.** Only indirectly: the physics conclusion ("only Kerr" along this axis, numerically) is already stated. A certificate changes its grade, not its content, so for them the value is small.

## What a partial cover gives
- **Each certified segment is self-contained:** every real k in that segment, certified. A partial production is reportable as "certified over [x, y] at 3/5" with the uncovered pieces left at the numerical grade, exactly like route (i)'s stated reach.
- **The story gets patchier,** with more stretches and more boundaries to state. Its value per core-hour is highest for segments that close a gap: those adjacent to the sliver, or the whole mid-region if large segments certify.

## The measured cost, as the two probes revised it (`C2_M_PROBES_RESULT.md`)
- **Pend (near 30/7, the dyadic chain) FAILED.** Every cell was refused at the start.
  - The guard was H1: d2kc0 at the base point. The cause is base2's ball squaring of s near 0, an evaluator artefact, not a property of F.

### How much of region B is reachable WITHOUT the base2 fix (a diagnostic, design-grade; certifies nothing)
- **The mechanism.** base2 (in `_nve_route1_segment_v7B.py`) must certify Re P > 0 on every s-ball. P = (90 − 21k) − (60 − 18k) a²s² + (10 − k) a⁴s⁴.
  - For real k < 30/7, every term is genuinely ≥ 0 and P ≥ 90 − 21k > 0.
  - On the first s-ball [0, w lim] (w = 1/96, lim = 1/bB), midpoint-radius squaring gives s·s a lower bound of −2(w lim/2)². That makes the middle term's lower bound negative, about −17.1 a² lim² w²/2 ≈ −1.5e−4.
  - The guard therefore fails once 21 d falls below that, i.e. for d = 30/7 − k below about **7.1e−6** (predicted).
- **Measured by bisection on base2 itself (Pend's floats entry): d* = 7.08e−6.** The point-k and segment-ball tests agree: pass at d = 1e−5, fail at 5e−6 and below. The prediction and the measurement agree, so the mechanism is the one named.
- **For the dyadic chain** [30/7 − 2d, 30/7 − d], with d = 1e−3 / 2^j and the segment's ellipse reaching to about 30/7 − 0.97 d:
  - H1 passes for j = 0..7, that is d down to 7.8e−6: **8 of the 37 dyadic segments.** P3 is j = 0 and already certified.
  - It refuses for j = 8..36: **29 segments.**
- **By length, without the fix:**
  - region B is reachable over [4.0, 30/7 − 7.8e−6];
  - the unreachable part is (30/7 − 7.8e−6, 30/7 − δ0), about 7.8e−6 long;
  - that is about **0.003% of region B (99.997% reachable)**, assuming nothing else refuses.
- **The other near-endpoint caveats are untested below d = 1e−3** (P3 is the only near-end certificate): node precision against |F|, and the outer branch point (V7 addendum 8). So the 8 is an upper bound from H1 alone, not a prediction that those segments certify.
- **By segment count,** production as costed (320 segments) cannot reach δ0: 29 segments, about 9%, would refuse at H1. The interval-certified end sliver covers only [30/7 − δ0, 30/7]. Without the fix, the gap between 30/7 − 7.8e−6 and the sliver stays numerical.

### The fix (a NEW mechanism; NOT run, for a ruling)
- **(1) Enclose s² from the s-ball's endpoints.** On s ≥ 0, s ↦ s² is monotone, so s² ∈ [lo², hi²] exactly, with no spurious negative part. Then every term of Re P is certified ≥ 0 and Re P ≥ 90 − 21 Re k > 0 for every K left of 30/7, down to δ0.
- **(2) Subdivide the first s-balls geometrically near s = 0.** The integrand d²√P/dk² ∝ P^(−3/2) peaks at s = 0 like (90 − 21k)^(−3/2). One rectangle of width 1/96 over-estimates that peak's integral by a factor of about w (α/c2)^(1/2): about 4e3 at d = 1e−12. That is still a valid bound, but adaptive subdivision keeps E tight.
- **Scope.** base2 is part of the code that certified P3, so this changes a certified component.
  - It needs a non-author read.
  - It needs a control that P3 still certifies with the changed code, and a must-fail control (the old squaring must refuse at d = 5e−6).
  - The read should check d2kc0_B's other s-ball loops for the same pattern.
- **Cost of the fix itself:** small, hours. Running the 29 extra segments is about 64 core-h at P3's measured rate, if the other caveats hold.
- **Pmid (mid-region, half 1/200) CERTIFIED:** every real k in [829/200, 831/200].
  - All 25 R/5 cells were accepted with no refinement, and every control behaved as at P3.
  - Margins: |F| ≥ 4.02, |tr M0| ≥ 0.0174, |Im tr M1| ≥ 0.9995.
  - It took about 1.1 h wall on 2 cores, the same as P3 for a segment ten times longer.
  - This is one k_c: half 1/200 elsewhere in the uniform part is still an extrapolation.
- **So the spend question, stated now:**
  - The uniform mid-region costs about 64 core-h at half 1/200 (Pmid certified at one k_c), against about 620 core-h at P3's size.
  - The dyadic end:
    - 7 more segments (j = 1..7, about 15 core-h) are reachable without the fix, if the other near-end caveats hold;
    - the last 29 need the base2 fix (a ruling) plus about 64 core-h.
  - Neither changes the claim's status while [3, 4] has no route.

## My recommendation for the value gate
The certificate's value is a grade change at one spin over part of the range, with [3, 4] still numerical.
- Pmid certified, so the mid-region at half 1/200 is cheap enough (about 80 core-h with the 7 reachable dyadic segments: about a day on 4 cores) to be worth it as a demonstration, reported as a stated reach.
- The dyadic end and the other spins should wait until there is a reason to expect region A can be closed. Without that, no amount of region-B work reaches "no gap".
