# Brief v1 for the Fable side-session (ansatz-machine-personal): route (i), the FIRST CERTIFIED SEGMENT

**From:** ansatz-machine (office), via the Bridge, for Sumit. 2026-11-26.
**Builds on:**
- your Part B (`data/nve/EPS_EFFECTIVE.md` B2–B5; `scripts/_nve_route1_proto.py`);
- the office check of it (`data/nve/EPS_OFFICE_CHECK.md`, Part B section);
- `docs/ROUTE1_REGISTRATION_INPUT.md`.
**Status of this brief:** nothing goes to you until Sumit says so. This is a single-segment build-and-measure step,
NOT the route-(i) registration.

## 0. The goal in one sentence
Turn the one-segment demonstration into a CERTIFICATE. That is: prove, in ball arithmetic, that at spin 3/5 and
E = 4/5, for every real k ∈ [1, 1.1],
- F(k) ≠ 0,
- tr M0(k) ≠ 0, and
- tr M1(k) ∉ [−2, 2],
with M0 the circle |z| = 1.35 and M1 the engine's lasso at k_c = 21/20, kept fixed.

## 1. What already exists (verified; read these)
- **The validated point evaluator** (`_nve_route1_proto.py`, Arb via Quantum's pinned python-flint 0.9.0,
  read-only). At k = 1, 21/20 and 11/10 it reproduced exactly, and its enclosures contain the engine floats.
- **The interpolation theorem, read at source:** ATAP Thm 8.2 (`chebfun.org/ATAP/chap8.m`).
  - If f is analytic in the OPEN Bernstein ellipse E_ρ with |f| ≤ M there, the interpolant p_n through
    cos(jπ/n), j = 0..n, satisfies ‖f − p_n‖_∞ ≤ 4Mρ⁻ⁿ/(ρ − 1) on [−1, 1].
  - Map [1, 1.1] to [−1, 1].
- **Part A's machinery** (`_nve_eps_certify.py`, verified and corrected; commit 9d0ee9f):
  - the closed form P = P_ref(1 + γs), which gives Δq with no subtraction;
  - the binomial majorant for c0 − c0_ref;
  - the maximum principle in k;
  - the Dyson bound ‖T − I‖ ≤ e^{∫‖B‖} − 1.
- **What is missing**, and what this round builds:
  - (i) a PROVED M (the demonstration only sampled it);
  - (ii) the Laurent-disc holomorphy precondition, CERTIFIED (the office's finding);
  - (iii) enough nodes for the proved M.

## 2. What to build
1. **Laurent-disc precondition, certified.** For every k in the k-region used (below), c0″ = c_K″√(1 − kφ) must be
   holomorphic in the whole disc |w| ≤ 0.9/a, not just bounded on its circle. Certify that the disc contains no zero
   of 1 − kφ(w) (the B roots), and no pole of φ or c_K″.
   - Use the closed-form roots w = u⁻²/a² with u² = [(30 − 9k) ± √(60k(k − 4))]/(90 − 21k), enclosed for k in a
     complex box.
   - At spin 3/5 and k ≈ 1 the margin is large; certify it anyway.
2. **A proved M on a k-disc that contains the ellipse.** The Bernstein ellipse E_ρ around [1, 1.1] lies inside the disc
   |k − k_c| ≤ R, with R = 0.05(ρ + 1/ρ)/2. Bound F, tr M0 and tr M1 on that disc:
   - **Reference solution.** Take the validated reference solution Φ along both loops at k_c = 21/20 (the evaluator
     gives it step by step; between steps use the Taylor enclosure with its tail, so that Φ is enclosed on whole
     path pieces, not only at nodes).
   - **The perturbation.** Generalise Part A's closed form to a reference k_c: with δ = c0(k) − c0(k_c),
     G2 = G2_c(1 + σ_c), σ_c = (2c0_cδ + δ²)/G2_c, and P = P_c(1 + γ_c s_c), s_c = σ_c/(1 + σ_c),
     γ_c = f0/(G2_c P_c).
     - **Check this with sympy first.** It is the k_c analogue of the identity the office verified.
     - The binomial majorant now acts on √(1 − (k − k_c)φ/(1 − k_cφ)), which needs a lower bound on |1 − k_cφ| along
       the radial rays.
     - On boxes covering the loops this gives sup |Δq| over the disc, together with the holomorphy certificate
       (σ_c < ½, |γ_c s_c| < ½).
   - **The Dyson bound.** ‖M_loop(k)‖ ≤ ‖M_loop(k_c)‖·exp(∫‖Φ⁻¹‖‖Φ‖|Δq||dz|), with ‖Φ⁻¹‖ = ‖Φ‖/|det Φ|.
     |det Φ| = 1 if Φ is normalised to I at the base point (Abel; there is no first-derivative term).
   - **The bounds.** |F| ≤ 2‖M1‖²‖M0‖² + 2, and |tr| ≤ 2‖·‖. These give M_F, M_0 and M_1.
3. **Choose n from the proved M.**
   - Pick ρ and n so that 4Mρ⁻ⁿ/(ρ − 1) is well below the smallest |interpolant| (≈ 0.265 for F).
   - The Dyson exponent may be large: Part A measured about 80 per unit |Δk| on the lasso at k = 0. If so, use more
     nodes or a smaller ρ, or split the segment.
   - Report the trade-off you chose, with the numbers.
4. **Point evaluations** at the n + 1 Chebyshev points. Reuse Part B's per-node jsonl checkpoint, keyed (spin,
   segment, n, node).
