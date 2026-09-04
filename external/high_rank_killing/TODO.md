# TODO — living list

*Open questions, unverified claims, deferred work. Rule IX: this file is as important as the
report, because it is what stops an open question quietly becoming a settled one.*

## RESUME POINT — 2026-09-05, after EXP-003 (write-up delivered)

**State.** `WRITEUP.md` is the deliverable: a 4D (1,3) vacuum pp-wave with a polynomially
irreducible, functionally dependent rank-3 Killing tensor (EXP-002), a 5D (1,4) vacuum companion
by gyratonic oxidation (EXP-003), CG's own (2,2) cubic shown explicitly to be `−½{Q_a,Q_b}`, and a
prior-art sweep on the object itself that found nothing. Rank ≥ 5 is parked per the user; rank 4
in vacuum is blocked (CG's rank-4 metrics have no Lorentzian form; the bracket tower closes).

**Open.** Only the KK reading of the 5D metric as a 4D Einstein–Maxwell pp-wave, which is stated
in `WRITEUP.md` §6 but not re-verified. The 5D squeeze closed at 3/9/20 (`results/exp003_5d_squeeze.log`).

## Before any construction

- [x] **M1 sweep.** Done — EXP-001.
- [x] **Dimension of the known examples.** CG rank 3: D = 4,5,6; rank 4: D = 5,6; all (2,q).
      Sibling's control is CG eq. 26, 5D, signature (2,3).
- [x] **Is rank ≥ 5 covered by an existing theorem?** No general theorem either way. Existence
      without field equations: yes (Galajinsky 2012). Non-existence: specific metrics only.
- [x] **Classical obstruction / rank bound.** None. DTT dimension formula per rank only.
- [x] **Decisions (a)–(c)** answered 2026-09-05: report both senses; state signature; continuation first.

## Instrument

- [x] Read `../conjecture_machine/scripts/_kt_cg5d.py` docstring in full. (Transcription hazard:
      derive the rank-4 target from CG eq. 24, never transcribe eq. 29 — `K_ttxw` vs `K_tttw`.)
- [x] CG 4D rank 3 reproduced from this repo by importing the sibling's prover: 2/6/11 (EXP-002).
- [ ] CG 5D rank 4 not yet reproduced from this repo (only needed if the 5D continuation is run).
- [ ] Galajinsky 2012's rank-5 Calogero tensor (7D Lorentzian) is the only published rank-5
      positive control. Check feasibility of running it; if infeasible, say so.
- [ ] Establish that any rank-5 search space could contain a rank-5 answer before any null
      means anything (representability rule).
- [ ] Note the prover's den¹ scope; den² was only ever run at ZV rank 4.

## Unverified claims (carried from EXP-001)

- Galajinsky 2012 irreducibility of ranks 3..n is "by construction" (leading-symbol argument);
  never checked exactly by anyone that I found.
- Lense–Thirring "towers" (Gray et al. 2022, GOKK 2025): irreducibility of rank ≥ 3 members only
  "hinted" in the source.
- The 4D Lorentzian lift of Kiyohara/Valent 2D metrics stays irreducible — expected, unverified.
- For a second-order-superintegrable 2D base the polynomial integrals close at rank 3 (so no
  polynomially-irreducible rank ≥ 4 from such a base) — `F² ∈ ℚ[H,Q1,Q2,p_t,p_s]` verified; the
  rank-4 brackets {Q1,F} = −(H−p_t p_s)Q2 and {Q2,F} = (H−p_t p_s)Q1 − ½a²p_s⁴ are reducible
  (verified pointwise, two values of a; `results/exp002_tower.log`). Closed for this metric.
- CG's "none of Hietarinta's cubic-or-higher systems is harmonic" — their inspection, not mine.
- ~~The Wick-rotation candidate — entirely unverified.~~ Verified in EXP-002.
- TTW extra integral has degree 2k — from secondary sources.

## Deferred

- Thompson 1986 full text (paywalled): reducibility on constant curvature taken from FG 2019 and
  McLenaghan–Milson–Smirnov 2004 instead.
- Galajinsky 2017 PPNL note: abstract only (no arXiv).
