# What a rigorous one-way-gate statement would need (2026-11-19; note only, nothing run)

**The statement.** At TS p = 4/5, E = 97/100, L = 41/8, on the section Σ = {y = 0, p_y > 0}, with
D = the region bounded by U (W^u_out from z\* to h) and R(U):
- **(L2)** P is defined and continuous on cl(D);
- **(L3)** every z ∈ cl(D) with P(z) ∉ cl(D) has a forward orbit that reaches x < x_pl and never meets D again.

The §157 reasoning then gives, rigorously, "every fate boundary inside D lies on W^s(γ)". With a rigorous A2 and
§154's transversality, it gives a Cantor set of edge points.

**What has to be enclosed.**
1. **γ:** an interval-Newton or Krawczyk enclosure of z\* = P(z\*), and an isolating block N around it with cone
   conditions (rigorous hyperbolicity). Inside N, exits are classified by the cones: outward along W^u_out (stays in
   D) or inward along W^u_in. This handles the infinitely many thin lobes that accumulate on z\*, which no finite box
   cover can.
2. **∂D:** a validated tube around U, from a parameterisation-method enclosure of the local unstable manifold in N,
   propagated through the ~8 to 9 iterates to h. R(U) follows exactly from the reversor. The transversality at h is the
   §154 statement, rigorous only with a CAPD-type proof (quantum's route).
3. **L2:** over a box cover of cl(D) \ N, interval enclosures of the first return. They must show the return time is
   finite and bounded, and the crossing is transverse (p_y ≥ c > 0 on every enclosure). Injectivity is then automatic,
   because P is the restriction of a flow map.
4. **L3:** for each box B in the cover, enclose P(B). If P(B) ⊂ int D it is done. If not, integrate the escaping part
   forward rigorously until it is certified to reach x < x_pl, with a proof that it misses D on every intermediate
   crossing. Near N, use the cone classification instead, plus a rigorous A2: enclose one fundamental domain of
   W^u_in and integrate it to x < x_pl.

**Tools and cost.**
- The RHS is rational (the TS metric is rational at p = 4/5), so interval evaluation is exact in form. CAPD's
  C¹-Lohner integrator, or an Arb Taylor integrator (FLINT/Arb 3.6 is on the box), is suitable.
- D spans x ≈ 9.8 to 57 and |p_x| ≲ 0.75. The lobes are thin (§154's angle is small), so expect ~10⁵ to 10⁶ boxes
  with refinement along ∂D. Each box needs one rigorous return.
- Embarrassingly parallel. Likely days of compute plus weeks of build. Only L3 needs finite-time integration beyond
  one return.

**What it would NOT give:** anything at other (E, L); anything about α or finite-horizon statistics; anything about
EMRI orbits. It is rigorous for the truncated geodesic problem at this level only.
