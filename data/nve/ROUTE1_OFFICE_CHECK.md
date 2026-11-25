# Office check of Fable's first certified route-(i) segment (branch `fable/2026-11-26-route1-seg`: 604d520 and d855810), 2026-11-26

**Checker:** ansatz-machine (office), a non-author.
**Ask:** the Bridge, items (a)–(d), plus reproduction.
**Verdict: VERIFIED.**
- **The result.** At spin 3/5 and E = 4/5, for every real k ∈ [1, 1.1]:
  - |F| ≥ 0.265023401,
  - |tr M0| ≥ 1.993158418,
  - |Im tr M1| ≥ 2.648820919 (so tr M1 ∉ [−2, 2]).
  These hold for the fixed circle polygon |z| = 1.35 and the fixed lasso of k = 21/20.
- **Scope.** It is one segment at one spin, and it is NOT the route-(i) registration. Nothing public changes until the
  Bridge says so.

## Reproduction on clean checkouts (same interpreters: Quantum's pinned Python 3.13.12 + python-flint 0.9.0, read-only; repo .venv for sympy and the engine)
- **v1 (604d520).** I reran prove, nodes (all 36 point evaluations, recomputed) and verdict.
  - `route1_seg_M_nseg1.json` and `route1_seg_verdict_nseg1.json` are BYTE-IDENTICAL.
  - All 36 node records are identical, string for string.
  - The controls are as reported: planted zero refused; precondition fires at 4.2 and 4.01 and certifies at 4.0;
    held-out points consistent; engine values inside the node enclosures.
- **v2 (d855810).** I reran prove, `verdict partB`, `nodes arb` (all 36 recomputed by the all-ball evaluator) and
  `verdict arb`.
  - `route1_seg_M_v2_nseg1.json`, both verdict JSONs and all 36 `nodes_arb` records are BYTE-IDENTICAL.
  - Both verdicts are CERTIFIED with the bounds above.
- **d855810 leaves every v1 file untouched** (git diff 604d520..d855810 touches only new v2 files, the write-up and
  the handover).

## (a) The Dyson chain and the gauge: CHECKED BY HAND
- **The gauge form.** With Y_k = Φ_c W, W′ = Φ_c⁻¹ΔAΦ_c W and W = C T C⁻¹ (C constant and invertible):
  T′ = (Φ_cC)⁻¹ΔA(Φ_cC) T, with T = I at the base point. ΔA = −Δq E21.
- **The rank-one norm.** E21 = e2 e1ᵀ, so (Φ_cC)⁻¹E21(Φ_cC) = [C⁻¹Φ_c⁻¹e2][e1ᵀΦ_cC].
  - With det Φ_c = 1 (Abel), Φ_c⁻¹e2 = J vᵀ, where v = (v1, v2) is the first row and J = [[0, −1], [1, 0]].
  - For 2 × 2 matrices, C⁻¹J = J Cᵀ/det C.
  - So the matrix is J(vC)ᵀ(vC)/det C, and its 2-norm is |vC|²/|det C|, exactly as used.
- **Legitimacy.** ANY constant invertible C gives a valid bound. Its conditioning enters through ‖M_cC‖_F‖C⁻¹‖_F and
  ‖C⁻¹M_cC‖_F, which are computed in balls; v2 also prints ‖C‖_F‖C⁻¹‖_F (≤ 2.151 for the circle, 31.11 for the
  lasso).
- **The bounds:**
  - ‖M(k)‖_F = ‖M_c C T C⁻¹‖_F ≤ ‖M_cC‖_F‖T‖₂‖C⁻¹‖_F;
  - |tr M(k)| = |tr(C⁻¹M_cC·T)| ≤ ‖C⁻¹M_cC‖_F·√2‖T‖₂;
  - |F| ≤ 2 + ‖M1‖_F²‖M0‖_F², using |tr ABCD| ≤ ∏‖·‖_F and ‖X⁻¹‖_F = ‖X‖_F for 2 × 2 matrices of determinant 1.
  - Grönwall gives ‖T‖₂ ≤ exp(∫‖B‖₂|dz|), and |Δq| ≤ |k − k_c| sup|dq/dk| on the convex disc.
