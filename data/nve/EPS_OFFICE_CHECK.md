# Office check of Fable's Part A, the explicit ε for Statement A (branch `fable/2026-11-25-eps`, 75957fd), 2026-11-26

**Checker:** ansatz-machine (office), a non-author.
**Ask:** the Bridge, items (1)–(5), plus Fable's own handover list.
**Verdict: VERIFIED, with one small rigour correction.**
- The certified radii must be quoted **rounded down**: ε_a ≥ **2.79e−3, 1.92e−3, 8.39e−4 and 1.06e−4** at spins 3/10,
  3/5, 4/5 and 9/10. See (6).
- The claim and ONLY_KERR are unchanged: integration waits for the Bridge and Sumit.

## (1) Reproduction on a clean checkout: bit for bit
- Detached worktree at 75957fd, the same `.venv`, the author's driver `data/nve/eps/run_all.py`, 10 runs.
- **All 10 JSON outputs are byte-identical** to the committed ones, and the logs are identical apart from wall time
  and peak (`eps_office_rerun.out`).
- Results: r = 2.799958e−3, 1.925559e−3, 8.398970e−4 and 1.063035e−4 (registered lassos); 227/250 gives 5.422444e−8;
  REFUSE gives "NO r"; the wide lassos give 2.799958e−3, 2.796178e−3, 1.443615e−3 and 1.472038e−4.

## (2) The algebra, by a non-author
- **Exact sympy checks:** G2 = G2_K(1 + σ) with σ = (−4aδ + D₊δ²)/D; P = P_K(1 + γs) with s = σ/(1 + σ) and γ = Δ/N;
  the linear part of γs in δ is gδ, with g = −4aΔ/(DN).
- **The Δq closed form follows** from the log-derivative of the product: P′/P = L + λ, λ = τ′/(1 + τ), τ = γs. So
  Δq = (3/16)((L + λ)² − L²) = (3/8)Lλ + (3/16)λ².
- **By hand, the rest of §2–§3:**
  - F = tr N² − tr(M1NM1⁻¹N), via tr N = −det N and Cayley–Hamilton;
  - F₀ = −4 sinh²(κω) n12 n21;
  - the Frobenius norm of B is |Δq|·|√ND|·cosh(2κ Re U)/κ;
  - ‖N − kX‖ ≤ (|k|/r)²(ε_C + ℓ_C² e^{ℓ_C}/2), by the Dyson tail and the maximum principle for Δq/k and
    (Δq − kδq)/k²;
  - ‖Z₁NZ₁⁻¹ − N‖ ≤ η(2 + η)‖N‖;
  - the entry-weighted Cauchy–Schwarz bound for the conjugation by diag(m, 1/m);
  - (Z2) |tr N| ≤ √2‖N‖_F;
  - (Z3) |tr M1(k) − tr M1(0)| ≤ ‖M1(0)‖_F η, and below |Im tr M1(0)| that rules out [−2, 2] and 0;
  - each bound/t² is monotone in t, so a pass at t covers every smaller t.
- **The majorant tables, read line by line:**
  - √(1 − x) = 1 − x/2 + R(x), |R| ≤ |x|²/(8(1 − |x|)) (binomial coefficients |a_n| ≤ 1/8 for n ≥ 2);
  - Φ̄ ≥ |φ| and h ≥ |c_K″||φ| on |u| = ν, both decreasing (Φ̄′ ∝ −96x − 24 < 0);
  - upper Riemann sums at left endpoints, tails h ≤ 3.002·4Φ̄(V)/(a³ν⁴) for ν ≥ V ≈ 410;
  - A0 = a²∫(ν − ν₀)h = a²∫T1, path-independent along the radial ray in |s| ≥ |z|, where |kφ| < ½.

## (3) The per-box bounds against INDEPENDENT truth: all PASS
(`scripts/_nve_eps_office_tailcheck.py` → `eps_office_tailcheck.out`)
- **Method.** Truth comes from direct mpmath quadrature (not the majorants):
  - c0(z; k) and c0′(z; k) of c_K″√(1 − kφ) along the radial ray;
  - c1 by quadrature (not the closed form);
  - q from its definition;
  - δq as a numerical directional derivative.
  The bounds come from the certifier's own `box_bounds` and `majorants`, on its own boxes: 12 circle boxes and 25 lasso
  boxes, including the 8 nearest r₊ and p₊, with 8 values of k on |k| = r_ref.

