# Carter's constant under deformations of Kerr

*What survives, why, and in what form. A write-up of §130–§142 of [RESULTS.md](../RESULTS.md), for a
reader who was not in the room. Everything here is exact linear algebra over GF(p), reproducible from
this repository; every number cites the section and the log that produced it.*

---

## In one page

A spinning black hole in general relativity (Kerr) has a **hidden conserved quantity**, Carter's
constant. It is what makes orbits around it orderly instead of chaotic, and waveform models for
extreme-mass-ratio inspirals lean on that order. Whether it survives when the black hole is deformed —
by a modified theory of gravity, or by anything else — is a question people usually answer with
numerical orbit plots. It can be answered exactly.

1. **It does not survive scalar Gauss–Bonnet gravity.** For the O(ζ)O(χ²) sGB black hole, no
   irreducible Killing tensor exists at ranks 2, 3, 4, 5 or 6 — only the trivial products of energy,
   axial angular momentum and the Hamiltonian. Exact, two primes, with the reducible span subtracted and
   the search space verified to contain the answer. The only published search in this theory
   ([Owen–Yunes–Witek 2021](https://arxiv.org/abs/2103.15891)) stopped at rank 2.
2. **Why it dies:** the sGB correction changes three things — the static gravitational profile, the
   frame dragging, and the hole's shape — and **each one kills Carter by itself**, in three independent
   ways that no combination cancels.
3. **The general rule:** a deformation of Kerr keeps Carter **if and only if it stays separable** (up to
   a coordinate change) — the orbit problem must still split into an independent radial and an
   independent angular problem. Measured, both directions, in a space of 92 deformations.
4. **A trap in the method, and a structure behind it.** Some deformations keep Carter² while killing
   Carter. They are not new symmetries: Carter survives there as a **rational** function of the momenta,
   invisible to a Killing-tensor search, and squaring cancels the denominator. The rank at which a
   hidden symmetry reappears therefore measures the **pole order** of the surviving Carter:
   order 0 → rank 2, order 1 → rank 4, order 2 → rank 6. In the quadrupolar sector the hierarchy
   **saturates at order 2**: rank 8 adds nothing.

The practical upshot for anyone running such searches: *"irreducible" in a polynomial basis is not
"independent" as a function*, and the difference is realised by explicit metrics right next to Kerr.

---

## 1. The instrument

The solver expands both in the coupling ζ and in the spin χ, because the sGB solution is a truncated
double series and is not an exact solution of anything. Writing {H, F} = 0 order by order,

    {H^(0,0), F^(1,n)} = -[ sum_{j>=1} {H^(0,j), F^(1,n-j)} + sum_j {H^(1,j), F^(0,n-j)} ]

the unknown always sits under the **Schwarzschild** bracket, so one matrix is built per rank and reused
at every level. Each level is an exact nullspace over GF(p) — no sampling, no thresholds. Three habits
do the evidentiary work:

- **Known-answer controls that can fail.** The χ-tower with sGB switched off must reproduce Kerr's
  Killing space and must deform L² into Carter — checked to be non-vacuous each time (§130).
- **The representability guard (D44).** A null means nothing unless the ansatz can express the answer;
  every floor direction's correction is tested for membership in the box before the verdict is read.
- **Two primes.** Every closure below is reproduced on p = 2147483647 and p = 2147483629.

The pipeline was rebuilt on 2026-09-19 (D48–D50): a Rust nullspace solver, the operator built from three
brackets per momentum monomial, rescaling instead of re-clearing, polynomial-ring clearing, and level
matrices held as flat arrays. Rank 3 went from 8.5 h to 52 s and rank 4 from 35 h to 4.5 min, with every
checkpoint identical to the old pipeline, expression for expression.

## 2. Scalar Gauss–Bonnet: the ladder (§130–§137)

    rank   ansatz        Kerr directions   floor   survivors at O(zeta chi^2)   both primes
    2      L^6, 24x20     5                 4       4                            yes
    3      L^6, 24x20     8                 6       6                            yes
    4      L^7, 27x24    14                 9       9                            yes
    5      L^7, 27x24    20                12      12                            yes
    6      L^8, 30x28    30                16      16                            yes

Read: *no irreducible Killing tensor of the O(ζ)O(χ²) sGB black hole at ranks 2–6, analytic in ζ with a
Kerr root, within the stated ansatz, by exact null over GF(p) on two primes, with the complete reducible
span subtracted.* Ranks 4 and 6 are the informative rungs (D42): Q² first exists at rank 4 and Q³ at
rank 6, so their outcomes are not implied by Carter's death at rank 2.

**Ceilings, in order of severity** (CLAUDE.md §3): the method is perturbative, so anything
non-analytic in ζ is invisible to it; the ladder is finite; and each closure is relative to its ansatz.

## 3. Why Carter dies in sGB (§138)

The sGB correction is a sum of physically distinct pieces. Switching them on one at a time (rank 2,
`KT_SGB_PIECES`, `data/anat/`):

    static  spherically symmetric reshaping (zeta chi^0)      Carter DIES
    rot     correction to frame dragging (zeta chi^1)         Carter DIES
    l2      quadrupolar shape change (zeta chi^2)             Carter DIES
    l0      spherical part at O(chi^2)                        Carter survives
    none    (plain Kerr, positive control)                    Carter survives

`l0` is harmless for a clean reason: at the order where Carter is tested it meets only the non-rotating
background, so it cannot break the rotational structure Carter is built from.

Exactly (`scripts/_kt_anatomy.py`): the obstruction is linear in the deformation, so the Carter-preserving
deformations form a subspace — spanned by `l0`, a spin shift, a mass shift and two coordinate changes —
and the obstruction space is **3-dimensional**. The three harmful pieces break Carter in three
independent ways; no combination cancels, with or without Kerr's own parameters re-tuned. Coordinate
changes cannot help either: their obstruction is identically zero, as the controls confirm.

## 4. The general rule: Carter ⟺ separability (§139)

Take **every** stationary, axisymmetric, reflection-symmetric deformation of slowly rotating Kerr in
Regge–Wheeler-type slots, each with a free radial profile (`scripts/_kt_carter_space.py`):

    eps chi^0  static, spherical    tt, rr, angular
    eps chi^1  frame dragging       l = 1 (Kerr-like), l = 3 (a current octupole)
    eps chi^2  spherical            l0tt, l0rr, l0ang
    eps chi^2  quadrupolar (shape)  l2tt, l2rr, l2ang

Results (profiles r⁻¹…r⁻⁶, and r⁻¹…r⁻⁸ as a check):

- **ℓ = 3 frame dragging kills Carter at first order in spin**, for any profile.
- **The spherical χ² sector is entirely free.**
- **Static, ℓ = 1 dragging and shape cannot move alone**: the static tt and rr profiles are *determined*
  by the angular part, the dragging and the shape. 3 conditions per power of 1/r plus 5 low-order ones,
  identical at both cutoffs.
- Controls (spin shift, mass shift, two coordinate changes) are inside the compatible space.

Then the interpretive step (`scripts/_kt_separable.py`). A metric whose Hamilton–Jacobi equation
separates keeps a Carter constant exactly; the general such class (Carter 1968; Benenti–Francaviglia
1979) is

    St g^ab = [A_tt(r), A_tphi(r), A_phiphi(r); A_rr(r)] + [B_tt(th), B_tphi(th), B_phiphi(th); B_thth(th)],
    St = R(r) + Theta(th)

with [Johannsen's metric](https://arxiv.org/abs/1501.02809) the subfamily whose radial (t, φ) block is a
perfect square. Transcription was checked twice (trivial functions reproduce our Kerr pieces exactly; the
r/θ split holds for arbitrary functions), and **all 88 linearized Johannsen deformations come out
Carter-compatible** in the tower — an independent test the map could have failed.

Comparing the two spaces as metric perturbations:

    comparison family                                        compatible directions NOT inside
    Johannsen subfamily + coordinate changes                        12
      + horizon-factor profiles                                     10
    GENERAL separable class + full coordinate changes                0     <- and the 23 non-compatible
                                                                             slot directions are outside

**Within this space, a deformation keeps Carter if and only if it is a separable deformation up to a
coordinate change.** Both directions measured. The principle is classical; what is new here is the direct
measurement without the classical structural assumptions, the explicit map of which sectors are locked
together, and the sGB diagnosis placed inside it.

## 5. The rational Carter, and the pole-order ladder (§140–§142)

**The trap.** At rank 4, two shape deformations keep Carter² while Carter itself dies — at face value an
irreducible rank-4 hidden symmetry. Stress tests (bigger ansatz L⁸ box 34×28, both primes, rebuilt from
scratch) did not break it. But the algebra settles what it is: from K = Q² + εK₁ conserved to first
order, {H₀, K₁} = −2Q{δH, Q}, and since {H₀, Q} = 0,

    G = K1 / (2Q)    satisfies    {H0, G} = -{dH, Q}

— **Carter survives, as a rational function of the momenta**, and squaring cancels the pole. The same
algebra generalises: a surviving Q^(m+1) means a Carter with a pole of order m. Hence a prediction:
*the first surviving power of Carter reads off the pole order.*

Measured, in the shape sector, with every count predicted before the run:

    deformation          rank 4            rank 6                      rank 8
    pole order 0 (separable)  all 14       all 30                      all 55
    d1, d2  (pole order 1)    9 + Q^2 = 10  16 + 4 + 1 = 21            25 + 9 + 4 + 1 = 39
    d3      (pole order 2)    9 (Q^2 dies)  16 + 1 = 17                25 + 4 + 1 = 30
    random                    9 (floor)     16 (floor)                 25 (floor)
    nested compatible spaces  5 < 7         5 < 7 < 8                  5 < 7 < 8 = 8

d3 was found at rank 6 and stress-tested as one concrete metric: Carter dies at rank 2 (L⁸, both primes);
**Carter² also dies at rank 4** (both primes — the falsifiable part: a single pole would have let it
through); Carter³ survives at rank 6 on both primes.

**The ladder saturates.** At rank 8 nothing first appears at Carter⁴: in the quadrupolar sector the
deepest pole is 2. Widening the radial profiles from r⁻⁶ to r⁻⁸ grows the compatible spaces but leaves
the per-order counts (2 at order 1, 1 at order 2) unchanged, so the saturation is not a cutoff effect.

**Consequence for the method (D52).** "Irreducible" as computed by this instrument means *not a
polynomial combination of lower-rank Killing tensors*, which is weaker than *functionally independent*.
Before any surviving direction above the floor is called a hidden symmetry, divide out powers of
lower-rank integrals and check whether the quotient solves the lower-rank equation. None of the sGB
verdicts is affected — every one landed exactly on the floor — but the rule matters the day one does not.

## 6. Where this sits in the literature

- **Separability ⇒ Carter** is Carter (1968); the converse, for Killing tensors with the right structural
  properties, is Benenti–Francaviglia (1979). [Papadopoulos–Kokkotas](https://arxiv.org/abs/1807.08594)
  and [Carson–Yagi](https://arxiv.org/pdf/2002.01028) *build* deformed Kerr metrics by imposing
  separability. §139 measures the converse at O(εχ²) without assuming those properties.
- **Rational first integrals of geodesic flows are a studied object**:
  [Aoki, Houri & Tomoda (2016)](https://arxiv.org/abs/1605.08955) introduce generalised Killing tensors
  and *inconstructible* rational first integrals; Kruglikov ([arXiv:2412.04151](https://arxiv.org/pdf/2412.04151))
  develops relative Killing tensors for them. **Our rational Carters are the constructible kind** —
  G = K₁/(2Q) is built from Killing tensors — so the concept is not new here. What is measured here is the
  hierarchy: which deformations of Kerr realise which pole order, and that the polynomial rank at which a
  symmetry reappears is exactly that order.
- **sGB and dCS**: Owen–Yunes–Witek searched sGB to rank 2 and dCS to rank 6 and conjectured no fourth
  constant; [Deich et al.](https://arxiv.org/html/2203.00524) see small chaotic features numerically in
  both; for dCS, [Cárdenas-Avendaño et al.](https://arxiv.org/pdf/1804.04002) see none and conjecture the
  opposite. No Morales–Ramis (all-rank, differential-Galois) proof exists for any of these spacetimes
  (D51) — the obvious, unclaimed gap.

## 7. Scope — what these results are not

- **Perturbative.** First order in ζ (or ε), through O(χ²); a symmetry non-analytic in the coupling is
  outside what the method can express, at any rank.
- **About a truncated metric.** The sGB solution is a double truncation; an external measurement puts the
  O(χ²) spin-truncation error of the Kerr 220 mode at ~6% at χ = 0.69 and ~19% at χ = 0.90.
- **Not a statement about observed orbits.** "No Killing tensor in this ansatz" is not "EMRI orbits are
  chaotic". That step needs a different instrument.
- **Rank-bounded.** Ranks 2–8 here; no finite ladder implies a statement about all ranks.
- **Basis-bounded** in §139–§142: 11 slots, profiles to r⁻⁸, the stated comparison families, one prime
  for the rank-8 map (both primes for the individual d3 checks).

## 8. Open questions

1. **Why does the pole order saturate at 2?** The shape sector is the ℓ = 2 angular pattern; the bound may
   be set by the angular degree. An ℓ = 4 deformation would test it (rank 8 again for order 3).
2. **Morales–Ramis for sGB** (D51): an all-rank, all-form non-integrability statement, which would beat
   both the rank and the analyticity ceiling. The ZV recipe transfers structurally; the obstacle is that
   the obstruction first appears at O(ζχ²), so a finite-ζ proof speaks only about the truncation.
3. **dCS**, where the literature holds two contradictory numerical conjectures, is directly in range of
   this instrument.

## 9. Reproducing it

```bash
./verify.sh                                   # the gate, including KT1-KT6 (solver-stack equality tests)
KT_SOLVER=rust KT_THREADS=4 .venv/bin/python scripts/_kt_double.py --rank 6 --denpow 8 --margin 6 --control --sgb
KT_SOLVER=rust .venv/bin/python scripts/_kt_anatomy.py          # §138, the three obstructions
KT_SOLVER=rust .venv/bin/python scripts/_kt_carter_space.py     # §139, the compatible space
KT_SOLVER=rust .venv/bin/python scripts/_kt_separable.py --span-only --general --jmax 2   # §139, separability
KT_SOLVER=rust .venv/bin/python scripts/_kt_pole_reduced.py --rank 8 --denpow 7 --margin 6  # §142
```

Controls: `scripts/kt_pause.sh <pid> stop|cont` pauses a run; `echo N > data/KT_THREADS` changes its core
count between solves.

**Errors found and fixed along the way, recorded because they shaped the results**: the floor-representability
formula was wrong for c ≥ 3 and had never been measured correctly at rank 6 (D50; the answer, 16, was
unchanged); a silent int64 overflow in `(G @ T) % p` corrupted the first Carter-power breakdowns, caught
because an exactly conserved quantity appeared to die (verification rule 70); and the verdict prose
mislabelled ranks 5 and 6 as "the first independent rung".