5. **The enclosure.** Clenshaw or the recurrence on sub-balls, with the all-finite assert, ± the proved bound. The
   verdict holds iff all three conditions hold on every sub-ball.

## 3. Controls (each must be able to fail; report every one)
| control | wiring | must |
|---|---|---|
| **planted zero** | certify "F − F(k_c) ≠ 0" on the same segment (it vanishes at k_c) | REFUSE (no certificate) |
| **planted precondition** | the root-enclosure check of §2.1 at k = 4.2 (+ a small complex box), where the B roots leave the safe region relative to |w| ≤ 0.9/a. If they do not at spin 3/5, pick the k where they do, and say so | FIRE (precondition fails) |
| **held-out points** | validated point evaluations at 3 non-node k in [1, 1.1] | each enclosure overlaps interpolant ± bound |
| **proved M ≥ sampled** | Part B's 8 ellipse samples (rerun, or from `route1_segment.jsonl`) | every sampled \|f\| ≤ the proved M |
| **engine** | the 50-digit engine's F, tr M0, tr M1 at two nodes | inside the node enclosures |
| **shrunken-M must-fail** | redo the verdict with M divided by 10¹² | held-out consistency or the verdict must break somewhere; if nothing breaks, say why (the control is then uninformative, which is a finding) |

## 4. SEALED prediction (the office's, written before any run; report against it)
- **The Laurent precondition** certifies at k ∈ [1, 1.1]. It fails at large k: B roots move toward the disc as
  k → 4.
- **The proved M_F** lies between 1e2 and 1e8. The wide range is the honest state, because the Dyson constant at
  k ≠ 0 is unmeasured.
- **The number of nodes needed** for a certified error ≤ 1e−3 is between 10 and 40.
- **The certified minimum of |F|** on [1, 1.1] is ≥ 0.26, consistent with the engine's 0.26533 at k = 1.
- **The certificate SUCCEEDS** on [1, 1.1]: probability about 70% this round. The main risk is a proved M so large that
  the node count exceeds the window.
- **Wall time:** 15–60 min on one core of a busy box (≈ 30 s per point evaluation at 10–40 nodes, plus the boxes).
- If any of these is wrong, report it plainly. A failed prediction is information.

## 5. Deliverables (branch only)
- **Branch** `fable/<date>-route1-seg` from current main (ddcbd53 or later).
- **`data/nve/ROUTE1_SEGMENT.md`:**
  - what is certified and what is only argued;
  - the generalised closed form, with its sympy check;
  - the proved M and the chosen (ρ, n);
  - the verdict and every control;
  - the sealed-prediction scorecard;
  - the measured Dyson constant c at k ≈ 1 (the missing input of B5);
  - a revised per-spin cost estimate for the full run.
- **`scripts/_nve_route1_segment.py`** (it may import from `_nve_route1_proto.py`), with outputs in
  `data/nve/eps/route1_seg_*`.
- **Commits** tagged `[model: Fable 5.2]` and marked UNVERIFIED. **Do not edit** the claim, ONLY_KERR, MRS_SECTION,
  RESULTS or the JOURNAL. The office checks and integrates.
- **A handover** `docs/HANDOVER_FABLE_<date>.md`.

## 6. House rules (unchanged)
- **Compute:** one process, 1 core, nice 12, and the core counts toward the fleet's 9 (wait if the box is full).
  Peak well under 1 GB.
- **NO job-ending caps:** no `timeout`, alarm() or step caps. On pressure, pause and report. Correctness gates stop
  only at a checkpoint.
- **Checkpointing:** one jsonl line per point evaluation.
- **python-flint** from Quantum's venv, read-only, with `python -I`.
- **Literature:** quote at source or mark "from memory".
- **Results that don't work out:** a refusal, or a proved M too big to use, is a result. Report the dominant factor
  and the cheapest fix.
- **If the window runs short:** finish §2.1–§2.2 (the precondition and the proved M, with the sympy check) cleanly
  before the node count. A proved M alone, with its measured Dyson constant, is already the missing input of B5.