| spin, r_ref | max \|Δq\|/α | max \|Δq − kδq\|/β | max \|ε₂\|/e0 | max \|ε₂′\|/e1 |
|---|---|---|---|---|
| 3/5, 0.003 (the one used) | 0.888 | 0.304 | 0.737 | 0.627 |
| 3/5, 0.3 | 0.693 | 0.263 | 0.703 | 0.593 |
| 9/10, 0.0003 (used) | 0.922 | 0.529 | 0.557 | 0.400 |
| 9/10, 0.3 | 0.702 | 0.452 | 0.525 | 0.377 |
| 3/10, 0.003 (used) | 0.788 | 0.192 | 0.908 | 0.868 |
| 4/5, 0.001 (used) | 0.891 | 0.528 | 0.616 | 0.468 |

- **Every ratio is ≤ 1:** the bounds are valid, and fairly tight.
- **Must-fail** (bounds divided by 1000): it fires at every spin.

## (4) The controls can fail as wired
- **Must-refuse (spin 3/5, `EPS_REFUSE=1`).** All 372 rows pass the holomorphy boxes, and every one has t = 0. So the
  refusal comes from the (Z1) inequality with |c2| set to 0, **not** from something incidental.
  - Code note: the printed reason is chosen by the flag `c2lo == 0`, not by the failing path. The rows show the
    reason is true here, but it should be derived from the failing check.
- **227/250.** r = 5.4e−8 is far below the third zero (|k| ≈ 1.6e−4), and the certified c2 interval contains the
  engine's value.
- **Engine consistency.** The certified remainder bound is 2,500 to 5,400 times the true |F − c2k²| (Fable's run; not
  repeated here).

## (5) The lasso polygon, certified EXACTLY (`scripts/_nve_eps_office_polycheck.py` → `eps_office_polycheck.out`)
- **Method.** The certifier's own polygon, tested in rational arithmetic (fractions).
- **Checks:**
  - the ring is a strictly convex polygon with distinct vertices, so a simple closed curve;
  - r₊ and p₊ are strictly inside it, at distance ≥ 0.1199 (registered) or ≥ 0.2409 (wide);
  - r₋ and p₋ are strictly outside;
  - the base point is outside;
  - the tail meets the ring only at its endpoint.
- **PASS at all 5 spins and all 3 wide variants.** So the lasso is tail · (a simple loop around exactly {r₊, p₊}) ·
  tail⁻¹, with winding numbers (1, 0, 1, 0).
- **Code note.** The certifier's own winding and U-increment checks (`ok_w`, `ok_u`) are PRINTED but do not gate the
  verdict. They held in every run. They should be hard gates; correctness gates may stop a run.

## (6) The one rigour slip: knife-edge bisection plus one under-bound
- **The slip.** In `assemble`, the conjugation weight |m|⁻⁴ on the small entry is divided by `mu2²`, where `mu2` is an
  UPPER bound of |m|². It needs a lower bound.
- **Why it matters at all.** `largest_t` bisects 60 times to the exact boundary, so the stored r sits at equality.
- **Recomputed** with the divisor replaced by a lower bound (mu2/(1 + 1e−7)²), from the stored constants:
  - at the stored r, (Z1) FAILS at every spin;
  - the largest certified r falls by 1.3e−10 to 4.4e−10 relative;
  - 0.9999·r passes everywhere.
- **Quote:** ε_a ≥ 2.79e−3 (3/10), 1.92e−3 (3/5), 8.39e−4 (4/5) and 1.06e−4 (9/10), and 5.4e−8 for the 227/250
  control.
- **Code fix to make:** use the lower bound in that divisor, and return r·(1 − 1e−6) after the bisection.

## (6b) The code fix, run, not argued (the Bridge's request; branch `office/2026-11-26-eps-fix`, commit 9d0ee9f, on top of Fable's 4bc7b37)
**Changes to `_nve_eps_certify.py`:**
- the |m|⁻⁴ weight now uses a LOWER bound of |m|², `mu2lo` = exp(2 min|Re κω|)·(1 − 1e−7), from the enclosure of Re κω;
- after the bisection, r is replaced by r(1 − 1e−6) and re-verified, and the run fails if it does not pass;
- the winding and U-increment checks are hard gates: a failure stops the run with no r;
- the refusal reason is now derived from the failing check, not from a flag.
All 10 runs were redone (all 10 homotopy gates True).

| run | fixed-code r | (a) passes the corrected test at r | quoted (3 s.f., rounded down) | (b) quoted ≤ r, and passes |
|---|---|---|---|---|
| 3/10 | 2.799955e−3 | yes (the code, and my own transcription) | **2.79e−3** | yes, yes |
| 3/5 | 1.925557e−3 | yes | **1.92e−3** | yes, yes |
| 4/5 | 8.398961e−4 | yes | **8.39e−4** | yes, yes |
| 9/10 | 1.063034e−4 | yes | **1.06e−4** | yes, yes |
| 227/250 (control) | 5.422438e−8 | yes | 5.42e−8 | yes, yes |
| wide lassos 3/10, 3/5, 4/5, 9/10 | 2.799955e−3, 2.796175e−3, 1.443614e−3, 1.472037e−4 | (printed by the code) | — | — |

