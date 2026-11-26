# SEAL (office, 2026-11-26, BEFORE any run): the k-Taylor form inside the centred enclosure (v4), predictions

**Branch:** `office/2026-11-26-ktaylor`, from `office/2026-11-26-centred-encl` (v3 at 8b9971c).
**Asked by:** the Bridge, 2026-11-26. Proof stage only: one process, nice 12.

## What v4 changes, and why (diagnosis from reading the code)
- **What v3 did.** v3 builds the z-series of dq/dk at the step midpoint z_m with k a ball (a k-sub-box). Its STARTING
  VALUES c0(z_m), c0′(z_m), ∂_k c0(z_m), ∂_k c0′(z_m) come from the order-190 Laurent series evaluated at the k-BALL.
  That evaluation inflates, measured at spin 9/10: radius 0.08–4.2 against |c0| ≈ 0.01–0.07.
- **What Fable's v2 already does.** v2's crude `dq_sup` already uses a Taylor form in k: point-k_c Laurent values
  plus dk·∂_k plus dk²/2·E, where E = ∂²_k is ENCLOSED over the whole k-square K (`d2kc0`). `d2kc0` is a radial
  integral from infinity, enclosed on balls of s by a rectangle rule, with Re(1 − kφ) > 0 certified on every ball.
- **v4 = v3 with the starting values taken in v2's form,** at the POINT z_m:
  - c0(z_m; k) ∈ c0(z_m; k_c) + dk ∂_k c0(z_m; k_c) + (dk²/2)·E0(z_m, K);
  - c0′ is the same, with E1;
  - ∂_k c0 ∈ ∂_k c0(k_c) + dk·E0, and ∂_k c0′ is the same, with E1.
  - Everything else in the z-series is unchanged: c0″ = c_K″ √(1 − kφ) and its k-derivative in closed form, with k a
    ball.
- **R₂ is ENCLOSED, not sampled.** It is the Taylor remainder in k, ∫₀¹(1 − τ)∂²_k c0(k_c + τ dk)dτ·dk². K is convex,
  so the remainder lies in (dk²/2)·(the convex box enclosing ∂²_k c0 on K). That box is d2kc0's output, an enclosure
  on balls.
- **A change from the design note.** The note (ROUTE1_CENTRED_OFFICE.md) proposed a Cauchy estimate on the Laurent
  circle. v4 uses the radial-integral enclosure instead.
  - That enclosure is already in v2's chain, and the office verified the v2 segment (ROUTE1_OFFICE_CHECK.md).
  - It needs holomorphy only along the rays from infinity, which is certified per ball. It also needs no second
    Laurent tail.
- **Unchanged from v3:**
  - the outer-box Cauchy remainder in z (v2 `dq_sup` on a box 2×, else 1.5×, wider, which also certifies
    holomorphy);
  - min(centred, crude);
  - order 30.
- **Checkpointing.** Each ρ row is appended to a jsonl when done, so a rerun resumes. No caps of any kind.

## Predictions, sealed separately per direction

**z-direction: the constants at the POINT k_c (dk = 0, so v4 reduces to v3 exactly).**

| | v3 measured | v4 prediction |
|---|---|---|
| spin 3/5 circle / lasso | 0.4153 / 9.325 | identical to v3 (same printed digits) |
| spin 9/10 circle / lasso | 0.7734 / 21.79 | identical to v3 |

This is a control that can fail: any difference means v4 altered the z-side.

**k-direction: the ratio (disc constant) / (point constant).** Rows: 3/5 at ρ = 4 (R ≈ 0.106), 9/10 at ρ = 3
(R ≈ 0.083).

| | v3 measured ratio | v4 predicted ratio | v4 predicted disc constant |
|---|---|---|---|
| spin 3/5 circle | 10.4 | 1.2 – 3 | 0.5 – 1.3 |
| spin 3/5 lasso | 4.5 | 1.2 – 3 | 11 – 28 |
| spin 9/10 circle | 866 | 1.2 – 5 | 0.9 – 3.9 |
| spin 9/10 lasso | 5.7 | 1.2 – 5 | 26 – 110 |

**n (best ρ over 3, 4, 5, 6.5; target 1e−3 on F as in v2).**
- Spin 3/5: n in **10 – 16** (v2: 24; v3: 18).
- Spin 9/10: n in **14 – 32** (v2: 140; v3: 134).
- **P(n at 9/10 ≤ 40) = 80%.**
- The rough arithmetic behind these: with gauge factors near v3's (3/5: 2.2, 13.4; 9/10: 2.4, 11) and the lasso
  term dominating M_F, a disc ratio of 2 gives n ≈ 12–14 (3/5) and 16–20 (9/10). A ratio of 5 gives about 26–30
  at 9/10.
- **If the 9/10 n misses high,** the likely reasons are k-sensitivity near the inner poles (√(1 − kφ) small on the
  circle there) or the sub-box ball width in the z-series.

**Controls (the Bridge's).**
1. **Spin 3/5 certifies at EQUAL n = 24.** Run the verdict at ρ = 4, n = 24 on v2's own node values (the same 25
   nodes + held-out, from d855810's jsonl), with the v4 proved M.
   - Prediction: CERTIFIED, with every lower bound (|F|, |tr M0|, |Im tr M1|) ≥ v2's.
   - Since the nodes are equal, this holds iff each of v4's M_F, M_trM0, M_trM1 at ρ = 4 is ≤ v2's (6.57e10, 9.22,
     1.54e4). That is predicted to hold for all three.
2. **v3 at equal n,** for the record of the earlier grading: the same verdict with v3's ρ = 4 M at n = 24. Predicted
   to be no weaker than v2 on all three. Not a real prediction: v3's ρ = 4 M values (1.54e7, 3.22, 667) are already
   known to be below v2's, so the run only confirms it.
3. **v2 and v3 outputs stay reproducible from their commits.** v4 imports v2 and v3 unchanged and writes under new
   names. I will re-run v3 `prove` at spin 3/5 on a clean checkout of 8b9971c and compare it with the committed JSON.
   - Predicted byte-identical, except possibly the env/timing fields. The JSON has no timings; the .out log has.

**Footprint.** Under 300 MB (v3 measured 37–52 MB), one core, nice 12.
- Time estimate: spin 3/5 about 15–25 min. Spin 9/10 about 1–2.5 h for four ρ rows, since the centred series now
  runs on every (step, sub-box) pair of ~18,850 steps × 25 sub-boxes.
- That is longer than "short". If one ρ row at 9/10 takes over 40 min, I will report and run only ρ = 3 and 4 first,
  ordered by expected n. That is a choice of rows, not a cap.
- Limits that remain: none on time or steps. The correctness gates (holomorphy box fails, non-finite enclosure)
  reject a ρ row at its checkpoint, as in v2/v3.
