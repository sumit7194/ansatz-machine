# RESULT: pilot P3, the proof-stage constants as k grows (spins 3/5 and 9/10)

**ansatz-machine-personal (Claude Opus), 2026-11-26.** Seal: `P3_SEAL.md`, with its addendum. Runners `air/p3.sh`
(floats at both spins, then 3/5 at k_c = 1/2, 2, 3, 39/10) and `air/p3c.sh` (the continuation, which skips only 3/5 at
39/10). Outputs were copied from the Air into `air_p3/` and are committed unchanged: the floats JSONs, the rows, the
proof JSONs, the dq checkpoints and the logs.

**Environment:** MacBook Air on the loaded fleet, one process, nice 15, pause-only guard (`job.sh` v2; the guard never
paused it). Floats ran on `.venv`: Python 3.14.10, python-flint 0.9.0, mpmath 1.3.0. The proof ran on `.venv313`:
Python 3.13.18, python-flint 0.9.0, prec 256 bits. Code: v5.1 as committed at b64a43c, code hash as printed in every
log header, unchanged. p3.sh ran 20:18:45 to 20:51:58 (rc 1). p3c.sh ran 20:57:10 to 23:20:02 (rc 1). Peak RSS was
32 to 49 MB.

**P3 measures how the constants grow with k. It certifies nothing**, since the verdict stage was not run.

**Two of the eight stages produced no row, for two different reasons, and neither reason is one the seal named.**
3/5 at k_c = 39/10 is in the seal's addendum. 9/10 at k_c = 3 is new and is described below. Neither issued a row or a
certificate, and neither wrote a rows file.

## The rows (ρ = 4, half-width 1/20, constants per unit k)

| spin | k_c | c0 (circle) | c1 (lasso) | n | M_F ≤ | precondition max\|w\| (Arb) | walks (circle / lasso) | prove |
|---|---|---|---|---|---|---|---|---|
| 3/5 | 1/2 | 0.900 | 14.033 | 14 | 1.527E+4 | 0.452 | 2,165 / 717 | 482 s |
| 3/5 | 2 | 1.361 | 22.192 | 14 | 1.156E+5 | 0.579 | 2,161 / 673 | 474 s |
| 3/5 | 3 | 3.997 | 57.057 | 20 | 4.297E+8 | 0.798 | 2,164 / 636 | 472 s |
| 3/5 | 39/10 | **no row**: `RuntimeError` in the Laurent derivative bound (seal addendum) | | | | | | |
| 9/10 | 1/2 | 6.479 | 34.337 | 16 | 2.972E+6 | 0.452 | 19,809 / 906 | 3,455 s |
| 9/10 | 2 | 10.960 | 60.793 | 22 | 2.660E+9 | 0.579 | 15,624 / 867 | 2,760 s |
| 9/10 | 3 | **no row**: `OverflowError` converting M_F to a float (below) | | | | | 13,535 / 822 | crashed at about 39 min |
| 9/10 | 39/10 | **no row**: the same Laurent `RuntimeError` as 3/5 (run alone afterwards, `air/p3d.sh`) | | | | | | 30 s |

- **The precondition maxima are the same at both spins** (0.452, 0.579), as they must be, since the Laurent disc
  depends on x = a²ω² only.
- **K-point z-direction control (circle / lasso).** At 3/5: 0.361 / 8.99, 0.470 / 10.10 and 0.590 / 12.78. At 9/10:
  2.230 / 20.40, 0.752 / 25.02 and 1.132 / 30.79 (that last one at k_c = 3, before the crash).
- **F1 never fired.** That includes 9/10 at k_c = 3, whose walks and both dq lists finished (104,934 F1 step checks in
  the walks alone).
- **Floats.** 3/5 took 55 to 57 s per k_c and about 3.8 min in all. 9/10 took 75 to 79 s per k_c and about 5.1 min in
  all. geometry_ok was True everywhere.

## What happened at 9/10, k_c = 3

The stage ran the self-test, both reference walks, the K-point control and both dq lists over the ρ = 4 k-square, and
wrote the dq checkpoint (73 records). It then crashed in `row_for` at the line computing n:

    n = max(2, math.ceil(math.log(4 * float(MF) / ((rho - 1) * V.TOL_F)) / math.log(rho)))
    OverflowError: cannot convert float infinity to integer

**M_F was a finite Arb ball, but larger than the largest float (about 1.8E+308), so `float(MF)` returned infinity.**
`dyson_sum` asserts a finite result, and the gauge is a float choice with det C ≈ 1, so the size comes from I0 and I1.
It does not come from a non-finite enclosure.

