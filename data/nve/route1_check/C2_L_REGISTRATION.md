# C2-L registration: a redrawn lasso with certified clearance, the next mechanism for C2-M. Committed BEFORE any C2-L code
**Office ansatz-machine, 2026-11-28.** GO from the Bridge (re-gate (B)).
**Order (the Bridge):**
1. this registration, committed as drafted;
2. the new code (the Krawczyk sweep, the c-tube cover, the homotopy swept-region check);
3. a NON-AUTHOR READ of that code before any registered run (new certification logic, so the read is required);
4. the measured cost probe on L0_0 (STOP if the projected cover exceeds 3 h);
5. the P2 pilot, once.
P1's own loop design stays a separate design computation, for a later ruling. The C2 time box (2026-12-12) stands.

## Why
C2-M P2 was stopped at the value gate (`C2_M_P2_RESULT.md`). The floats entry's lasso winds once around G2's upper
zero z*(k), but as k moves over P2's ellipse box the zero comes within about 0.014 of the lasso's path. That number is
design guidance (point samples), not a certificate. The refused cells were exactly those with a centre clearance below
about 0.022. The obstruction is CLEARANCE, not analyticity: the winding stays 1 and F is analytic on E_4. A lasso
drawn with uniform clearance from the zero's whole sweep removes the near-singular q on the path, which is what made
CAPD's steps collapse.

## The mechanism
**1. The new lasso L'** (per segment, from the committed geometry rule plus this change):
- the SAME tail as the floats entry's lasso L, from the base point bB to the point where L starts its turn round z*;
- then a circle of radius r_L about z*(k_c), replacing L's tight turn;
- then the same tail back.
- r_L is fixed by the rule before any run: the midpoint of the admissible window [s* + c, d_other - c], where:
  - s* is the radius of the certified enclosure of the zero's sweep over K (item 2);
  - d_other is the certified distance from z*(k_c) to the nearest OTHER singular point's sweep (a G1 zero, the other
    G2 zero, B's zeros, +-ia);
  - c is the clearance (item 3).
  - If the window is empty, there is no L' for that box: refused before any CAPD run.
- At P2 (design guidance): s* is about 0.045 (the sweep over the R-box) and d_other about 0.14 (the G1 zero at about
  1.806), so with c = 0.03 the window is about [0.075, 0.11].

**2. The certified sweep enclosure s*:** an interval Newton/Krawczyk test on G2(z, k) = 0 in z, with k the whole box K
as a ball. G2's z-derivative enclosure comes from c0 and c0' on the z-box x K, obtained as in item 3. The result is a
ball containing z*(k) for EVERY k in K, with uniqueness. The other singular points' sweeps are enclosed the same way:
the G1 zero by Krawczyk, and B's zeros and +-ia in closed form.

**3. The clearance criterion, stated in advance: c = 0.03.**
- That is three times the zero's sweep over an R/20 cell, and above the 0.022 split that separated refused from
  accepted cells.
- **Certified, not sampled:** for every k in K and every z in the CLOSED c-tube about L', G1(z, k) G2(z, k) != 0,
  B(z^2/a^2, k) != 0 and z^2 + a^2 != 0.
- How it is computed: c0 and c0' on the tube come from the path's own enclosure (a CAPD run along L' at the cell, or
  C0's walk) plus Taylor with M |dz|^2/2, where M = C0.sup_box over the tube box x K (k as a ball, which C0 supports);
  f0 is explicit. The tube x K is covered by Arb boxes, refined adaptively.
- A failure refuses the box before any CAPD run.

**4. Homotopy invariance, CERTIFIED (stronger than winding numbers):**
- **Why winding numbers are not enough:** with two or more punctures, pi_1 of the punctured plane is free and
  non-abelian. Two based loops with the same winding number about every puncture can differ by a conjugation, and
  F = tr(M1 M0 M1^-1 M0^-1) - 2 is NOT invariant under conjugating M1 alone. So the draft certifies the homotopy
  itself.
- **The homotopy:** the straight-line deformation L_t = (1 - t) L + t L' (vertex by vertex, after inserting matching
  vertices; the tails coincide, so only the turn region moves). The region it sweeps is the union of the quadrilaterals
  between corresponding edges.
- **The certificate:** that swept region x K is free of every singular point, by the same nonzero test as item 3
  (G1 G2, B, z^2 + a^2).
- **Then:** for every k in K, L' is based-homotopic to L in the plane minus the singular points. M1 is unchanged, so F
  is the SAME function the floats entry defines. The winding numbers (1 about G2+, 0 about everything else) follow and
  are recorded as a check, not as the argument.
