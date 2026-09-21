# Scope manifest for objects shipped out of this repo

Adopted from the bridge's `ops/SCOPE_MANIFEST.md` after five scope statements failed to ship with one
object in one night. **An object ships with all seven fields or it does not ship.**

The diagnosis the form exists for: the pattern was never *getting scope wrong* — every omitted
statement was true and known. It is that scope is **invisible from both ends**. The sender cannot see
it because the object is complete in a frame where every assumption is ambient; the receiver cannot
see it because **absence has no signature** — a truncated object and an exact one are the same
characters on the page. No amount of care by either party catches it, which is why it recurred five
times rather than once.

| field | what it must say |
|---|---|
| **OBJECT** | the actual mathematical object, not the role it plays |
| **EXACT IN** | parameters carrying no truncation |
| **TRUNCATED IN** | every other parameter, **with the order**. No truncation line = read as exact |
| **VALID RANGE** | per parameter, **with the size of the first neglected term at the boundary** |
| **CONVENTIONS** | H halved? Q Carter or total? coordinates, signature, mass normalisation |
| **UNIQUE?** | unique object, or one representative of a family — and what the freedom is |
| **NOT CHECKED** | stated **positively**; absence of a claim is not a claim of absence |

`VALID RANGE` carries a **positive instruction**, not just a caution: **state which parameter is
EXACT, because that is the one to push, not the one to shrink.** An object exact in ε and truncated
in χ gets *better* as ε rises (the truncation floor is fixed while the signal grows quadratically)
and only linearly better as χ falls. Three rounds of this leg swept ε *downward*, deeper into the
floor-dominated half, because everyone was shrinking the parameter they were worried about. The
crossover sat above every grid point used. This is the same fact as "the truncated parameter was held
fixed while the exact one was swept to zero", now saying which way to go.

`VALID RANGE` is deliberately not "state the range": "χ ≤ 1" is true and useless, while
"χ⁴ = 0.13 at χ = 0.6" is the number that stops a sweep. `NOT CHECKED` is the only field a careful
receiver cannot reconstruct from the object itself.

---

## K1_A.txt — RETROSPECTIVE MANIFEST

- **OBJECT** — the O(ε) correction to **chain 4**, a basis vector of this solver's rank-2 Kerr
  nullspace. **NOT the correction to Carter.** chain4 = −8·L² + P_φ² + 56χ²(H + P_t²), H unhalved;
  equivalently −8Q − 7P_φ² + 56χ²(H + P_t²) with Q = Carter = L² − P_φ².
- **EXACT IN** — ε at first order: {H_def, chain4 + εK₁} = 0 at O(ε) exactly, verified symbolically.
- **TRUNCATED IN** — **χ, at order 2**, verified exactly through χ². **CORRECTED 2026-09-22: the
  first uncontrolled order is χ³, NOT χ⁴.** chain4 is even in χ, but Kerr's Hamiltonian is not of
  definite parity — g^{tφ} ~ a makes H_χ¹ nonzero and odd (verified: it is the only level carrying a
  P_t·P_φ cross term). So the χ³ bracket is {H₃,B₀} + {H₁,B₂}, generically nonzero. Both the bridge
  and I said χ⁴; a collaborator's measured truncation exponent came in at 3.17 / 3.13 / 3.08 and
  their refusal to round it to 4 is what caught it.
- **VALID RANGE** — χ: first neglected term is O(**χ³**); χ³ = 0.216 at χ = 0.6, χ³ = 4.2e-4 at
  χ = 0.075. A finite-χ drift test at 0.6 is dominated by truncation. ε: valid while ε·|h| ≪ 1 pointwise on the
  sampled region; at r ∈ [5.1, 9.1] that is 0.06–0.6% for ε = 0.05.
- **VALID RANGE, in r** — **K₁ has a GENUINE SIMPLE POLE AT THE HORIZON, r = 2M.** Verified:
  at x = 2 every (x−2) factor drops and the numerator leaves 1024·χ²·P_t²·y²(y²−1) ≠ 0, against the
  simple zero in x⁴(x−2)(y²−1); **residue 64·χ²·P_t²·y²**. Not a chart artefact — (y²−1) appears in
  numerator and denominator and the axis is regular, while r = 2M is physically distinguished. So
  **the first-order expansion has a shrinking radius of validity in the SPATIAL coordinate, not only
  in ε: it is uniform only for ε ≪ (r − 2M).** Every test run so far used orbits at r ∈ [5.1, 9.1],
  well outside, so nothing measured is affected.
- **CONVENTIONS** — `hamiltonian()` **carries a factor 1/2**. The 56 coefficient is in *unhalved* H;
  in code units it is 112χ²H_code + 56χ²P_t². Coordinates x = r, y = cos θ; M = 1; χ = a.
- **UNIQUE?** — **No.** Defined up to adding any Killing tensor of the undeformed background. The
  *absolute* drift is choice-independent; any **normalised** drift is not, since adding P_φ², P_t² or
  H changes |chain4 + εK₁| without changing its drift. εK₁/Q reaches ~11 at χ = 0.9.
- **NOT CHECKED** — the second prime for K₁'s extraction beyond the CRT re-reduction; behaviour at
  χ > 0.6; whether the grade-2 survivor is literally the square of anything (D52 divide-out not run);
  any statement about geodesics, chaos, or observable orbits.

## CHAIN4.txt — see the file's own header, corrected 2026-09-22