**What the checkpoint shows (read from the dq file, not from a row):**
- **On the circle the dq bounds exploded.** Their sum over the walk rose from 1.656E+4 at k_c = 2 to 3.669E+8 at
  k_c = 3, a factor of about 22,000. The largest single step bound rose from 954 to 1.08E+6. The median rose from 1.06
  to 532.
- **The lasso side grew only about 4×,** from a sum of 2.01E+4 to 8.26E+4.
- **The blow-up is concentrated.** About 95% of the circle sum comes from 2,066 of 13,535 steps, in a few arcs placed
  symmetrically under conjugation. The middle of the walk stays below about 120.
- **Many more steps fell back to the crude bound.** 1,760 steps kept it, against 9 at k_c = 2.
- **At the centre point it does not happen.** The K-point control on the same circle is 1.132 at k_c = 3, against
  0.752 at k_c = 2.

**The blow-up appears only when k ranges over the complex k-square** (half-side R = 0.10625), not at k_c itself.

**Rough size (an estimate, not a measurement).** If I0 had scaled with the dq sum from k_c = 2, c0 would be about
2E+5 per unit k and I0 = R·c0 about 2E+4. M_F contains e^(2·I0), far beyond the float range. Overflow needs I0 + I1 above
about 354, so even an I0 about fifty times smaller would still overflow (a hundred times smaller would not, by
itself).

**What I have not established.** I have not located where in z those arcs sit, or which singular point produces them.
The four singular points in the floats file stay at least 0.36 outside the circle |z| = 1.2639 at k_c = 3 for real k.
The working hypothesis is that a singular point of q (a zero of G1 or G2) comes close to the walk's step boxes for
**complex** k about 0.1 from 3. A dq/dk bound that grows about 10⁴× across a box of half-side 0.106 suggests a
singularity in k only slightly outside the box. That is a hypothesis, not a diagnosis.

**Two separate findings, kept apart:**
1. **A method limit at 9/10.** With ρ = 4 and half-width 1/20, the walk-side constants at 9/10 run away between k_c = 2
   and 3. At 3/5 the same settings reach k_c = 3 and stop between 3 and 3.9, on a different, spin-independent mechanism
   (the Laurent arcs). **So the method's reach depends on the spin, and at 9/10 it stops earlier.** This mechanism is
   spin-dependent, unlike the Laurent one.
2. **A fail-closed gap in the code.** A runaway M_F should give a rejected row. Instead it gives an uncaught exception
   that ends the runner. That is not unsound: no row and no certificate were written, and the dq checkpoint holds only
   rigorous bounds. But the runner stopped, so 9/10 at 39/10 never ran. Production would meet the same crash. A fix
   (compute n in Arb, or reject a row whose n exceeds a stated cap) is a code change and needs its own read and a
   T1–T4 rerun.

## Against the seal

| sealed prediction | measured | |
|---|---|---|
| ρ = 4 row admitted at 1/2, both spins (P = 95%) | admitted, admitted | hit |
| ρ = 4 row admitted at 2, both spins (P = 90%) | admitted, admitted | hit |
| ρ = 4 row admitted at 3, both spins (P = 85%) | 3/5 admitted; **9/10 no row (crash)** | **miss at 9/10** |
| 39/10 rejected, "precondition not certified" (P = 95%) | 3/5: no row, but from the Laurent `RuntimeError`, before the precondition; 9/10: not run | no row as predicted, **wrong mechanism**; 9/10 untested |
| 3/5 at 1/2: c0 0.6–1.2, c1 9–17, n 12–14 | 0.900, 14.03, 14 | hit, hit, hit |
| 3/5 at 2: c0 1.0–2.5, c1 16–30, n 14–16 | 1.361, 22.19, 14 | hit, hit, hit |
| 3/5 at 3: c0 1.5–4, c1 20–45, n 14–18 | 3.997, **57.06**, **20** | hit (at the edge), **miss**, **miss** |
| 9/10 at 1/2: c0 4–9, c1 25–45, n 16–18 | 6.479, 34.34, 16 | hit, hit, hit |
| 9/10 at 2: c0 8–20, c1 45–90, n 18–24 | 10.96, 60.79, 22 | hit, hit, hit |
| 9/10 at 3: c0 10–30, c1 55–120, n 20–30 | no row | **not measured (miss of the row itself, above)** |
| F1 does not fire at 1/2, 2, 3 (P = 97%, 95%, 90%) | did not fire at either spin, 9/10 at 3 included | hit |
| F1 does not fire in the walks at 39/10 (P = 85%) | 3/5 stopped before the walks; 9/10 not run | untested |
| c1 increases with k, 1/2 < 21/20 < 2 < 3 (P = 80%) | 3/5: 14.03 < 15.8 < 22.19 < 57.06; 9/10: 34.34 < 40.3 < 60.79, k = 3 not measured | holds where measured |
| ratio c1(3)/c1(21/20) in 1.3–3 (same P = 80%) | 3/5: **57.06/15.8 = 3.6**; 9/10: not measured | **miss at 3/5** |
| wall time 3/5: 8–20 min per k_c | 8.0, **7.9**, **7.9** min | hit, miss (just below), miss (just below) |
| wall time 9/10: 30–70 min per k_c | 57.6, 46.0 min; k_c = 3 crashed at about 39 min | hit, hit, — |
| floats under 2 min (3/5), under 10 min (9/10) | **3.8 min**, 5.1 min | **miss**, hit |
| addendum: 9/10 at 39/10 stops with the same Laurent `RuntimeError` (P = 95%) | the same `RuntimeError`, same line (run alone, `air/p3d.sh`; see below) | **hit** |
| addendum: 9/10 at 3 has c1 ≥ 120 (P = 60%) | no row | **unresolved** (the lasso dq sum rose 4.1× from k_c = 2, which would put c1 near 250 if the gauge weights scaled alike; that is an estimate, not a measurement) |

