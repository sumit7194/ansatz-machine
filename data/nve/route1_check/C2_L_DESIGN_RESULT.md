# C2-L at P2: REFUSED at the design stage. The registered window for rho_r is empty (2026-11-28)

**Under the registered rule (erratum E1, item 1), there is no L' for the P2 box. It is refused before any CAPD run.**
No cost probe and no P2 pilot follow from this registration. A different K or a different c would be a new mechanism,
and that needs a ruling.

Record: `c2/c2l_P2_design.json`. Code: `scripts/_nve_c2l.py`, stage `design`. Its content hash is in the record.
Wall time was 50 s.

## What was computed
- **Certified sweep enclosures.** Krawczyk enclosures of r+ (G1), p+ and p- (G2) were computed over the C2-M cover's k-square K. K is the 25 kbox cells about k_c = 83/20, with half-side R = HALF (4 + 1/4)/2.
  - Cells were refined into quarters where Krawczyk failed. That gave 322 leaf cells across three levels.
  - Each box holds exactly one zero for every k in its cell.
- **s(.)** is the maximum over the cells of |box − zero(k_c)|, as an upper bound:
  - s(r+) = 0.0057;
  - s(p+) = s(p-) = 0.0797.
- **d(r+, p-) = 0.1428.**
- **The window** is [s(r+) + c, d(r+, p-) − s(p-) − c] = [0.0357, 0.0331], with c = 0.03. **It is empty.**

## Is the emptiness an artefact of the enclosure? No.
A design check used float Newton at point k on 100 points of K's boundary. |zero(k) − zero(k_c)| is the modulus of a holomorphic function, so its maximum is on the boundary.
- The true supremum of p-'s displacement is **0.0760**, at the corner k_c + R + Ri. The enclosure over-estimates it by 0.0037.
- With the true value, the window would be [0.0355, 0.0368]: non-empty by 0.0013 at best.
- So even a perfect enclosure leaves essentially no room. A disc whose clearance from p-'s sweep is c plus half a thousandth is not a design worth certifying.

## Why the design guidance was wrong
The registration's guidance put s(p±) at about 0.045 over "the R-box". That came from point samples that did not reach K's corners.
- Over E_4 alone, the true sweep of p± is **0.0596** (16 points on E_4's boundary).
- Over the square K, it is 0.0760.
- K's corners lie outside E_4, but the C2-M cover uses the square.

## The registered predictions
"The window is non-empty at P2: 80%": **failed.** The later predictions (the certificates, the L0_0 probe, the cover cost, P2 certifying) are not reached.

## What would change it (each a new mechanism, for a ruling; none is run)
- **(i) K = E_4 rather than the square.** The C2-M cover would cover only E_4, with the corner cells refined and the sub-cells wholly outside E_4 dropped. ATAP needs F only on E_4.
  - With the E_4 sweep (point value 0.0596), the window is about [0.034, 0.053].
  - This changes C2-M's cover as well as C2-L.
- **(ii) A smaller c.** c = 0.03 was registered as three R/20 sweeps and above the 0.022 split. Choosing it now, after seeing the window, is a post-hoc change.
- **(iii) A smaller box** than P2's R. The window opens as the sweep shrinks.

## Development notes (the code is unread; a non-author read is still required before any registered run)
The cell field over a k-ball was rebuilt during development. Each change was made because a dev test showed the earlier form vacuous or unable to contract.
1. A walk with k as a ball was vacuous, about 1e16. Arb's series recurrence over-estimates exponentially with a ball parameter, and its integrator cannot meet a tolerance.
2. It was replaced by a Taylor model in k. The point walk at the centre carries dc/dk (deriv=True) and keeps the carried branch. A certified bound on the second k-derivative comes from a rectangle rule at the base plus sup |c0_kk''| over the working square.
3. z-boxes now use a second-order Taylor with the exact c0''. The branch for the k-ball is the ratio sqrt(B_K/B_c), certified in the right half-plane.
4. f0 and f0' now use centred forms. Naive evaluation of the rational functions alone stopped Krawczyk contracting: the factor was 0.75 at radius 0.01, now 0.22.
5. After the first strict inclusion, Krawczyk iterates by intersection. Requiring strict inclusion again fails at the fixed point, whose width is the zero's own sweep.

A refusal cannot be a false certificate. The decisive number is 0.0760, and it is reproduced by an independent float computation.
