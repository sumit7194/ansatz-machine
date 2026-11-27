# SEAL: two small checks before any v7 decision. (1) Loop closure for a finite-loop c0. (2) The 9/10 stop-(c) scan

**Office ansatz-machine (Claude Opus), 2026-11-27.** On Sumit's go, via the Bridge ("yes go ahead with both checks"):
- both run on the Mac mini, one process, nice 15;
- the Air productions are untouched;
- no production change and no v7 work.

This note, both scripts and the predictions are committed before either float part runs.

## 1. Loop closure: the mathematics (done before any float)

**Normalisation (read from the code).**
- c0'' = −√(8/5)·a³·√B(z²/a², k)/(z² + a²)³. The branch is fixed by c0'' ~ −12a z⁻⁴ at k = 0, i.e. √B ~ +√(90−21k)·u² at
  large positive u. This is `_nve_lower.radicand` and `_nve_lower_hp`'s header formula.
- c0 and c0' vanish at ∞. Region A uses the Laurent series with C[0] = C[1] = 0. Region B uses c0'(Z0) = −∫_Z0^∞ c0''
  and c0(Z0) = ∫_Z0^∞ (t − Z0) c0''(t) dt along the real axis.

**The finite singularities of c0:**
- the four branch points z = ±a√w±, with w± the roots of B(w, k);
- the poles z = ±ia, of order 3, or of order 2 at k = 4.

B's discriminant is 240k(k − 4):
- for 0 < k < 4 the w± are complex conjugates, with |w±|² = (10 − k)/(90 − 21k) ≤ 1, so all four branch points lie in
  |z| ≤ a;
- for 4 < k < 30/7 they are real and negative, so the branch points lie on the imaginary z-axis. The outer pair runs to
  ±i∞ as k → 30/7.

**Closure of a loop γ** (c0, c0' and √B's sheet all return) requires three things:
- (i) γ winds an even total number of times around the branch points;
- (ii) Δc0' = ∮ c0'' dz = 0;
- (iii) Δc0 = z_s·Δc0' − ∮ z c0'' dz = 0 (by parts; z_s is the base point).

Two facts follow:
- **A loop in a simply connected region free of c0's singularities closes, automatically.** Region B's loops (the
  capsule lasso and the Γ disc) are guarded to lie in |z − Z0| ≤ ratio·R_c, with ratio ≤ 0.6–0.7 and R_c the distance
  from Z0 to the nearest c0 singularity. So they close for every k at which that guard passes.
- **A loop enclosing ALL of c0's finite singularities closes.** c0'' = O(z⁻⁴), so z·c0'' = O(z⁻³), and both integrals
  equal residues at ∞, which are zero. That is the region-A circle |z| = R0, as long as every branch point stays inside
  it. That holds for every k ≤ 4. Above 4 it holds until the outer root reaches |w| = (R0/a)². Bisection on B's
  closed-form roots gives:

  | spin | R0 | k_cross (circle touched) | k at a 0.1 margin |
  |---|---|---|---|
  | 3/10 | 1.1492 | 4.2344 | 4.2251 |
  | 3/5 | 1.35 | 4.1571 | 4.1410 |
  | 4/5 | 1.3382 | 4.0899 | 4.0710 |
  | 9/10 | 1.2639 | 4.0480 | 4.0302 |

  Above k_cross the circle encloses the inner branch pair and ±ia but not the outer pair. √B's sheet still returns
  (two branch points), but Δc0' = −(the period around the outer pair) is generically ≠ 0, so **the circle does not
  close** there.
- **Predicted answer: "closes".** It closes on the circle for k ≤ k_cross(spin) (4.03 to 4.23 with margin), and on
  region B's disc loops from region B's registered start (3.95; 3.8 at 9/10) up to 30/7. The two overlap at every
  spin, and no closed words are needed.
  - This holds for a k-box too, if the same geometric guards hold for every complex k in it.
  - Near 30/7 the region-B loops never come near the escaping branch points, which stay on Re z = 0. Only the
    guard's R_c matters, and it is set by the inner singularities.

## 2. Float check of closure (`scripts/_closure_check.py`)