**The surprises the seal named:** none happened. No row was admitted at 3.9, c1 did not decrease anywhere, and F1 did
not fire. **What happened instead and was not named:** two crashes, each from a mechanism the seal did not list.

## The misses, plainly

1. **At k_c = 3 the 3/5 constants grew faster than sealed.** c1 was 57.1 against a top of 45, n was 20 against a top of
   18, and the ratio c1(3)/c1(21/20) was 3.6 against 1.3–3. I took v2's crude constants, which doubled, as the guide.
   Growth to k = 3 is steeper than that.
2. **9/10 at k_c = 3 produced no row.** The circle-side dq bound over the complex k-square ran away, and the code
   crashed rather than rejecting the row.
3. **3/5 at 39/10 stopped on the Laurent arc bound, not the precondition.** That is recorded in the seal addendum.
4. **Wall times at 3/5 came in just under 8 min for two stages, and the 3/5 floats took 3.8 min, not under 2.** These
   are timing misses and do not affect the constants.

## Where the method stops, as measured (ρ = 4, half-width 1/20, fixed 400 Laurent arcs)

- **Spin 3/5:** it works through k_c = 3 and stops before 3.9, on the Laurent arcs, where min |1 − kφ| ≈ 0.02 on
  |x| = 0.81. That limit does not depend on the spin.
- **Spin 9/10:** it works through k_c = 2 and stops before 3, on the walk-side dq bound over the complex k-square.
  That limit does depend on the spin.
- **Region A runs to about k ≈ 4 (LIMZ).** With these settings, the top of it is out of reach at both spins, and at
  9/10 the gap starts lower. **Neither stop says where the last certifiable segment ends.** A smaller k-square (lower
  ρ or a narrower segment) or adaptive Laurent arcs might reach further. Each of those changes is untested and needs
  its own seal, and adaptive arcs also need a code read and a T1–T4 rerun.

## Addendum: spin 9/10 at k_c = 39/10, run alone (2026-11-26, after this result was accepted)

**Run on the Bridge's go.** Runner `air/p3d.sh` (576395b, committed before it ran) is a verbatim subset of p3c.sh: the
same environment and command line, with only that one stage. It ran on the Air from 23:33:52 to 23:34:22, rc 1.
Outputs are in `air_p3/`: `p3d.log`, `guard_p3d.log`, `route1_seg_9_10_kc39o10h1o20_v5.out`.

**It stopped the same way as 3/5.** That was `RuntimeError: Laurent tail bound: non-finite on |omega| = 0.9/a`, in
`V.laurent(acb(kc), True)` (v5 line 197, v2 line 168), before the precondition and before any walk. **The addendum's
prediction (P = 95%) is a hit.** It is consistent with the Laurent-circle quantity depending on x = a²ω² only.

**A correction to the diagnosis in the seal addendum, made before probe (a) runs.** The addendum said an arc's ball for
1 − kφ "evidently contains 0". That was not established, and a first-order numpy model argues against it:
- At k = 3.9 the smallest ratio over the 400 arcs, of |1 − kφ| at the arc centre to a first-order estimate of that
  arc's ball radius, is about 24. A ball 24 times smaller than its distance from 0 does not contain 0.
- Re(1 − kφ) < 0 sets in at k ≈ 3.873. Where it is negative, |Im(1 − kφ)| ≥ 0.04, so at first order no arc's ball
  straddles the branch cut of the principal square root either.

So **why** the arc bound goes non-finite at 3.9 is open. Candidates are Arb's dependency inflation in evaluating φ on
an arc ball (well beyond first order), or the branch-cut handling of `acb.sqrt`. Probe (a) is designed to settle it by
recording each arc's actual ball.
