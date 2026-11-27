# Ansatz Machine v1.2.0: release notes (DRAFT, not released)

**Status: UNCHANGED in kind.** The "Only Kerr" result is still a careful numerical result, not a theorem. v1.2.0
makes the one rigorous local piece, Statement A, explicit: each spin now has a certified radius ε_a. It also records
a new, separate line of work (route (i)) as far as it has been verified. That includes one finished, checked production
result: at spin 3/5, interval certificates cover every real k in 0 < k ≤ 3, an internal result. Route (i) is NOT part
of the claim. No number in the main claim changed.

## What changed since v1.1.0 (tag v1.1.0, 2026-11-25)

### 1. Claim v3.1: Statement A with an explicit, certified ε_a (`data/nve/CLAIM_FAMILY_II.md`)
- **What it says.** For each tested spin a ∈ {3/10, 3/5, 4/5, 9/10} at E = 4/5, and every complex k with
  0 < |k| ≤ ε_a, the monodromy group of the lower-axis ρ-equation is Zariski-dense in SL(2, C).

  | spin a | 3/10 | 3/5 | 4/5 | 9/10 |
  |---|---|---|---|---|
  | ε_a (interval-certified, rounded down) | 2.79 × 10⁻³ | 1.92 × 10⁻³ | 8.39 × 10⁻⁴ | 1.06 × 10⁻⁴ |

  In v1.1.0, ε_a existed but was not quantified.
- **What ε_a certifies, exactly.** For every complex k with 0 < |k| ≤ ε_a:
  - the equation's coefficient is holomorphic in k on both loops used, so no singular point reaches them;
  - the monodromies M0 (a circle) and M1 (a fixed lasso, certified exactly in rational arithmetic) satisfy:
    - tr[M1, M0] − 2 ≠ 0 (irreducible);
    - tr M0 ≠ 0 and tr M1 ≠ 0 (not imprimitive);
    - tr M1 ∉ [−2, 2] (infinite).

  Each ε_a is the certifier's radius rounded down to three significant figures, and the rounded value passes the
  test itself.
- **How.** A certified remainder bound, |F − c2k²| < |c2||k|² on 0 < |k| ≤ ε_a.
  - It is built from an exact SL₂ identity for F = tr[M1, M0] − 2 and a Dyson bound in Kerr's solution basis.
  - It is evaluated in interval arithmetic.
  - Sources: `data/nve/EPS_EFFECTIVE.md`; verification in `data/nve/EPS_OFFICE_CHECK.md`, including a bit-for-bit
    reproduction, independent quadrature of every per-box bound, and one slip found and fixed before use.
- **The four conditions are unchanged and part of the statement.**
  1. It is an anchor near Kerr, not new range.
  2. It is rigorous only relative to the applicability chain:
     - Proposition 2 rests on our own proof, not yet independently checked;
     - e₋ = 1/e₊ is assumed, or taken as the definition;
     - one cited theorem number (Lemma C(a)) is secondhand.
  3. c2 ≠ 0 is certified spin by spin, and it is false at spin ≈ 0.908.
  4. Credit as below.

### 2. Route (i): interval certification over stretches of k. Internal, partly verified, not in the claim
Route (i) aims to replace the 50-digit floating-point counts over the range of the twist k ("region A") with
interval-arithmetic certificates, one stretch of k at a time. Method:
- Chebyshev interpolation of validated (Arb) node values;
- a proved bound M on a complex ellipse, via a Dyson bound;
- the ATAP Thm 8.2 error bound.

What is in hand, and how it is graded:
- **Two certified stretches (internal results), both for real k ∈ [1, 1.1].** On each, F ≠ 0, tr M0 ≠ 0 and
  tr M1 ∉ [−2, 2].
  - **Spin 3/5.** Certified by the first implementation, then independently checked. It is also certified by the
    improved enclosure with half the nodes (12 against 24).
  - **Spin 9/10.** Certified with the improved enclosure (18 nodes; the first version needed 140).
  - **Checks on the 9/10 certificate:**
    - it was reproduced byte for byte on a second machine (same pinned Python minor version);
    - every node value was confirmed by an independent 50-digit engine that shares no code with the certifier
      (44 of 44 nodes across both stretches);
    - the code was read by a non-author.