- **Sympy, independent of Fable's script:** the combined form (2b), dq/dk = (3/8)λ∂_kλ, is an identity; and the
  radial-integral representation of c0 and c0′ matches the Laurent rule on monomials ω⁴…ω⁸.
- **`step_ref` against `P.step` (v1):** the diff shows only the added segment enclosure, plus namespace changes.

## (b) The float steps: CLOSED by d855810 (and the v1 argument holds)
- **v1.** Every float operation after the ball stage is a conversion of an Arb bound, or a product, sum, square root or
  exp of non-negative quantities, each inflated by 1 + 1e−7. No bound-carrying chain subtracts nearly equal floats.
  Accumulated rounding is at most about 1e−15 relative (exp adds about I·1e−16, with I ≤ 300), so the inflation
  dominates.
- **v2 removes the question.** Every bound is a ball to the printed verdict. Floats remain only as choices (vertices,
  step points, ρ, n, C, sample points), any of which is valid. The printed decimals are rounded outward and
  re-verified (`lo_dec`, `hi_sci`).

## (c) dq/dk enclosed over the WHOLE k-disc and every path box: CLOSED by d855810
- **v1.** It already enclosed dq/dk (it was never sampled): on sub-boxes covering the disc (boxes wholly outside the
  disc were dropped, correctly) and on boxes covering each step segment.
- **v2.** It keeps all 5 × 5 sub-boxes of the square and asserts coverage of the square, of [0, 1] in s and of [0, π]
  in θ. It also asserts the pair counts: 54,075 = 2,163 × 25 on the circle and 17,575 = 703 × 25 on the lasso, none
  skipped. The verdict refuses mismatched counts.

## (d) An independent second implementation: PASS
(`scripts/_nve_route1_office_engine.py` → `data/nve/route1_office_engine.out`)
- **The setup.** The registered 50-digit floating-point engine, which shares no code with the Arb evaluator, on the
  SAME fixed loops: the 96-gon circle and the k = 21/20 lasso polygon.
- **Interior nodes j = 6 and 18** (k = 1.0854 and 1.0146): the engine's F, tr M0 and tr M1 lie inside the certified
  node enclosures.
- **The proved-M chain.** At 4 complex k on |k − 21/20| = R = 0.10625, with T = C⁻¹M_c⁻¹M(k)C and the certificate's own
  gauge matrices: ‖T‖₂ = 1.011 (circle) and 1.055–1.061 (lasso), against e^{I0} = 4.56 and e^{I1} = 2233.
  |F| ≤ 0.349, |tr M0| ≤ 1.995 and |tr M1| ≤ 2.887 there, all far below the proved M.
- So the chain's direction, basis and gauge are right, and the bound is valid and loose, as Fable says.

## Other items
- **Node evaluation (v1).** `arb(ball, 0)` KEEPS the ball's radius, so the v1 nodes were evaluated on the tiny exact-node
  ball, not at its midpoint. The Cauchy widening was redundant there, but conservative. v2 evaluates at the midpoint
  and widens, as written.
- **The walk's vertex gap (Fable's new finding): CONFIRMED by reading.** In `_nve_route1_proto.walk`, an edge ends at a
  float-computed point. That point can miss the vertex by a few ulp, or stop up to 1e−15 short through the
  `done < seglen − 1e−15` exit, while the next edge starts exactly at the vertex. An uncovered sliver of path of
  length ≲ 1e−15 results: harmless at node radii of 1e−9, but not enclosed.
  - It affects Part B (recorded against it in `EPS_OFFICE_CHECK.md`) and the v1 node values.
  - v2's walk ends every edge exactly on its vertex. v2's verdict on its own all-ball nodes is CERTIFIED with the same
    bounds.

**Environment:** Arb work used Quantum's pinned Python 3.13.12 and python-flint 0.9.0 (read-only, `-I`). Sympy and
the engine used the repo `.venv` (Python 3.14.5, mpmath 1.3.0, sympy 1.14.0). One core per run, box load ~10. v1
reproduction 04:00–04:15, engine check about 8 min, v2 reproduction 04:32–04:50; peak < 50 MB.
