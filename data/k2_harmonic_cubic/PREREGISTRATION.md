# K2 → K1: is any published planar potential harmonic AND integrable only through a cubic integral?

*Pre-registered 2026-09-24 by ansatz-machine, BEFORE any sweep or computation, at The Bridge's request. It is
light work: web sweep plus symbolic Laplacians and small linear solves. It stops after step 2 with a report.*

## Why it matters
A natural 2-D system H = ½(p_x² + p_y²) + V with a **harmonic** V and a cubic integral I₃ lifts (Eisenhart) to
a 4-D Lorentzian **vacuum** spacetime with a rank-3 Killing tensor. If the system has **no** quadratic integral
(integrable, not superintegrable), that tensor is **functionally independent**, which is open problem K1
(and the problem Cariglia–Galajinsky's conclusion and Filyukov 2017 name). The known example
(SW-IV σ = 0, §147) is superintegrable, so it doesn't count.

## A correction to the plan as handed over, recorded before computing
The third-order lists for **Cartesian-separable** (Gravel 2004) and **polar-separable** (Tremblay–Winternitz)
potentials are superintegrable **by construction**: separability supplies a quadratic integral. Every
harmonic entry there is excluded by rule (c) below. Those lists are searched for the **control class** only.
K1 candidates can come only from classifications of systems with a cubic integral and **no** quadratic one:
Drach (1935), Holt (1982), Fokas–Lagerstrom (1980), Grammaticos–Dorizzi–Ramani, Hietarinta's review (Phys.
Rep. 147, 1987), Galajinsky–Lechtenfeld (arXiv:1306.5238, the prepotential class), and their citers.

## The rule (fixed now)
A potential V(x, y) on flat E² is a **HIT** iff all three hold, each checked exactly in this repo:
- **(a) harmonic:** ΔV ≡ 0 symbolically, for the stated parameter values, with V not affine (an affine V has
  linear integrals and lifts trivially).
- **(b) cubic integral reproduced:** the published I₃ satisfies {H, I₃} ≡ 0 symbolically. If it can't be
  reproduced, the entry is **UNVERIFIED**, never a hit.
- **(c) not superintegrable:** the space of quadratic integrals K^{ij}p_ip_j + W (K a flat Killing tensor, 6
  parameters; W exists iff curl(K∇V) = 0) is **1-dimensional**, i.e. only H. If it's ≥ 2, the entry is
  **EXCLUDED (superintegrable)**, because I₃ is then functionally dependent on the quadratics.

Outcome classes per entry: HIT / EXCLUDED-superintegrable / NOT-HARMONIC / UNVERIFIED.

## Controls (must behave as stated, or the run is void)
- **C1**, must come out EXCLUDED: SW-IV σ = 0, V = √(r+x)/r. Harmonic ✓, cubic ✓, quadratic family dim 3.
- **C2**, must come out NOT-HARMONIC: SW-IV with its Kepler term, V = α/r + β√(r+x)/r, α ≠ 0 (Δ(1/r) ≠ 0 in 2-D).
- **C3**, must pass (b) and (c) (cubic reproduced, quadratic family dim 1): one known integrable-only cubic
  system from the literature (Holt or Fokas–Lagerstrom), whatever (a) says. It shows test (c) can say "not
  superintegrable" and isn't stuck at "excluded".

## Sweep method (step 1)
Citation-graph walks from the anchors (Hietarinta 1987; Galajinsky–Lechtenfeld 2013; Gravel 2004;
Tremblay–Winternitz), using INSPIRE `refersto:recid:<id>` queries. **Each query gets a positive control** (a
known citer must appear) **and a count bound** (the count must be plausible for the anchor). The lesson of the
malformed `refersto:arxiv:` query: a count of 25,061 is noise, not a list. Math-ph papers poorly covered by
INSPIRE are searched on arXiv/Scholar with the same vocabulary. Every query, count and control outcome is
logged in `SWEEP.md`.

## My expectation, stated now so it can be wrong
**No HIT** in any published list. CG 2015 and Filyukov 2017 both pose this as open, and an integrable-only
harmonic cubic system sitting in a classification table would likely have been noticed. Confidence:
moderate. A HIT would be a major result; the most likely HIT-like outcome is a UNVERIFIED entry (an integral
we can't reproduce), which must not be over-read.

## Stop condition
Report to The Bridge after step 2 (symbolic ΔU plus rules (b)/(c) on every listed potential), before
anything further.

---

# STEP 3 (pre-registered 2026-09-24, before reading Tsiganov's list): Drach's cubic-integrable systems

**What CG 2015 already did (read at source first, §2–3):** Drach systems have H = p_x p_y + U(x, y) on a (1,1)
base. The Eisenhart lift is Ricci-flat iff **U_xy = 0 (additivity, U = f(x) + g(y))**, and CG state that
"only two" of Drach's models satisfy it. Both are superintegrable by CG's own footnotes: the first carries
p_y² + 2αx; the second's extra quadratic is the one the workspace's EXP-003 recovered, and its real form is the
§147 pp-wave (SW-IV σ = 0). **Under x = z, y = z̄, Euclidean harmonicity is exactly additivity**, so step 3 is
an *independent check of CG's inspection*, not new ground.

**Rule, per Drach entry:**
1. **Additive?** U_xy ≡ 0 symbolically, as the entry is written. **Prediction to test: exactly two entries
   (CG's claim).**
2. **Real Euclidean form?** For additive entries, whether constants and allowed maps make g = f̄, so that
   V(z, z̄) = f(z) + f̄(z̄) is real, harmonic and non-affine.
3. **Real Lorentzian lift (the Bridge's condition):** the lifted metric is real with signature (1,3). A metric
   that is real only in signature (2,2) is one of CG's own metrics in disguise, and does NOT count.
4. **Rule (c):** the Euclidean real form has a 1-dimensional quadratic-integral family (integrable only).
   HIT iff 1–4 all pass.

**Controls:** C4 = CG's first additive system, U = α(y − βx) + γ/√x: it must yield no non-affine real
harmonic form (f and g can't be conjugate unless γ = 0). C1′ = CG's second, U = α/√x + β/√y: with α = β its
real form must be SW-IV σ = 0 (up to √2) and be EXCLUDED (dim 3).

**Scope caveats, recorded now:** (i) the list is Drach's as presented by Tsiganov (nlin/0001053); Drach 1935
itself is not re-read. (ii) Additivity is tested in the coordinates each entry is written in; a system that
becomes additive only after a coordinate change plus time reparametrisation (Stäckel / coupling-constant
metamorphosis, possible for fixed-energy integrals) would be missed. That is a known blind spot, stated
positively. (iii) Integrals that exist only at fixed energy do not lift to Killing tensors of the full metric
and are excluded.

**Expectation:** no HIT, and CG's "only two additive" reproduced. Confidence: high for "no HIT", moderate
for "exactly two" (it depends on how Tsiganov writes each entry).