**What runs:**
- every spin, k ∈ {3, 3.5, 3.9, 4 − 10⁻⁶, 4.02, 4.1, 4.2, 4.25, 4.28, 30/7 − 10⁻⁶};
- two loops:
  - the circle |z| = R0(spin), based at R0;
  - the region-B test circle |z − Z0| = 0.7·R_c(k), with Z0 = 1.954, 2, 1.618, 1.4926 by spin.
- 50-digit mpmath, √B continued by continuity in small steps, the periodic trapezoid rule at 8000 and 16000 points (the change is reported).
- **Printed:** the sheet flip, |Δc0'|, |Δc0| and a scale (max |c0''| on the loop).

**Criteria (registered here):**
- a loop **closes at a k** if the sheet returns and |Δc0'|, |Δc0| ≤ 10⁻³⁰ × max(1, scale);
- it **does not close** if either exceeds 10⁻¹⁰ × max(1, scale);
- anything in between is **unresolved**, and is reported.

| prediction | P |
|---|---|
| the circle closes at every tested k ≤ k_cross(spin) (all k ≤ 4 included) | 95% |
| the circle does NOT close at every tested k > k_cross(spin) (from 4.1 at 4/5 and 9/10; 4.2 at 3/5; 4.25 at 3/10), with the sheet returning and Δc0' ≠ 0 | 90% |
| the region-B test circle closes at every tested k where 0.7·R_c > 0 and it contains no singularity | 97% |
| for k < 4 (3, 3.5, 3.9) two branch points lie in Re z > 0, so R_c (and the test circle) is smaller there; it still closes | 90% |
| overall answer "closes" (no k in [3, 30/7) without a closing pair) | 90% |
| wall time under 10 min | 85% |

## 3. The stop-(c) scan at spin 9/10 (`scripts/_stopc_scan.py`)

**What runs:**
- region A's own machinery (`_nve_lower_kc.ProblemC`, Laurent c0 for complex k; the singular points r±, p± tracked
  by Newton from Kerr's, as in `_nve_spin_scan`);
- the capsule lasso built at k_c (real) exactly as LauA does, and the circle R0 = 1.2639;
- for k_c ∈ {2, 2.5, 3}, a 9 × 9 grid over the route-(i) k-square [k_c ± R] × [±R]i, with R = (1/20)(4 + 1/4)/2 =
  0.10625 (the square P3 used), plus the centre.

**Per k:**
- ρ_c(k) and max |w_root(k)| (the Laurent precondition needs < 1/0.81);
- the tracked points' distance to the circle and to the lasso;
- zeros of G1 and G2 in the annulus ρ_c + 0.02 < |z| < 2.5, counted by winding on |z| = ρ_c + 0.02 and |z| = 2.5 and
  located by Newton from a grid. Each is reported with its distance to the circle and to the lasso.

**"Singularity found" (registered here):**
- for some k in the k_c = 3 square, some singular point of the ρ-equation (any zero of G1 or G2, tracked or found)
  comes within 0.05 of the circle or the lasso (the registered loop guard); or
- max |w_root| over the square reaches 1/0.81.

Anything that comes within 0.15 but not 0.05 is reported as "close", not "found".

| prediction | P |
|---|---|
| at k_c = 2 nothing comes within 0.15 of either loop anywhere on the square | 80% |
| at k_c = 3, "singularity found" | 55% |
| if found, it is a zero of G1 or G2 (a singular point of the ρ-equation), not a c0 branch point | 75% |
| max \|w_root\| stays below 1/0.81 on all three squares (the precondition passed in P3) | 90% |
| the zero counts in the annulus are constant over each square except where a point crosses a counting circle | 80% |
| wall time under 30 min (one process per k_c, in parallel) | 75% |

**What each outcome means:**
- found at k_c = 3 → stop (c) is a nearby complex-k singular point. A narrower segment (a smaller k-square) or
  real-k Taylor models avoid it.
- not found → the 22,000× growth has another cause, which stays open.

**Environment:** Mac mini, `/Users/sumit/Github/conjecture_machine/.venv/bin/python`. That is Python 3.14.10, with
mpmath, sympy and numpy at the versions printed in the result. Each run is one process at nice 15. The scripts are
run from this worktree, `personal/2026-11-26-route1-check`, at the commit that adds this seal.
