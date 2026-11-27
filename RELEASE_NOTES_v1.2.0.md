# Ansatz Machine v1.2.0: release notes (DRAFT, not released)

**Status: UNCHANGED in kind.** The "Only Kerr" result is still a careful numerical result, not a theorem. v1.2.0
makes the one rigorous local piece, Statement A, explicit: each spin now has a certified radius ε_a. It also records
a new, separate line of work (route (i)) as far as it has been verified. Route (i) is NOT part of the claim. No number
in the main claim changed.

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
- **What the method can reach, as measured by sealed pilots:**
  - segment centres up to k ≈ 3 at spin 3/5 and k ≈ 2 at spin 9/10;
  - nowhere above a centre between k = 3.7 and 3.8 at any spin, where the fixed Laurent arcs fail;
  - so the top of region A (up to 30/7 ≈ 4.29) is out of reach of this method as built.
- **Near k = 0 at spin 9/10,** the evaluator's own uncertainty (about 2.6 × 10⁻⁸) exceeds |F| below k ≈ 2 × 10⁻³.
  A gap is expected there between Statement A's edge and the lowest certifiable k.
- **Production status at the time of these notes: RUNNING, not finished.** Pre-registered scope:
  - spin 3/5 on [ε_a, 3];
  - spin 9/10 on [ε_a, 2], with the expected small-k gap;
  - the top of region A parked.

  No production result is included in this release, and none is claimed.
- **What is unregistered or unapproved, labelled as such:**
  - the pre-registration (`docs/ROUTE1_REGISTRATION.md`) is a draft, with the production scope recorded as an
    amendment;
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
