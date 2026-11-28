# Referee guide: claim → file → expected output → run time

For the draft preprint `paper/main.pdf`. Paths are relative to the repository root
(https://github.com/sumit7194/ansatz-machine).
- The software release is v1.2.0, doi:10.5281/zenodo.24593416.
- **Two places hold the files:**
  - the counts, the end sliver and Statement A are on `main` (and in the v1.2.0 archive);
  - the route-(i) production certificates are on the public branch `personal/2026-11-26-route1-check`
    (written `[branch]` below), at the commits named.
- **Environment:**
  - counts and Statement A: Python 3.14.5 with mpmath 1.3.0, sympy 1.14.0 and numpy 2.4.6
    (`ENVIRONMENT/requirements-lock.txt`);
  - route (i): Python 3.13.18 with python-flint 0.9.0, in a separate venv.
- Run times are on one laptop core (Apple M1 or M-series). Every script's docstring repeats its own command.

## 1. The numerical result over (0, 30/7] (Table 1, rows 1–3; §3.1)

| claim | command | expected output | run time |
|---|---|---|---|
| counts on (0, 4.05], spin 0.6 | `.venv/bin/python scripts/_nve_lower_kc_count.py` (resumable; finite-group case `_nve_lower_kc_finite.py`) | `data/nve/gapb.out`, `gapb_verdict.json`: F has Kerr's double zero at 0, and everything else is zero-free | hours |
| counts on [3.95, 30/7 − 10⁻¹²], spin 0.6 | `.venv/bin/python scripts/_nve_lower_hp_count.py` | `data/nve/window.out`, `window_verdict.json`: zero-free | hours |
| endpoint k = 30/7, spin 0.6 | `.venv/bin/python scripts/_nve_lower_k307.py` | `data/nve/k307_A1.out`, `k307_A1_verdict.json` | minutes |
| counts and endpoint at spins 0.3, 0.8, 0.9 | `NVE_SPIN=4/5 .venv/bin/python scripts/_nve_spin_scan.py run` (and 3/10, 9/10) | `data/nve/spin_run_*.out/.json` | up to a few hours per spin |
| end sliver, spin 0.6 (E 0.8 and 1.5) | `data/nve/t48b_fixed/sliver_closure_iv_fixed.py` | `data/nve/t48b_fixed/out_fixed.txt`: δ0 = 1.37e−11 (E 0.8), 1.9e−9 (E 1.5) | 3–15 min |
| end sliver, spins 0.8, 0.9 and 0.3 | `T48_GEO=data/nve/t48b_spin/geo_<spin>.json python data/nve/t48b_spin/sliver_spin.py`; `data/nve/t48b_s4/sliver_s4.py` | `data/nve/t48b_spin/out_*.txt` (δ0 2.4e−10, 3.6e−10); `data/nve/t48b_s4/out_3_10.txt` (7.4e−15) | 3–15 min each |
| degenerate cases (post hoc) | `scripts/_nve_spin_locate.py`, `_nve_spin_kstar.py`, `_nve_spin_locateA.py`, `_nve_ac.py` | `data/nve/spin_locate_4_5.out`, `spin_kstar_4_5.out`, `spin_locateA_9_10.out`, `ac_secant.out`, `ac_circle.out` | minutes |

## 2. Statement A (§3.2)

| claim | command | expected output | run time |
|---|---|---|---|
| c2 formula and value | `NVE_SPIN=3/5 .venv/bin/python scripts/_nve_c2_analytic.py` | `data/nve/c2/analytic_3_5.out`: c2 ≈ 0.1935 + 0.0985i, \|c2\| ≈ 0.217 | seconds |
| c2 ≠ 0, interval-certified | `NVE_SPIN=3/5 .venv/bin/python scripts/_nve_c2_certify.py` | `data/nve/c2/certify_3_5.out`: VERDICT c2 != 0 CERTIFIED | about 10 s |
| must-fail control | `NVE_SPIN=3/5 C2_PLANT=holo .venv/bin/python scripts/_nve_c2_certify.py` | `certify_3_5_PLANTED_mustfail.out`: refused | about 10 s |
| ε_a, interval-certified | `NVE_SPIN=3/5 EPS_R0=1.35 .venv/bin/python scripts/_nve_eps_certify.py` | `data/nve/eps/eps_3_5.out`: VERDICT ... epsilon = r = 1.925557e-03 (tabulated, rounded down: 1.92e−3) | about 80 s |
| ε_a refusal control | as documented in `data/nve/EPS_OFFICE_CHECK.md` | `data/nve/eps/eps_3_5_REFUSE_CONTROL.out`: refused | about 80 s |
| independent checks | `scripts/_nve_c2_sympy_check.py`, `_nve_c2_engine_check.py`, `_nve_eps_office_tailcheck.py`, `_nve_eps_office_polycheck.py` | `data/nve/c2_sympy_check.out`, `c2_engine_check.out`, `eps_office_*.out` | minutes |

The other spins are the same commands with `NVE_SPIN=3/10, 4/5, 9/10` and `EPS_R0` = 1.1492, 1.3382, 1.2639.

## 3. Interval certificates over part of the twist range (§3.3, Figure 1)

| claim | where | expected output | run time |
|---|---|---|---|
| spin 0.6: every real k in [1/640, 3] | `[branch]` `data/nve/route1_check/PROD_3_5_RESULT.md` (commit f7b8e55); log `air_prod_3_5/data/nve/eps/route1_prod_3_5.out` | 35 `CERTIFIED` segments; last lines `batch rerun ... identical True` and `REACH ... [1/640, 3] ... covers the target [eps_a, 3]: True` | 15.9 h |
| spin 0.3: every real k in [1/320, 3] | `[branch]` `data/nve/route1_check/PROD_3_10_RESULT.md` (commit b3e7494); log `air_prod_3_10/.../route1_prod_3_10.out` | 34 `CERTIFIED` segments, one `STOP RULE (radius-limited)` at [1/640, 1/320], `REACH ... [1/320, 3]` | 14.1 h |
| predictions fixed before the runs | `[branch]` `PROD_SEAL.md` (3/5), `PROD_SEAL_3_10_4_5.md` (3/10) | compare with the "Against the seal" tables in the result files | n/a |
| rerun a production | `PY313=.venv313/bin/python PY314=.venv/bin/python NVE_SPIN=3/5 R1_R0=1.35 PROD_TOP=3 PROD_EPS=1.92e-3 .venv313/bin/python -I -u scripts/_nve_route1_production.py` (on `[branch]`; 3/10: `R1_R0=1.1492 PROD_EPS=2.79e-3`) | the same log, with byte-identical verdicts | 14–16 h |
| Figure 1 data | `python3 paper/make_figure_data.py` (on `main`; it reads the two logs from `[branch]` via git) | `paper/fig_bounds_3_5.dat`, `fig_bounds_3_10.dat` (35 and 34 segments) | seconds |
| loop validity (circle closes while it encloses all branch points) | `[branch]` `NVE_SPIN=<a> python scripts/_closure_check.py`; record `CLOSURE_STOPC_RESULT.md` (06a256a) | `closure_stopc/closure_*.out`: CLOSES up to k_cross, DOES NOT CLOSE beyond | 74 s per spin |

## 4. Not in the paper's results (in progress, or out of scope)
- **Spins 0.8 and 0.9:** the route-(i) productions are still running. No result is claimed.
- **The top of the range [3, 30/7 − δ0]:** numerical only. A plan to certify it exists but is not approved.
