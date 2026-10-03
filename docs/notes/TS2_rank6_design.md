# TS δ=2 at p = 4/5, rank 6: how to do it properly (design note, nothing run)

*2026-10-04, overnight. Written at the Bridge's request after rank 6 was cut for tonight's caps (30 GB footprint,
10 GB disk). The aim is a clean, exact rank-6 rung at the point Vollmer 2016 did not cover. A null there would be
new.*

## Where the cost actually is (measured tonight, not assumed)

| run | unknowns | operator nonzeros | operator build | Rust solve | blocks found |
|---|---|---|---|---|---|
| TS r2 den¹ | 2,250 | 11.4 M | 204–215 s | 3.0 s | 4 (largest 705 cols) |
| TS r3 den¹ | 4,500 | 26.1 M | 268 s | 13.2 s | 4 (largest 1,170) |
| TS r4 den² | 21,875 | ~125 M (projected) | see r4 log | see r4 log | — |
| TS r6 den³ | 102,900 | **~800 M (projected)** | — | — | — |

Two facts drive the design:

1. **The solver already exploits the parity structure.** `rust/ktsolve` finds blocks by union-find on the
   row/column graph. On TS it finds exactly **4 blocks of about ¼ each** at every rank tried. That is what
   y → −y, p_y → −p_y (g^ab is exactly even in y, checked) and (t, φ) → (−t, −φ) predict, and here the
   structure is discovered from the matrix rather than assumed. So "block the operator by parity" is already
   true *inside the solve*. Solving is not the bottleneck (seconds).
2. **The bottleneck is building and holding the whole operator at once.** That means the SymPy template
   brackets, then the Python-level shift-and-add over every column (around 250 B per nonzero as dicts; ~100 B
   per nonzero end to end on tonight's array path, including the Rust copy), then a single matrix file
   (12 B per nonzero, which is ~9.6 GB at 800 M).

## The plan, in order of payoff

**1. Build and solve one parity sector at a time (≈ 4× less peak memory and disk).**
- Columns are m(p)·x^a y^b / L^d.
- Under y → −y, p_y → −p_y a column has parity (−1)^(b + e_y), where e_y is the p_y exponent of m. Under
  (t, φ) → (−t, −φ) it has parity (−1)^(e_t + e_φ).
- H is even under both, so {H, ·} preserves both parities. The operator is exactly block-diagonal over the
  4 sectors, and the nullity is the sum over sectors.
- Each sector is an independent run: its own columns, its own matrix file, its own nullspace. Peak becomes
  one sector, about ¼ of 800 M ≈ 200 M nonzeros, i.e. ~2.4 GB on disk and ~20 GB footprint on tonight's
  bytes per nonzero. **Both are under the caps**, run serially.
- The reducible products split by sector too, since p_t and p_φ are odd under time reversal and H is even.
  So the reducible span is subtracted per sector.
- **Validation by reproduction:** the per-sector nullities must sum to the full-operator nullity, and the
  per-sector reducible ranks to the full one, exactly, at ranks 2, 3 and 4 (all done tonight on the full
  operator), on both primes, together with the Kerr r2/r3/r4 controls. A sector that disagrees means the
  parity argument is wrong for this metric, which the union-find result already says it isn't.

**2. Build the columns in NumPy, not Python dicts (≈ 10–20× less memory during the build, much faster).**
- Every column is the same three templates shifted: cleared(m, a, b) = x^a y^b U + a x^(a−1) y^b V + b x^a y^(b−1) W
  (D49). So all columns of a monomial come from three small arrays by integer index shifts and scalar
  multiplies mod p. This is a vectorised operation that emits uint32 (row-code, col, val) triples directly.
- No per-column dict ever exists. That removes the ~250 B per nonzero transient and Python's per-entry loop,
  which is most of the 204–268 s build at ranks 2–3 and would be hours at rank 6.
- **Validation:** the same arrays as the dict path, byte for byte, at ranks 2–4 (SHA-256 of the sorted
  triples) plus the nullspace-basis hash. That is the same equality test that cleared tonight's
  dict → array change.

**3. Only then, if still needed: drop to den² for the irreducible search at rank 6 as a complementary
ansatz.**
- den³ is required to hold the full reducible algebra (H³), and that is the honest primary run.
- A den² run is NOT a substitute. It cannot contain H³, so it measures a different, smaller space. It is
  noted here only so nobody reaches for it as a shortcut.

## What a rank-6 result would and would not say
- **A null:** "no irreducible Killing tensor of valence 6 on TS δ=2 at p = 4/5 (q = 3/5), within
  {x^a y^b / L³}, box 34×34 (the reducible box plus margin 4), exact over GF(p) on two primes, reducible span
  subtracted". It complements Vollmer 2016 (valence ≤ 7 at p = 3/5) at a parameter point he did not treat.
  Ceilings: rank (6 is a single rung) and ansatz (box and denominator). It is exact, not perturbative.
- **A positive** would need, before any claim: the second prime, the Bridge's independent check, a widened box,
  and reproduction from a different implementation (the two-implementation rule).

## Cost estimate for the proper run (to be re-measured after steps 1–2 exist)
4 sectors run serially. Each is ~200 M nonzeros, ~2.4 GB on disk, and a Rust peak like tonight's per-nonzero
rate. A few hours per sector at 2–4 threads, ×2 primes. That fits one unattended night in a sector-by-sector
queue, with the controls first.
