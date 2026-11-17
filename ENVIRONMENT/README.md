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
| platform | macOS 26.5, arm64 (all results through §152); since 2026-10-24 macOS 27.0.1 (26A434), regression-checked identical, see below |
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
**Read this first: the independence is in the CODE, not the interpreter.** The Bridge's implementations (V10, V10-MN,
V11, V12) run on the SAME Python stack as this repo: CPython 3.14.5 from this repo's `.venv`, numpy 2.4.6 and
scipy 1.18.0 (both Accelerate), sympy 1.14.0, mpmath 1.3.0, numba 0.65.1 / llvmlite 0.47.0, macOS 26.5 arm64 (pinned
in TheBridge ENVIRONMENT/, 243ec82). A bug in a shared dependency (sympy, numpy, numba, Accelerate) would therefore
NOT be caught by our cross-check. The fleet's different-stack implementations are tabula (Python 3.12, then a newer
venv) and quantum (3.13 plus Rust/Arb).

Where the two differ, the difference is real:

| claim | this repo | the Bridge (same interpreter, independent code) | what is genuinely different |
|---|---|---|---|
| §149 TS jet bound | `_kt_jet.py`: numpy series; rank by FLINT 3.6.0 `nmod_mat` or Rust `ktdense` | V10 | the rank engine (FLINT/Rust vs the Bridge's own numpy int32/int64 Gaussian elimination over GF(2³¹−1), no FLINT); series code; points; primes |
| §151 MN jet bound | `_kt_jet_mn.py` (the same stack + exp/√ series, T-specialisation) | V10-MN (fafb1ae) | the metric transcription (its V9), the exp/√ evaluator, the rank engine, points, draw |
| §150 chaos / α | Dormand–Prince 5(4) in numba (`_ts_chaos.py`) | V11 / V12, numba DOP853 | the integrator order and code, event handling, L_sep method, seeds, estimator (binomial MLE in V12) |
| §152 p-sweep | `_kt_jet.py` | V10 subset (queued) | as §149 |

## Known library hazard (resolved)
A vendor numerical-library defect in the platform BLAS/LAPACK QR routine, found by the fleet (tabula) and reported to the
vendor. It was classified as a reliability defect, not a security issue, and is fixed in macOS 27.0.1.
**Audit of this repo's cited results (2026-10-11): not affected.**

Forward rule: any new dense floating-point linear algebra with dimensions in the hundreds gets its shapes logged and
checked against the fleet's hazard note before its results are cited.

## OS update regression check (2026-10-24, macOS 26.5 → 27.0.1, build 26A434)
- The Python stack is unchanged (numpy 2.4.6, scipy 1.18.0, sympy 1.14.0, mpmath 1.3.0, numba 0.65.1, llvmlite 0.47.0),
  as are FLINT 3.6.0 and rustc 1.98.1. Only the OS changed.
- Three reruns compared with the pre-update outputs:
  1. MN jet-bound controls (`_kt_jet_mn.py --controls`): exact GF(p) series and FLINT rank. **Bit-identical**
     to `data/jet/mn_controls.out`.
  2. TS δ = 2, p = 4/5, rank-8 jet verdict at (3, 1/3). **Identical** to `data/jet/targets.out`.
  3. Floating-point engine RHS against 50-digit evaluation (`_ts_chaos_ergocheck.py`): numba/LLVM floats.
     **Bit-identical** to `data/ts_chaos/ergocheck.out`.
- No result needs a rerun.

## OS update regression check (2026-11-17, macOS 27.0.1 → 27.2, build 26B123)
The stack is unchanged apart from the OS. Four spot checks were run at low priority on 1 core, each compared with the
stored output:
1. MN jet-bound controls (exact GF(p) series and FLINT rank): **bit-identical**.
2. TS δ = 2, p = 4/5, rank-8 jet verdict at (3, 1/3): **identical**.
3. Floating-point orbit-engine RHS against 50-digit evaluation (numba/LLVM): **bit-identical**.
4. NEW: one double-double high-precision orbit (HP probe base `T:ts:1:R1`, N = 600: status, crossings, end time,
   steps and shell error): **bit-identical**.

A first attempt reported three false "DIFFERS" because no check had actually run: a command was stored in a zsh
variable, which zsh does not word-split. It was rerun correctly. See JOURNAL 2026-11-17 for the guard added.
