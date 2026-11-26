# Pilot P1: result against the seal (2026-11-26, Air)

[ansatz-machine-personal. Seal: `P1_SEAL.md`, dfa8d48, committed before the run. Ran as `air/p1.sh` on the MacBook Air
under `.venv313` (Homebrew Python 3.13.18, python-flint 0.9.0, mpmath 1.3.0, sympy 1.14.0, numpy 2.5.0), nice 15,
pause-only guard (never paused), 17:04:02 to 17:20:24, rc 0. The node file was new ("0 records already on disk"), and
`p1.sh` refuses to start if it exists. The 46 manifest files were unchanged afterwards. Outputs are in `air_p1/`.]

| quantity | sealed prediction | measured | |
|---|---|---|---|
| verdict | CERTIFIED, P = 97% | **CERTIFIED** | hit |
| \|F\| ≥ | 0.26500 to 0.26508 | 0.265039275 | hit |
| \|tr M0\| ≥ | 1.9931584 (7 dp) | 1.993158417 | hit |
| \|Im tr M1\| ≥ | 2.6488208 or 2.6488209 (7 dp) | 2.648820879 | hit (2.6488208 truncated, …09 rounded) |
| planted zero | refused | refused | hit |
| held-out points | \|p − f\| ≤ 1e−6 for F | ≤ 7.0e−8 (F), ≤ 5.4e−11, ≤ 7.1e−11 (traces) | hit |
| proved M ≥ sampled on the ρ = 6.5 ellipse | true, F overestimated 1e5 to 1e7 | true, ×5.7e6 (traces ×1.3, ×1.1e2) | hit |
| engine end values (k = 1, 11/10) inside the node enclosures | true | true, true | hit |
| shrunken M (÷1e12) below the sampled maximum | F yes; tr M1 yes; tr M0 possibly not | below for F, tr M0 and tr M1 | hit; the tr M0 hedge resolved to "below" |
| wall time | 10–20 min | 16.4 min (24 evaluations at 40–42 s) | hit |

**All ten sealed items hit.** The 3% doubt (an evaluator failure on the widest ellipse) did not happen: all 8 ellipse
points at ρ = 6.5 evaluated, with F radii 1.3e−9 to 1.5e−9.

**What this establishes:** the v4 spin-3/5 row ρ = 6.5 certifies [1, 1.1] at its own n = 12. The equal-n run had
needed n = 24 at ρ = 4 (|F| ≥ 0.265334372 there; the n = 12 bound is lower because its error bound is larger). At
spin 3/5, v4's smaller constants halve the node count for this segment, which feeds the P1–P3 cost redo.
