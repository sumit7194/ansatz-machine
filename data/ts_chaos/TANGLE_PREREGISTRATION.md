# Does the Lyapunov orbit at the TS δ = 2 capture edge have a transverse homoclinic point? Pre-registration, 2026-11-18, BEFORE any build output or run

Ask: Sumit, directly in chat: "go ahead with option C at our capture edge" (SADDLE_REDESIGN_PROPOSAL.md, option C).
Prior work inside the fleet, relayed and not verified here: tabula §199b and the Bridge's V16 found a transverse
splitting at OTHER levels (p = 3/5 with E = 0.94 prograde; p = 4/5 with E = 0.94 prograde, unresolved). Our level
differs (69623bb). Nothing of theirs is read, used, or compared here. Every piece of this is built from our own engine.

## Level (fixed)
- **TS:** p = 4/5 (`ts2:4/5`), E = 97/100, L = 41/8 (σ = 1, retrograde). This is the α level L1 and the saddle-test level;
  its capture-edge window lies on the line p_x = 0 at x0 ∈ [9.912067, 9.945202].
- **Kerr control:** `ts2kerr:4/5`, E = 97/100, L = 2550268/1000000 (separatrix-matched, as in §150).

## Method
Section y = 0 crossed upward (p_y > 0), coordinates (x, p_x); this is the map P on the energy shell H = −1/2.
1. **Symmetries, checked exactly (sympy) before use.** The reduced Hamiltonian is even in (p_x, p_y), since
   (t, φ) → (−t, −φ) is an isometry. If also g(x, −y) = g(x, y), the map is reversible with R(x, p_x) = (x, −p_x).
   Then **W^s = R(W^u)**, and a crossing of W^u with the line p_x = 0 is a symmetric homoclinic point.
2. **Neck:** the saddle x_s of W(x, 0); the neck is open iff −1 − W(x_s, 0) > 0.
3. **Fixed point** of P near (x_s, 0): Newton on P(z) − z = 0, with a DD finite-difference Jacobian. Eigenvalues λ and μ.
4. **Unstable manifold**, outward branch (away from the horizon). Seeds z* + s·v_u for s in the fundamental domain
   [δ, δλ), δ = 1e−12. Iterate k times; find the first crossing of the line p_x = 0 by bisection in s, and the tangent
   t_u there by a finite difference in s.
5. **Splitting angle** between W^u and W^s = R(W^u) at that point: θ = 2·atan(|dx| / |dp_x|), with t_u = (dx, dp_x).
   W^u = W^s requires the tangent to be perpendicular to the line, so dx = 0. θ is coordinate-dependent: it is a
   zero-versus-nonzero test, not a number to compare across projects.
- **Section map engineering:** a new module (`scripts/_ts_tangle.py`), built on the validated DD RHS (`_hp_dd.build_dd_rhs`,
  GBS k = 12). Each crossing is located exactly on y = 0 by a secant search on the final step length. The existing
  lifetime engine records the first step after a crossing, which is not good enough for a map. The initial p_y comes
  from the shell for a general p_x. `_hp_dd.py` itself is not edited.

## Gates (each must pass, in order; a failure stops the run and is reported)
- **G0 structure:** reflection symmetry exact for both metrics; the neck open at both levels; the Newton residual
  ≤ 1e−24; λμ = 1 to ≤ 1e−12 (area preservation); the fixed point on p_x = 0 to ≤ 1e−24 (symmetry). If the neck is
  closed or no fixed point exists, STOP: this level has no Lyapunov orbit and the question is ill-posed there.
- **G1 positive control, same tracing code:** the forced pendulum ẍ = −sin x + ε sin(t), stroboscopic map at phase 0.
  Its reversor is R(x, p) = (−x, p) and its symmetry line is x = 0, where the upper separatrix crosses. Melnikov
  predicts an angle θ ≈ ε·π·sech(π/2)/2 = 0.6260 ε. It must match within 10% at ε = 1e−3 and 3e−3, and give
  θ ≤ 1e−9 at ε = 0. (The integrator is a float64 RK4 at 20,000 steps per period; the code that locates crossings,
  tangents and angles is shared with TS.)
- **G2 negative control, Kerr:** θ_Kerr ≤ 1e−12 at R2, and Carter conserved along W^u (over the iterates used) to
  ≤ 1e−20 relative.
- **G3 precision, TS:** θ_TS at R1 (1e−22) and R2 (1e−28) agree to ≥ 6 significant digits.
- **G4 seed independence, TS:** θ_TS at δ = 1e−12 and 1e−11 agrees to ≥ 6 significant digits.

## Verdict rule
- **TRANSVERSE:** G0–G4 pass, and θ_TS ≥ 1e3·max(θ_Kerr, |θ_TS(R1) − θ_TS(R2)|, |θ_TS(δ) − θ_TS(10δ)|).
  Claim: the neck's Lyapunov orbit at this level has a transverse symmetric homoclinic point. By Smale–Birkhoff that
  gives a horseshoe and hence a chaotic saddle. The plunge boundary on the section, the stable manifold of the neck
  orbit, then accumulates on itself, so the capture edge contains a Cantor set in the N → ∞ limit. **Numerical, not
  rigorous.** The rigorous version would need interval arithmetic (a CAPD-style computer-assisted proof, as an ask to
  quantum).
- **NOT RESOLVED:** gates pass but θ_TS is below the bar. No statement; it is NOT evidence of integrability.
- **VOID:** any gate fails.

## Predictions (sealed by this commit)
| item | prediction | confidence |
|---|---|---|
| G0 neck open with a fixed point found, at both levels | yes | ~80% |
| G1 Melnikov within 10% | yes | ~85% (a new tracer) |
| G2 Kerr zero splitting | yes | ~85% |
| TS verdict TRANSVERSE | yes | ~70% (§150 found chaos at this level; a splitting below resolution is possible) |

## Scope
One level, the first symmetric crossing of the outward branch, and a coordinate angle. It says nothing about other
levels, valences or EMRIs. A null (NOT RESOLVED) does not reverse §150.

## Blinding and resources
- θ_TS, λ_TS and the TS fixed-point location are TS chaos numbers. They are added to tools/EMBARGOES.json before any
  output, then sealed (commit + sha256) and sent to nobody until the Bridge arranges it.
- Expected cost under 30 min on 1 core, < 1 GB, < 10 MB disk, measured first. A slot request goes to the Bridge if a
  measurement exceeds 30 min. nice 10, detached; stop guards as in the saddle test.
