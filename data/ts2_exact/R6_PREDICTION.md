# TS δ=2 p = 4/5, RANK 6, per parity sector — sealed prediction

*Committed before the rank-6 run (Bridge GO 2026-10-04, gates 1–2 passed first). Instrument:
`scripts/_kt_exact_sector.py`. Settings: rank 6, den L³, box 34×34 (the reducible box plus margin 4), 102,900
unknowns in four sectors: s0 (sy=0, sT=0) 27,230 columns; s1 (1,0) 26,670; s2 (0,1) 24,500; s3 (1,1) 24,500.*

| sector | (sy, sT) | predicted nullity | predicted reducible | predicted IRREDUCIBLE |
|---|---|---|---|---|
| s0 | (0, 0) | 16 | 16 | **0** |
| s1 | (1, 0) | 0 | 0 | **0** |
| s2 | (0, 1) | 0 | 0 | **0** |
| s3 | (1, 1) | 0 | 0 | **0** |
| total | | 16 | 16 | **0** |

**Why these numbers.** The 16 reducible products p_t^a p_φ^b H^c with a + b + 2c = 6 all have a + b even (so sT = 0)
and are even in y (so sy = 0). They all fall in s0. The other three sectors carry no reducibles. Any nullity in
those sectors would be irreducible by construction.

**Confidence: ~95% for 0 irreducible in every sector.** Same basis as the rank 2–4 prediction (788dcc9), which
matched. A positive in any sector would surprise me. If one appears, that sector's second prime runs, then STOP,
and it goes to the Bridge for an independent check. No claim of any kind before that.

**Partial results are allowed and will be labelled.** The hard stop is at 13:30 IST. Prime 0 runs all four sectors
first (two processes in parallel), then prime 1. A sector without both primes is reported as single-prime and not
as a rung.