- **The refusal control now prints** "NO r ((Z1) fails at every t, even t = 1e−12 r_ref: the |c2| lower bound is 0, so
  c2k² cannot dominate)".
- **The bounds on |m|²** (mu2lo ≤ |m|² ≤ mu2) are recorded in each JSON. Their relative width is about 2e−7.
- **So the quoted table rests on a run of the corrected code.**

## (7) "The k = 0 lasso is kept fixed": acceptable wording
- For |k| ≤ r the holomorphy boxes certify that no zero of P or of f0² + c0² reaches L.
- So the engine's re-centred lasso and the fixed one are homotopic, and both are elements of the monodromy group.
- Statement A needs only two elements that generate a Zariski-dense subgroup.

**Environment:** Python 3.14.5 (.venv), mpmath 1.3.0, sympy 1.14.0, macOS arm64. One core, nice 12, at box load ~24.
The 10-run rerun took about 17 min; the tail check about 25 min; peak < 150 MB.

---

# Part B (Fable commit 4bc7b37): office check, 2026-11-26
**Verdict:** the prototype is CORRECT as a prototype. It certifies nothing over an interval of k, as it says itself.
- **(B1) ATAP Theorem 8.2, read AT SOURCE.** The source is the book's own chapter source, `chebfun.org/ATAP/chap8.m`.
  - Hypotheses (from Thm 8.1): f analytic on [−1, 1] and continuable to the OPEN Bernstein ellipse E_ρ, with |f| ≤ M
    there.
  - Conclusions: ‖f − f_n‖ ≤ 2Mρ⁻ⁿ/(ρ − 1) for the Chebyshev projection, and ‖f − p_n‖ ≤ 4Mρ⁻ⁿ/(ρ − 1) for the
    interpolant, in the sup-norm on [−1, 1].
  - "Chebyshev points" are cos(jπ/n), j = 0..n (ch. 2, eq. 2.2), as the code uses.
  - E_ρ is the image of |z| = ρ under the Joukowsky map.
  - The quote from memory is right; the 2019 extended edition was not checked.
- **(B2) "Real k suffices."**
  - CLAIM v3 reads "for every real k ∈ (0, 30/7]", so enclosures along the real interval are exactly what the claim
    needs.
  - Route (i) was NEVER registered. It exists only as a plan (C2_ANALYTIC §7) and in the brief, so this is not a swap
    of a registered method. The route-(i) pre-registration must state it.
  - The registered floating counts (GAPB, WINDOW, SPIN) stay as they are.
- **(B3) Reproduced exactly** on a clean checkout, with the same interpreter (Quantum's pinned Python 3.13.12 and
  python-flint 0.9.0, used read-only):
  - the three point enclosures (k = 1, 21/20, 11/10) are IDENTICAL to the committed ones, string for string;
  - all 16 segment records are identical;
  - the held-out centre test is unchanged (F: 3.37e−8 against a bound of 1.18e−7).
  The log is `eps_office_partB_rerun.out`.
- **(B4) The acos fix is correct.** The Chebyshev recurrence has an all-finite assert. No other path drops a
  sub-ball silently:
  - a non-finite Laurent bound raises;
  - a G1 or G2 box containing 0, or a non-finite q, refuses the disc, so ρ is halved and the run raises at 1e−4;
  - a point too close to the Laurent circle raises;
  - a non-finite node value trips the assert or makes the error bound infinite, which fails safe;
  - `contains(0)` on a non-finite ball reports "does not exclude 0".
- **One precondition is ARGUED, not certified.** The Laurent tail's Cauchy estimate needs c0″ holomorphic in the
  whole disc |w| ≤ 0.9/a, but the code samples |c0″| only on its boundary circle.
  - It holds for spin 3/5 and k ≲ 3: the B roots satisfy |u| = ((10 − k)/(90 − 21k))^{1/4} < 1, φ's poles are at
    |w| = √3/a and c_K″'s at |w| = 1/a, all outside the disc.
  - It must be CERTIFIED in the route-(i) build, by root enclosures; it is cheap.
- **B5, the plan,** is input for a future registration only. Points to carry into it:
  - M must be PROVED on the ellipse (B4 steps 1–2);
  - the Laurent-disc holomorphy check above;
  - every limit listed beside the time estimate, per the no-caps rule (no wall-clock caps; checkpoints per node,
    which `route1_segment.jsonl` already has).
