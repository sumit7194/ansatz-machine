# RESULT: probe (a), where the Laurent bound stops between k = 3 and 3.9

**ansatz-machine-personal (Claude Opus), 2026-11-26.** Seal: `PROBE_A_SEAL.md`, with the script
`scripts/_nve_route1_laurent_probe.py` and the runner `air/probea.sh`, all committed at d5fa60e before the run. It
ran on the Air from 23:37:08 to 23:37:38, rc 0, with `.venv313` (Python 3.13.18, python-flint 0.9.0, prec 256) at nice
15 under `job.sh`. Before launch, the sha256 of the probe, the runner and v2 matched on both machines. Logs are in
`air_probea/`.

**Environment:** as above. v2 (`_nve_route1_segment_v2.py`) was unchanged; its sha256 matched the Mac mini's copy.

## What it found

**The derivative bound V.laurent(k, deriv=True) passes through k = 3.7 and fails from k = 3.8, at both spins.** The
plain bound passes at every k tested, 3.9 included. The arc-by-arc diagnostic is **identical** at spins 3/5 and 9/10.
Only M differs, by the spin's prefactor, since 1 − kφ on |x| = 0.81 does not depend on the spin.

| k | 3.0 | 3.1 | 3.2 | 3.3 | 3.4 | 3.5 | 3.6 | 3.7 | **3.8** | 3.85 | 3.9 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| derivative bound | pass | pass | pass | pass | pass | pass | pass | pass | **FAIL** | FAIL | FAIL |
| arcs non-finite (of 400) | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 84 | 112 | 140 |
| arcs whose 1 − kφ ball is on the branch cut | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | **0** | 8 | 36 |
| M (deriv), spin 3/5 | 2.91E+3 | 3.09E+3 | 3.30E+3 | 3.57E+3 | 3.91E+3 | 4.36E+3 | 4.99E+3 | 6.00E+3 | — | — | — |

**The cause is (iii), the square root's own enclosure.** At k = 3.8, on a failing arc (arc 45):
- the ball of 1 − kφ is 0.024 + 0.117i ± 0.056. Its distance from 0 is 0.119, so it does **not** contain 0, and it does
  not touch the branch cut;
- `acb.sqrt` of that ball returns |s| 0.228 ± 0.228, a ball that reaches 0;
- the derivative's division by s is then non-finite.

Every failing arc at 3.8 is like this: s contains 0, and 1 − kφ contains neither 0 nor any of the cut. The branch cut
plays a part only from 3.85 upward (8 arcs, then 36 at 3.9).

**The second finding: Arb's balls are much wider than my model.** The ball radius of 1 − kφ is 0.027 to 0.057 at the
worst arcs, 10 to 40 times my first-order estimate (0.001 to 0.008). The seal had allowed for 2.7×, from the k = 1/2
smoke test. The excess comes from evaluating φ on a whole arc ball, a box from exp(iθ) over θ ± π/400 through a
rational expression, with no centred form. **So the arcs, not the closeness of 1 − kφ to zero, are what set the stop.**
min |1 − kφ| is still about 0.04 at k = 3.8.

## Against the seal

| sealed prediction | P | measured | |
|---|---|---|---|
| k = 3, both spins: plain and derivative pass | 99% | pass, pass | hit |
| k = 3.9: plain passes, derivative fails | 98% | yes, at both spins | hit |
| every derivative bound at 3.1 … 3.8 passes | 70% | **3.8 fails** | **miss** |
| if any fails, the first failure is at k ≥ 3.7 | 90% | first failure at 3.8 | hit |
| k = 3.85: the derivative bound passes | 50% | **fails** | **miss** |
| the pass/fail pattern is identical at both spins | 90% | identical, arc for arc | hit |
| at 3.9 the failing arcs have s containing 0 | 90% | all 140 | hit |
| why: (i) branch cut 40%, (ii) 1 − kφ contains 0 35%, (iii) sqrt inflation 25% | — | **(iii)** at 3.8. At 3.9, 36 of 140 failing arcs also meet the cut, and none contains 0 | (iii); my most likely cause was wrong |
| wall time under 2 min per spin | 90% | about 2 s per spin | hit |

## What it changes

- **The spin-independent stop for segment centres, with the current code, is in (3.7, 3.8).** It no longer sits
  somewhere between 3 and 3.9. A 0.1-wide segment centred at 3.7 can at least build its Laurent data. Whether its
  ρ = 4 row then passes the precondition and the walks is not tested.
- **Above about 3.75, every spin needs C2.** That is the top of region A: 3.85 at 9/10, and about 4 at the other spins.
- **C2's design is now specific.** The failure is enclosure width, so either of these is enough:
  - smaller arcs (fixed or adaptive) wherever s comes out containing 0;
  - a centred evaluation of φ on each arc.

  A branch-aware square root is **not** needed below about 3.85. Refining only the arcs that fail keeps every number
  below the stop bit-identical. Above 3.85 the cut also enters, and the ρ = 4 precondition fails near 3.9 regardless
  (registration §4.1).
- **Correction recorded.** The seal addendum's "an arc's ball evidently contains 0" was wrong in detail. 1 − kφ's ball
  does not contain 0; s's ball does. The P3_RESULT addendum had already marked that statement as unestablished.
