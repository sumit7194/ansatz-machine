# K2 → K1 — sweep log (step 1) and result (step 2), 2026-09-24

## Step 1: citation sweep (INSPIRE API; every query with a count bound and a positive control)

| anchor | recid | citers | bound | positive control | outcome |
|---|---|---|---|---|---|
| Cariglia–Galajinsky 2015 | 1351199 | 18 | — | matches the Bridge's V6 count | query form validated |
| Galajinsky–Lechtenfeld 2013 (arXiv:1306.5238) | 1239677 | 5 | ≤ 20 ok | "CG 2015 cites it" — **FAILED**: INSPIRE shows CG 2015 does not cite it | count fine; **the control was mis-chosen by me** (an unchecked assumption), not a broken query |
| Hietarinta 1987, Phys. Rep. 147 | 230388 | 68 | ≤ 150 ok | Galajinsky–Lechtenfeld 2013 present — **ok** | valid list; contains the two key recent classifications |

**Identifier errors caught:** my *guessed* arXiv IDs for Gravel 2004 and Tremblay–Winternitz returned unrelated
papers (a Maxwell-field paper and an exoplanet paper). They were resolved by title instead: Gravel 2004 =
math-ph/0302028 (not in INSPIRE), Tremblay–Winternitz = arXiv:1002.1989 (recid 3018773). Never query a guessed ID.

**The list used:** Mitsopoulos & Tsamparlis, *Cubic first integrals of autonomous dynamical systems in E² by an
algorithmic approach* (arXiv:2301.02473, a citer of Hietarinta 1987), Table I: "Integrable potentials V(x,y)
that admit CFIs of the type J^(3,2)_0", which merges Hietarinta 1987 and Karlovini 2000 and adds new entries.
Read from the arXiv **LaTeX source**, because the ar5iv rendering truncated before the tables. Also located:
Tsiganov, *On the Drach superintegrable systems* (nlin/0001053), whose abstract promises "a complete list of all
known systems on the plane which admit a cubic invariant". Its abstract does NOT claim all Drach systems are
superintegrable (only a Stäckel subset). **Not yet processed**; see the open item.

## Step 2: result (`scripts/_k2_harmonic_cubic.py` → `step2.out`)

Controls: C1 (SW-IV σ=0) harmonic ✓ (its superintegrability was measured in §147); C2 (with a Kepler term) not
harmonic ✓; C3 (the Holt-type V3) cubic reproduced ✓ and quadratic family **dim 1** ✓, so test (c) can say
"integrable only".

| Table I entry | verdict |
|---|---|
| V1 F₁(y+√3x)+F₂(y−√3x)+F₃(−2y) | harmonic ⇔ harmonic quadratic + affine → separable → quadratic family dim 2 → **EXCLUDED** |
| V2 Toda exponentials | ΔV = 4k²(…) ≠ 0 → **NOT-HARMONIC** |
| V3 Holt type | harmonic only if all parameters vanish → **NOT-HARMONIC** |
| V4 (xy)^(−2/3) | ΔV ≠ 0 → **NOT-HARMONIC** |
| V5 (x²−y²)^(−2/3) | ΔV ≠ 0 → **NOT-HARMONIC** |
| V6 k₁/r² + (k₂e^{√3θ}+k₃e^{−√3θ})/r³ | each homogeneous piece nonzero → **NOT-HARMONIC** |
| V7 (new in MT 2023) | harmonic only for k₁=k₂=k₃=0 (linear in k; checked at 4 points) → **NOT-HARMONIC** |
| V8 k/r + F₂/r² + F₃/r³ | harmonic sub-family (k=0, F₂∝cos/sin 2θ, F₃∝cos/sin 3θ) killed by the paper's own side condition: sin6/cos6 coefficients 27(C−D)(C+D)/4, −27CD/2 → C=D=0 → trivial |

**HITS: none**, in Table I of arXiv:2301.02473, for cubic integrals of type J^(3,2)_0. As pre-registered:
a clean negative, relative to that list and that integral type.

## Open item (NOT done — beyond the pre-registered stop)
The most promising remaining source is **Drach's list** (via Tsiganov nlin/0001053). The §147 object came
from Wick-rotating a Drach system on a (1,1) base: there Ricci-flatness is U = f(x) + g(y), and with x = z,
y = z̄ the Euclidean potential is harmonic **iff g = f̄**. So every Drach system of that form with conjugate f, g
is a harmonic real potential by construction, and the only question is superintegrability. Drach systems
written in complex coordinates may not appear in real Cartesian tables like MT's in recognisable form. Step 3
would be: go through Drach's list, find the entries with a Euclidean real form, and test rule (c) on each.

## Step 3: Drach's ten systems (`scripts/_k2_drach.py` → `step3.out`)

Read CG 2015 §2–3 first, at source: additivity U_xy = 0 on the (1,1) base **is** Euclidean harmonicity under
x = z, y = z̄. CG report only two additive Drach systems, both superintegrable by their own footnotes. Drach's
list is taken from Tsiganov nlin/0001053, eqs (a)–(l), read from the LaTeX source.

**Additivity**, as a linear condition on the couplings (α, β, γ): null space of U_xy sampled at 50-digit
precision. The gap is clean: zero singular values print as 0.0, the others are ≥ 3e-5. (a) was handled
analytically (complex exponents): not additive.

- **The literal count, 6 entries (d, e, f, g, k, l), did NOT match the pre-registered "exactly two".** The fault
  is my criterion, which counted degenerate members. (d) and (f) become additive only by collapsing to a
  function of x alone; (g) only by becoming affine; and (k) is (l) under x ↔ y, up to an affine term.
  **Reduced count: (e) and (k)≡(l), which are CG's two**, reproduced under that equivalence and not under my
  literal test. Recorded as a flaw in how I pre-registered, not glossed.
- **Real Euclidean forms** (need U = f(z) + f̄(z̄), non-affine): one-variable members have no conjugate pair;
  (g) is affine; (k)'s pair (γx, αy^(−1/2)) can't be conjugate; (l) forces β = 0, so affine; **only (e)**
  survives, and its real form is exactly the §147 potential, SW-IV σ = 0, **superintegrable → EXCLUDED**.
  These real-form steps are **argued, not computed** (the script labels them so), except (e)'s
  superintegrability, which was computed in §147.

**HITS: none.** Across MT 2023 Table I and Drach's list, no published planar potential is harmonic and
integrable only through a cubic integral. K1 stays open, now with the two obvious reservoirs checked.
Blind spot, as pre-registered: systems that become additive only after a coordinate change plus a time
reparametrisation (Stäckel transform) are not covered.
