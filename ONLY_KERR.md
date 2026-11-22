# Twisted Kerr-mass fields: geodesics along the symmetry axis are not integrable (landing page)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.24431695.svg)](https://doi.org/10.5281/zenodo.24431695)

Archived as Ansatz Machine v1.0.0, DOI [10.5281/zenodo.24431695](https://doi.org/10.5281/zenodo.24431695).

**In five lines.**
1. We take stationary axisymmetric vacuum fields with exactly Kerr's mass profile along the symmetry axis, and
   deform only the twist, by a one-parameter family with parameter k (k = 0 is Kerr).
2. Along the bound geodesic that runs up and down the lower symmetry axis, the linearised motion has a "monodromy
   group" that is as large as it can be (Zariski-dense in SL(2, C)) for every twist in the physical range.
3. By the Morales–Ramis theorem, this rules out a complete set of meromorphic constants of motion near that orbit.
   Kerr's own Carter constant is the integrability that is lost.
4. The result is numerical (50-digit arithmetic). It is proved in interval arithmetic only at the top end of the
   range. It covers four spins and one energy.
5. Two hostile referee rounds were run on it and answered. Every step of the argument is checked here or cited at
   source.

**Status:** a careful numerical result, not a theorem. Read the status block of the claim first.

## The documents
| document | what it is |
|---|---|
| [`data/nve/CLAIM_FAMILY_II.md`](data/nve/CLAIM_FAMILY_II.md) | **THE claim (version 2)**: status, the one-sentence statement, conventions, the evidence table with a grade per row, scope, prior art, and a separate related result on rational axis data |
| [`data/nve/MRS_SECTION.md`](data/nve/MRS_SECTION.md) | Why Morales–Ramis(–Simó) applies. §1 the theorem and the class of integrals excluded; §4 and §4b the off-axis metric (Proposition 2, with our own majorant convergence proof); §5–§5e the lower-axis data (e₋ = 1/e₊, derived; no reflection symmetry needed), the Cartesian NVE, loops, k → 0, k = 4; §6 the citation status, each checked at source |
| [`data/nve/T38_GRADING.md`](data/nve/T38_GRADING.md), [`data/nve/T51_GRADING.md`](data/nve/T51_GRADING.md) | The two referee rounds, point by point, with our grades and fixes |
| [`data/nve/NOTES2_KOVACIC_CHECK.md`](data/nve/NOTES2_KOVACIC_CHECK.md) | The check, against Kovacic's original paper, behind the related result on rational axis data |
| `data/nve/*_PREREGISTRATION.md` | Every run was pre-registered before it was executed. Failed and void runs are kept and labelled |
| [`RESULTS.md`](RESULTS.md) §158, §159, §161–§163 | The lab-notebook entries |

## Evidence table → code → output
Paths are relative to the repository root.

| claim row | script | output | pre-registration |
|---|---|---|---|
| counts on (0, 4.05], spin 0.6 | `scripts/_nve_lower_kc_count.py` (+ `_nve_lower_kc_finite.py` for the finite-group case) | `data/nve/gapb.out`, `gapb_verdict.json`, `gapb.jsonl`, `gapb_finite.out` | `GAPB_PREREGISTRATION.md` |
| counts on [3.95, 30/7 − 10⁻¹²], spin 0.6 | `scripts/_nve_lower_hp_count.py` (engine `_nve_lower_hp.py`) | `data/nve/window.out`, `window_verdict.json` | `WINDOW_PREREGISTRATION.md` |
| k = 30/7, spin 0.6 | `scripts/_nve_lower_k307.py` | `data/nve/k307_A1.out`, `k307_A1r2.out`, `k307_A1_verdict.json`; the VOID first run is kept as `k307.out` | `K307_PREREGISTRATION.md` (amendment A1) |
| counts and endpoint at spins 0.3, 0.8, 0.9 | `scripts/_nve_spin_scan.py` (modes `geo`, `run`) | `data/nve/spin_geo_*.json`, `spin_run_*.out/.json`; the crash is kept as `spin_run_3_10_crash1.out` | `SPIN_PREREGISTRATION.md` |
| end sliver, interval arithmetic, spin 0.6 (E = 0.8 and 1.5) | `data/nve/t48b_fixed/sliver_closure_iv_fixed.py` (with `PATCH.diff`) | `data/nve/t48b_fixed/out_fixed.txt` | `T48_T49_CHECK.md` |
| end sliver at spins 0.8, 0.9 (S3) and 0.3 (S4) | `data/nve/t48b_spin/sliver_spin.py`, `data/nve/t48b_s4/sliver_s4.py` | `data/nve/t48b_spin/out_*.txt` (the S2 failures are kept as `*_S2fail.txt`), `data/nve/t48b_s4/out_3_10.txt` | `SPIN_PREREGISTRATION.md` amendments S2–S4 |
| spin 0.8, degenerate pair near k ≈ 4.0082 (post hoc) | `scripts/_nve_spin_locate.py`, `_nve_spin_kstar.py` | `data/nve/spin_locate_4_5.out`, `spin_kstar_4_5.out` | labelled post hoc |
| spin 0.9, extra non-real zero (post hoc) | `scripts/_nve_spin_locateA.py` | `data/nve/spin_locateA_9_10.out` | labelled post hoc |
| a_c ≈ 0.858446 | `scripts/_nve_ac.py` | `data/nve/ac_secant.out`, `ac_circle.out` | post hoc |
| a⁷–a⁸ weakening | `scripts/_nve_endpoint_scaling.py` | `data/nve/endpoint_scaling.out` | — |
| no zeros split off k = 0 | analytic (`MRS_SECTION.md` §5d), with the counts above | — | — |
| e₋ = 1/e₊ (Kerr; an asymmetric two-mass check) | `scripts/_nve_t51_axis_check.py` | `data/nve/t51_axis_check.out` | — |
| the family is not reflection-symmetric | `scripts/_nve_family2_reflection.py` | `data/nve/family2_reflection.out` | — |
| Proposition 2, numerical control | `scripts/_nve_prop2_majorant_control.py` | `data/nve/prop2_majorant_control.out` | — |
| related result (rational axis data) | `scripts/_nve_monodromy.py`, `scripts/_nve_ts2_axis_deg.py` | `data/nve/monodromy.out`, `ts2_axis_deg.out` | `NVE_PREREGISTRATION.md` |

## Rerunning
- **Environment** (see [`ENVIRONMENT/`](ENVIRONMENT/)):
  - Python 3.14.5, with mpmath 1.3.0, sympy 1.14.0, numpy 2.4.6 and scipy 1.18.0.
  - Recorded on macOS arm64.
  - Install with `python3.14 -m venv .venv && .venv/bin/python -m pip install -r ENVIRONMENT/requirements-lock.txt`.
- **Commands.** Each script's docstring gives its command and its output file.
  - The spin is set by the environment variable `NVE_SPIN`, e.g. `NVE_SPIN=4/5 .venv/bin/python scripts/_nve_spin_scan.py run`.
  - The sliver certificates read the loop geometry from `T48_GEO=data/nve/t48b_spin/geo_<spin>.json`.
- **Cost.**
  - Most runs take seconds to tens of minutes on one core, using well under 1 GB.
  - The spin runs and the window count take up to a few hours.
  - The interval certificates take 3–15 minutes each.
- **Precision.** Results are 50-digit floating point unless stated otherwise. The integration step was varied as a
  control; each pre-registration says how, and the outputs record the agreement.

## How this was made
- **AI assistance.** This work was developed with substantial assistance from Anthropic's Claude, which:
  - wrote and ran most of the code;
  - checked the literature at source;
  - drafted the documents.
- **Author's role.** The author chose the questions, directed and reviewed the work, and takes responsibility for it.
- **Other AI sessions.**
  - The referee rounds (T38, T51) were hostile reads by a separate AI reviewer session; T-numbers are its task
    numbers.
  - Several cross-checks were done blind by other AI sessions working on separate projects. The documents call them
    "relayed" until reproduced here. Names such as "the Bridge" (the coordinating and cross-checking session) and
    "Neon" (the reviewer) refer to these sessions.
- **Review.** No professional physicist has reviewed this yet. Corrections are very welcome.

Author: Sumit Pal (independent researcher).
