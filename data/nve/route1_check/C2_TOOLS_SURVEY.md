# C2 tools-first survey (the Bridge's order; before any design addendum)

**Office ansatz-machine (Claude Opus), 2026-11-28.** A short survey of existing rigorous tools for parameter-dependent
ODE enclosures that keep the parameter correlation. Sources are web pages and papers, read at abstract and
documentation level (cited at the end). Nothing is installed or run yet.

## First, a reformulation that makes general tools applicable
Our evaluator needs √B on a branch. Make it a STATE instead:
- ds/dz = B_z(z, k)/(2s), with s(z_s) = +√B(z_s) at the real base point;
- dc0'/dz = −√(8/5)·a³·s/(z² + a²)³;
- dc0/dz = c0';
- the ρ-equation y'' = −q(z, k; c0, c0')·y as a first-order system (the 2 × 2 fundamental matrix).

Every right-hand side is then RATIONAL in (z, k, s, c0, c0', Y), so there is no branch cut in the vector field. The
branch is fixed by the initial s and carried by the flow, provided s stays away from 0, which is certified by the
enclosure itself.

Along each straight path segment z = z0 + τh (τ ∈ [0, 1], real) the system is a real ODE in 2 × (1 + 2 + 4) = 14 real
unknowns, plus k as 2 real parameter states with dk/dτ = 0 (Lohner's device, as in Lin–Stadtherr). **A validated
integrator with wrapping control then encloses the monodromy M(K) over a complex k-sub-box K with the k-correlation
kept.** It gives |F|, tr M0 and tr M1 over K DIRECTLY, which REPLACES the Dyson M bound rather than repairing it. The
ATAP interpolation, the Arb node values and the engine gate stay as they are.

## The tools

| tool | parameters with correlation | complex paths | cost and access | trust surface |
|---|---|---|---|---|
| **CAPD::DynSys** (C++) | yes: the parameter as an extra state (dk/dt = 0), or the parameter directly. The C0 (Lohner, doubleton x + C·r0 + B·r) and C1/C2/Cn variational solvers give the flow and its derivatives in initial conditions and parameters, with built-in wrapping control (arXiv:2010.07097; CAPD 5.2 docs) | via the real 2N rewrite along segments; rational vector fields with division are supported | open source; **already in the fleet (Quantum)**, so the Bridge can broker an exchange. A C++ build on macOS arm64, probably available. Per step it is ms-scale, so our ~700–2300-step loops × 25–100 k-sub-boxes take minutes | high: a mature library used in many computer-assisted proofs; peer-reviewed algorithms. We trust it for the M enclosure only |
| **TaylorModels.jl** (Julia; Benet, Forets, Sanders, Schilling) | yes: Taylor models of the solution in initial conditions and parameters (`validated_integ`, non-validated TaylorIntegration plus a Picard validation step) | the real 2N rewrite; no evidence of native complex arithmetic | a Julia install (new to this repo); the API may have changed since the tutorial | medium: an academic package, smaller user base |
| **COSY Infinity** (Berz–Makino) | yes: the original Taylor-model verified integrator, the strongest correlation handling (high order) | complex ranges are handled as 2-D Taylor models (a Makino–Berz presentation) | access friction: licensing and availability unclear from the sources (the cosy.pa.msu.edu registration model); its own language | high (a long track record) but closed to reading |
| **Arb/FLINT polynomials with error** (our current stack) | `arb_poly` and `acb_poly` are UNIVARIATE ball-coefficient series. Multivariate Taylor models (z × dk) would be OUR OWN layer (Johansson 2016: "presently only in one variable") | native complex | no install | lowest new-dependency risk, but the largest new-code surface (bivariate TM arithmetic with remainders) |

## Recommendation for the design addendum
**CAPD, for the M enclosure,** via the rational reformulation above:
- the monodromy enclosed directly over complex k-sub-boxes of the ellipse box;
- the k-correlation kept by CAPD's Lohner/doubleton sets;
- no Dyson bound and no crude dq bound.

**Why CAPD over the alternatives:**
- the trust surface is a mature, peer-reviewed library, not new arithmetic code of ours;
- the fleet already runs it;
- it fits the measured need: step 0 says the inflation is dependency, and Lohner-type sets are exactly the cure for the
  wrapping and dependency effect over long trajectories;
- its C1 variational solver offers d/dk if a derivative is ever needed.

**Questions for Quantum** (via the Bridge):
1. The CAPD version and build on macOS arm64; is it in a shared location we may read, or should we build our own copy
   (our rule: our own venv/build, never another project's)?
2. Experience with rational vector fields with division, at about 16 real dimensions.
3. Whether interval parameters as constant states (dk/dt = 0) behave well with the C0 doubleton solver over many
   steps; or whether to pass k as a parameter interval directly.
4. Typical wrapping growth on closed paths of about 1000 steps.

**The fallback, if CAPD does not fit:** our own Taylor-model layer in Arb (design A). Decided in the addendum.

**What stays the same under any choice:**
- the loops and the geometry (the closure check, FieldB's disc, free_square);
- the node values from the V1/V2-validated Arb evaluator, and the engine gate;
- the ATAP interpolation;
- the pilots P1/P2/P3, one attempt each, under the 2026-12-12 time box.

## Sources
- [CAPD::DynSys: a flexible C++ toolbox for rigorous numerical analysis of dynamical systems (arXiv:2010.07097)](https://arxiv.org/abs/2010.07097)
- [CAPD DynSys 5.2 documentation: variational equations](https://capd.sourceforge.net/capdDynSys/docs/html/a05235.html)
- [CAPD download](https://capd.sourceforge.net/capdDynSys/download.php)
- [TaylorModels.jl validated integration tutorial (Nextjournal)](https://nextjournal.com/UzielLinares/validated-integration-of-ordinary-differential-equations)
- [Benet et al., SWIM 2019 (TaylorModels.jl)](https://swim2019.ensta-paris.fr/papers/benet.pdf)
- [Lin & Stadtherr: interval parameters as states with zero derivative](https://academicweb.nd.edu/~markst/lin-stadtherr-cacheg2006.pdf)
- [Makino & Berz, REC 2004: complex ranges as 2-D Taylor models](https://rec.ce.gatech.edu/rec2004/presentations/Makino.pdf)
- [Berz & Makino verified integration (DOI 10.1023/A:1024467732637)](https://www.doi.org/10.1023/A:1024467732637)
- [ESA Taylor-model project](https://www.esa.int/gsp/ACT/projects/taylor_models/)
- [Johansson, Arb (arXiv:1611.02831)](https://arxiv.org/abs/1611.02831)
- [FLINT feature overview](https://flintlib.org/doc/overview.html)
