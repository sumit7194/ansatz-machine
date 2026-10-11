# Environment and how to reproduce

Fleet policy (2026-10-11, from the user): our code is used as proof, so someone must be able to replicate it.

## The pinned environment
- `stamp.json`: the machine-readable stamp, written by `scripts/envstamp.py`. It records the Python version and
  executable, platform and macOS, the git commit, numpy, scipy, sympy, mpmath, numba, llvmlite, the BLAS/LAPACK of
  numpy AND scipy, rustc and cargo, FLINT/GMP/MPFR, and the dylibs `native/flint_rank` links.
- `requirements-lock.txt`: `pip freeze` of the interpreter that runs everything.

| item | version (stamp 2026-10-11) |
|---|---|
| Python | 3.14.5 (Homebrew), `.venv` |
| numpy / scipy | 2.4.6 / 1.18.0, both linked to **Apple Accelerate** (BLAS and LAPACK) |
| sympy / mpmath | 1.14.0 / 1.3.0 |
| numba / llvmlite | 0.65.1 / 0.47.0 |
| platform | macOS 26.5, arm64 |
| Rust | rustc 1.98.1, cargo 1.98.1; `rust/ktdense/Cargo.lock` and `rust/ktsolve/Cargo.lock` are committed |
| FLINT | 3.6.0 (Homebrew; libflint.24), GMP 6.3.0, MPFR 4.2.2 |

No Lean in this repo.

## Setup and native builds
```bash
python3.14 -m venv .venv && .venv/bin/python -m pip install -r ENVIRONMENT/requirements-lock.txt
brew install flint            # 3.6.0 at stamp time (pulls gmp, mpfr)
cc -O2 -o native/flint_rank native/flint_rank.c -I/opt/homebrew/include -L/opt/homebrew/lib -lflint -lgmp -lmpfr
(cd rust/ktdense && cargo build --release)
(cd rust/ktsolve && cargo build --release)
.venv/bin/python scripts/envstamp.py      # refresh the stamp on YOUR machine and compare
```
The `flint_rank` command line above was reconstructed on 2026-10-11, because the original build command was not
recorded. It is verified: the rebuilt binary gives byte-for-byte the same output as the committed binary on a test
matrix (the Kerr rank-4 jet matrix, nullity 14).

Note: `.venv/bin/pip`'s shebang still points to the repo's former path. Use `.venv/bin/python -m pip`.

## How to reproduce the cited results
All runs are exact (GF(p)) or deterministic (seeded). Each command prints a VERDICT line comparable to the committed
log.

| result | command | log |
|---|---|---|
| §149 TS jet bound (e.g. p = 4/5, valence 10) | `.venv/bin/python scripts/_kt_jet.py --metric ts2:4/5 --rank 10 --point 3,1/3` | `data/jet/targets.out` |
| §149 validation (Kerr Carter, ZV, Vollmer TS p = 3/5 r7, sabotage) | see `data/jet/PREREGISTRATION.md`; `_kt_jet.py --metric kerr:1:1/2 --rank 2 --point 3,1/3` etc. | `data/jet/validation.out` |
| §151 MN controls | `.venv/bin/python scripts/_kt_jet_mn.py --controls` | `data/jet/mn_controls.out` |
| §151 MN bound | `.venv/bin/python scripts/_kt_jet_mn.py --mn p1 --ranks 1-10 --points P1,P2` (and `--mn p2`) | `data/jet/mn_targets.out` |
| §152 p-sweep builds | `data/jet/run_psweep_build.sh` | `data/jet/psweep_build.out` |
| §152 p-sweep jets | `data/jet/run_psweep.sh` (160 verdicts) | `data/jet/psweep.out` |
| §150 α (first pair) | `.venv/bin/python scripts/_ts_chaos_alpha.py 2 1500` | `data/ts_chaos/alpha.out` |
| §150 α addenda | `data/ts_chaos/run_alpha2.sh`, `data/ts_chaos/run_alpha3.sh` | `alpha2.out`, `alpha3.out` |
| §150 scans / confirmations | `data/ts_chaos/run_v2.py`, `data/ts_chaos/run_confirm.sh` | `scans_v2.out`, `confirm_A5.out` |
| §150 provenance checks | `scripts/_ts_chaos_cachecheck.py`, `_ts_chaos_check3.py`, `_ts_chaos_ergocheck.py` | `cachecheck.out`, `check3.out`, `ergocheck.out` |
| TS2 file parse integrity | `scripts/_ts2_parse_check.py` (20 fresh processes, `PYTHONMALLOC=debug`) | `data/jet/ts2_parse_check.out` |

Bit-for-bit reproduction of the α floating-point integrations is expected on the same arm64 / Accelerate / numba
stack. On a different stack, individual orbits near the fractal boundary can change outcome; that is the measured
sensitivity itself. The α VALUES should agree within their confidence intervals, and the exact (GF(p)) jet bounds
must agree exactly.

## The two independent implementations behind each claim
| claim | this repo | independent implementation |
|---|---|---|
| §149 TS jet bound | `_kt_jet.py`: Python 3.14.5 + numpy 2.4.6 series, rank by FLINT 3.6 or Rust `ktdense` | the Bridge V10, its own stack (see TheBridge FINDINGS) |
| §151 MN jet bound | `_kt_jet_mn.py` (the same stack + exp/√ series) | the Bridge V10-MN (TheBridge fafb1ae), its own transcription and evaluator |
| §150 chaos | Dormand–Prince 5(4) in numba 0.65.1 (`_ts_chaos.py`) | the Bridge V11 (numba DOP853); V12 α pending |
| §152 p-sweep | `_kt_jet.py` | the Bridge V10 subset reproduction, queued |
