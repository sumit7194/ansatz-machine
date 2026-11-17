# Which Kerr symmetries survive a small quadrupole deformation, at valence 1–4 (6 if cheap)? An ansatz-free first-order jet test. Design pre-registration, 2026-11-17, BEFORE any build or run

Ask: the user, via the Bridge (item (c), "design and preregistration now; request a compute slot when ready"). This is
the repo's founding question (CLAUDE.md §1): does a quadrupole-deformed Kerr admit an irreducible Killing tensor of rank
3 or 4? Until now it has been answered only inside basis boxes (§130–§146, mod p, analytic in the coupling). This brings
the box-free prolongation bound of §149/§151 to small deformations.

## Method
- H = H₀ + ε H₁ (Kerr plus a first-order deformation), F = F₀ + ε F₁, with F_i ∂_t, ∂_φ-invariant valence-d tensors.
  {H, F} = O(ε²) means {H₀, F₀} = 0 and {H₀, F₁} + {H₁, F₀} = 0.
- **Jet bound:** apply the §149 prolongation at a regular point P to the PAIR (F₀, F₁): stack both equations, with
  jets of F₀ and F₁ up to order M + 1 and M = d. B(d) = #cols − rank is an upper bound on dim{(F₀, F₁)}. The F₁
  solutions with F₀ = 0 are exactly the Kerr KTs (dim K(d) = 2, 5, 8, 14 at d = 1–4).
  So **S(d) := B(d) − K(d) ≥ dim{F₀ ∈ Kerr KTs that extend to first order}**, the surviving directions.
- **Trivial floor:** products of p_t, p_φ, H always survive, at T(d) = 2, 4, 6, 9. S(d) = T(d) proves that nothing
  beyond the trivial products survives at first order (locally; any coefficient form; invariant class; analytic in ε
  with a Kerr root, which is ceiling 1 of CLAUDE.md §3, stated).
- **Arithmetic:** dual-number series over GF(p): every series carries an O(ε) part, built on `_kt_jet.Series` and, for
  √ and exp, `_kt_jet_mn.MNSeries`. Mod-p rank ≤ rational rank keeps B an upper bound. (Note the direction: B is an
  upper bound and K(d) is exact, so S is an upper bound.)

## Validation BEFORE any target (each must pass; these are known answers from the box method, §139–§142)
1. **Null deformation:** a pure coordinate/parameter shift of Kerr (δM or δa). Everything survives: S(d) = K(d) at d = 1–4.
2. **Separable deformation (§139):** Carter survives. S(2) = T(2) + 1 = 5.
3. **Pole-order-1 direction d1 (§140–§141):** Carter dies at d = 2 (S(2) = 4) but Carter² survives at d = 4
   (S(4) ≥ T(4) + 1).
4. **Pole-order-2 direction d3 (§141):** S(2) = 4, and Carter² also dies at d = 4. (The Carter³ survival at d = 6 is
   reproduced only if d = 6 is affordable.)
5. **Sabotage:** a random non-separable deformation. S(d) = T(d) at d = 2, 4.

Controls 3–4 make it a two-method check of the published ladder. The d1 and d3 deformation fields come from the
RESULTS definitions (`_kt_perturb` / `_kt_anatomy`, on the O(χ²) slow-rotation Kerr base used there).

## Target
**Manko–Novikov to first order in the anomalous quadrupole β** (q ∝ β), on the exact Kerr base (the β = 0 MN chart
is Kerr; §151 verified it). This is an exact vacuum perturbation: d/dβ of the verified MN metric at β = 0, with
e^{βZ} → 1 + βZ. It is non-rational through R = √(x² + y² − 1); points are taken with R0 rational, as in §151.
- Parameter points: p1 base (M = 5, a = 3) and p2 base (M = 13, a = 5).
- Jet points: P1 (17/10, 3/5) and P2 (19/9, −1/3), as in §151.
- Valence d = 1–4; 5–6 only if the measured cost allows.

## Predictions (sealed by this commit)
| item | prediction | confidence |
|---|---|---|
| controls 1–5 reproduce | yes | ~75% (a new combined-order implementation) |
| MN-β, d = 2: Carter survives? | NO, S(2) = 4 | ~85% (MN is non-integrable at finite β; Carter is not expected to survive even to first order) |
| MN-β, d = 3: anything beyond trivial (6)? | no, S(3) = 6 | ~85% |
| MN-β, d = 4: does Carter² survive (pole order 1)? | open, no confident prediction: Carter² survives ~40% / dies ~60% | — |

The d = 4 outcome is the scientifically interesting one: a surviving Carter² would mean MN's quadrupole bends Carter
into a rational integral at first order, the §140 mechanism, now ansatz-free.

## Scope of any null or positive
First order in ε only (a statement about the linearised problem); invariant tensors; local near P; valence ≤ 4 (or 6);
two parameter points. Positives go to the Bridge for independent reproduction before any claim.

## Resources (to be requested from the Bridge before any run longer than 30 min)
Matrices at d = 4: about 2× the §151 size (pairs of jets), ~2000 × 1900, seconds each. Even d = 6 is minutes. Estimated
total < 1 h on 1 core, < 1 GB, < 50 MB disk. The build and validation are the main cost (hours of my time, not compute).

## Addendum 1 (2026-11-17, before any build output or run)
Controls 3–4 (d1, d3) live in the double expansion (coupling ε × spin χ², slow-rotation base), not on exact Kerr, so
they need a two-parameter version of the pair test. Staging:
- **Stage 1 (exact Kerr base in the MN chart, β = 0):** controls 1 (null: a pure coordinate change ξ^x = s(x), giving
  δg^{ab} = −L_ξ g^{ab}; everything must survive, S(d) = K(d)); 2 (separable: δg^xx = s(x)·g₀^xx/(x² − 1) with
  s = x³/7; Carter and hence the whole Kerr algebra must survive, S(d) = K(d)); 5 (non-separable sabotage:
  δg^xx = (x y/7)·g₀^xx; S(2) = 4 expected, i.e. Carter dies). After those pass, the MN-β target at d = 1–4.
- **Stage 2 (gate on any CLAIM):** controls 3–4, the ladder reproduction in the double expansion. No MN-β result is
  claimed, and none is sent beyond the Bridge as a finding, until stage 2 passes. The MN-β numbers are recorded as
  they come but labelled "pre-validation".
The predictions are unchanged.