- **A production result at spin 3/5 (internal, checked): certified for every real k in [1/640, 3]**
  (1/640 ≈ 1.56 × 10⁻³). It covers the pre-registered target [ε_a, 3].
  - On that whole range, F ≠ 0, tr M0 ≠ 0 and tr M1 ∉ [−2, 2].
  - It used 35 segments, all certified at the first attempt, with no splits.
  - Every node value of every segment fell inside its interval enclosure under the independent 50-digit engine
    (36 of 36 gate runs).
  - A rerun of every verdict from its stored data was identical, and the must-fail controls refused as they should.
  - **What it means:** this interval overlaps Statement A's (0 < |k| ≤ ε_a, ε_a ≈ 1.92 × 10⁻³). So at spin 3/5 the
    lower axis has interval certificates for every real k from 0 to 3, with no gap.
    - This holds relative to the same applicability chain.
    - It is part of region A, not all of it; region A runs up to 30/7 ≈ 4.29.
  - Record: `data/nve/route1_check/PROD_3_5_RESULT.md` on `personal/2026-11-26-route1-check`, scored against its
    seal, which was committed before launch.
- **What the method can reach:**
  - up to k ≈ 3 at spins 3/10, 3/5 and 4/5, and k ≈ 2 at spin 9/10. This comes from sealed pilots and
    top-of-reach checks, and at 3/5 it is now confirmed by production;
  - nowhere above a centre between k = 3.7 and 3.8 at any spin, where the fixed Laurent arcs fail;
  - so the top of region A (up to 30/7 ≈ 4.29) is out of reach of this method as built.
- **Near k = 0 the evaluator's own uncertainty sets a floor.** Below it, a segment cannot be certified however finely
  it is split (the driver stops that chain at once). As measured by the running productions:
  - at spin 9/10 the floor is at k = 1/80 = 1.25 × 10⁻². This is a larger gap above Statement A's edge (about
    10⁻⁴) than the pre-registered prediction (7.8 × 10⁻⁴ to 3.1 × 10⁻³), recorded as a miss;
  - at spin 3/10 it is at k = 1/320 ≈ 3.13 × 10⁻³, a small gap above ε_a = 2.79 × 10⁻³, as predicted;
  - at spin 3/5 there is no gap.
- **Production status at the time of these notes:**
  - spin 3/5 is finished and checked, as above;
  - spins 9/10 (to k = 2), 3/10 and 4/5 (each to k = 3) are RUNNING. No result for them is claimed here, beyond the
    measured floors above. They are planned for v1.3.
- **What is unregistered or unapproved, labelled as such:**
  - the pre-registration (`docs/ROUTE1_REGISTRATION.md`) is still headed "draft". Its production scope (§5A) and
    Sumit's approval of that scope are recorded in it, but the rest of it has not been approved as a whole;
  - the two certified stretches predate it and are internal.
- **Where the code is.** The route-(i) code (v2 to v6) and its outputs live on branches. This release's tree holds
  only the records on main (`data/nve/ROUTE1_*.md`, `docs/ROUTE1_REGISTRATION*.md`). Branches:
  - `fable/2026-11-26-route1-seg` (v2);
  - `office/2026-11-26-centred-encl` (v3);
  - `office/2026-11-26-ktaylor` (v4 and the 9/10 certificate);
  - `personal/2026-11-26-route1-check` (v5, v6, the checks and pilots).

### 3. Nothing else changed
The one-sentence claim, its conditions and every other number are as in v1.1.0.

## Credit
- **The ε_a certifier:** a separate AI side-session (branch `fable/2026-11-25-eps`, 75957fd), with the coordinating
  repository's code fix 9d0ee9f (merged in bd74e05).
- **Its verification:** the ansatz-machine session (e10f274, bcd9292).
- **Route (i):**
  - the first implementation and the spin-3/5 certificate: the same side-session;
  - the improved enclosures and the spin-9/10 certificate: the ansatz-machine session;
  - the non-author read, reproduction, engine cross-check, hardening and pilots: a second ansatz-machine session;
  - the productions, and the spin-3/5 result and its checks: the ansatz-machine session;
  - the code reads: the coordinating session ("the Bridge").
- All of these are AI sessions working under the author's direction. See the paragraph below.

## AI assistance
This work was carried out with AI assistance: Claude (Anthropic) for code, analysis, literature checks and drafting,
and Gemini (Google) for hostile referee reads and cross-checks. AI outputs were treated as unverified until checked;
every result reported as established was verified independently, by exact symbolic computation, exact linear algebra
over two finite fields, independent reimplementations and 50-digit numerics with must-fail controls, interval-
arithmetic certificates where stated, and sources read at source; results not yet verified this way are labelled as
relayed, numerical or unverified. The author takes full responsibility for the content.

## Citation
Cite all versions as DOI 10.5281/zenodo.24431694. This version (v1.2.0) is DOI [minted by Zenodo at release].