- Gamma (M0) is unchanged: its cells completed in C2-M P2, and C2-M's H3 already certifies it per path.

**5. Then C2-M, unchanged:** the 25-cell cover with driver v2 and H1–H4, the refinement rule, M1–M4, the verdict with
v6's full controls, and the engine gate (C2_M_REGISTRATION.md, C2-M-1, C2-M-2). The bars and cost bar stay the same,
everything counted, including the new certificates in items 2–4.

## The test, once
- **Cost probe first (measured, not assumed):** the worst P2 cell from the stopped run, L0_0 (k = 4.065 - 0.085i),
  with L'. Record its CAPD time and acceptance, and the time of the item 2–4 certificates.
- **The bar:** the projected P2 cover (25 x the probe time / 2 cores, plus the certificates) <= 3 h, or STOP before
  the pilot.
- **The P2 pilot re-run** as the test: `c2m_pilot.sh P2` with the L' floats entry. Graded "new mechanism (C2-L) after
  C2-M P2 was stopped at the value gate". The archived partial cover is not reused.

## P1 (the circle)
P1 does NOT get a route from this alone; it needs its own loop design.
- Its failure mode differed. CAPD at P1 failed on the CIRCLE (loop 0), where c0's width accumulated round the loop and
  met a small G2 near the base point. The C2-TM failure there was on the lasso remainder.
- The same certified-tube criterion can be applied to a re-chosen circle radius and P1's lasso. But the circle's radius
  is constrained: it must enclose all of c0's branch points (the v7 precondition, R0 - 0.1), and whether a radius with
  uniform clearance from every G zero's sweep exists is unknown.
- **Proposal:** a design computation first (the window for the circle radius and for P1's lasso, as in item 1), and
  only if it is non-empty, a P1 cost probe. A separate ruling.

## Predictions (to be recorded at registration)
- The window is non-empty at P2: 80%.
- The certificates (items 2–4) pass at P2: 65%.
- The L0_0 probe cell is accepted: 60%.
- The P2 cover is within the cost bar: 40%.
- P2 certifies: 30%.

## Erratum E1 (2026-11-28; committed before any C2-L code): the lasso encloses TWO points, so the new loop is a two-disc hull, not a circle
**Found before coding** (exact polygon winding numbers at k_c = 83/20, floats entry 83/20). The floats lasso winds
**1 about BOTH G1's zero r+ (about 1.8060) AND G2's upper zero p+ (about 1.8143 + 0.1425i)**, and 0 about G2's lower zero
p- and every c0 singularity (B's zeros, +-ia). This is the region-B rule's "capsule lasso around [r+, p+]". Gamma winds 1
about all three G zeros.

The registered item 1 (a circle of radius r_L about z*(k_c) replacing the turn) would therefore have LEFT r+ OUT. That
changes the homotopy class, and so F. It is withdrawn.

**Item 1, amended: the new lasso L'.**
- The same tail as L from bB up to the hull; then the boundary of the CONVEX HULL of two closed discs, D(r+(k_c), rho_r)
  and D(p+(k_c), rho_p), traversed in L's orientation; then the tail back.
- The radii are fixed by the rule before any run, from the CERTIFIED sweep enclosures (item 2):
  - rho_p = s(p+) + c + c/2, where s(.) is the sweep enclosure's radius about the k_c position;
  - rho_r = the midpoint of [s(r+) + c, d(r+, p-) - s(p-) - c], where d(r+, p-) is the certified distance from r+(k_c)
    to p-(k_c).
- If any window is empty, there is no L' for that box: refused before any CAPD run.
- **Design guidance at P2 (point samples, not certified):** s(p+) and s(p-) are about 0.045 over the R-box, s(r+) is
  about 0.003, and d(r+, p-) is about 0.143. With c = 0.03 that gives rho_p of about 0.09, rho_r in [0.033, 0.068]
  (midpoint about 0.05), and a clearance from p-'s sweep of about 0.047.

**Item 2, amended:** Krawczyk sweep enclosures for r+ (a zero of G1), p+ and p- (zeros of G2), with k over K as cells.

**Items 3 and 4 unchanged in kind:**
- the c-tube about L', and the straight-line homotopy L -> L' with its swept region, are certified free of every
  singular point for every k in K (G1 G2, B, z^2 + a^2 nonzero);
- the swept region now lies between L's capsule and the wider hull. It must contain neither r+ nor p+ (both stay inside
  both loops) nor p-.
- The recorded windings, as a check, are **1 about r+ and p+, and 0 about p- and the rest**.

**Item 4's phrase "1 about G2+, 0 about everything else" is corrected accordingly.**
