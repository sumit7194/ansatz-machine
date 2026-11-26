# Air reproduction of the spin-9/10 v4 certificate: result (2026-11-26)

[ansatz-machine-personal. Ran on the MacBook Air at `~/GitHub/ansatz-air/`, with the code copied at 43a2de1 (all
46 manifest files verified unchanged after the run). Started 12:25:12, ran under nice 15 and the pause-only guard
(job.sh v2, which never paused), finished 14:19:21 with rc 0. Outputs are in `air_out/`.]

## Verdict: DIFFERS. The certificate matches; three rows that were not chosen differ.

`scripts/_nve_route1_air_compare.py data/nve/route1_check/air_out`:

| file | result |
|---|---|
| `route1_seg_v4_9_10_dqck.jsonl` (per-step dq bounds, 9.1 MB) | **byte-identical** (sha256 210a0e41…) |
| `route1_seg_verdict_v2_arb_9_10_v4cert_nseg1.json` | **byte-identical** (sha256 7276bd69…) |
| `route1_seg_M_v2_9_10_v4cert_nseg1.json` (the chosen row, v2 format) | identical after dropping `sec` |
| `route1_seg_v4_9_10_rows.jsonl` | **DIFFERS**: row ρ = 4 (the chosen row) is identical apart from `sec`; rows ρ = 3, 5 and 6.5 differ |
| `route1_seg_M_v4_9_10_nseg1.json` | **DIFFERS**: the same three rows (`env` and `sec` dropped as declared) |

The rows that differ do so in these fields, and only these: the gauge matrices C0 and C1 (last digit of a double, e.g.
0.47127386174373814 against …803), the gauge norms (16th digit) and everything bounded through the gauge, which is
I0, I1, M_F, M_trM0, M_trM1, the Chebyshev errors and c0/c1 per k (relative change 1e-12 to 1e-9). For example, ρ = 6.5
gives M_F 9.722916884974E+14 on the Air against 9.722916884897E+14 committed. n, ρ, the step counts, the coverage
counts and the choice of row are all the same, and every printed 4-digit number in the log matches.

## Cause: complex × complex in Python 3.13 and 3.14 (measured, machine ruled out)

`gauge()` (`_nve_route1_segment_v2.py:427`) builds the gauge in plain Python doubles, including
`W12 += w * x1.conjugate() * x2`. I hashed 100 000 random results of each operation it uses, plus the common libm calls,
under three interpreters:

| operation | 3.13.12 (Mac mini, the committed run) | 3.14.5 (Mac mini) | 3.14.10 (Air) |
|---|---|---|---|
| complex × complex | d3b89778 | **b9b58d79** | **b9b58d79** |
| float × complex, complex / complex, abs, sqrt, sin, exp, log, atan2, pow | same on all three | same | same |

Only the product changes, and it changes with the Python version, not the machine: the two 3.14 builds agree across the
two computers. The script is `float_ops_hash.py` in this folder. Both machines run macOS 27.2.x.

**Why this does not touch the proof.** By its docstring, the gauge is "a CHOICE, not part of the proof: any invertible C
gives a valid bound", and `dyson_sum` / `gauge_norms` then recompute everything for that C in Arb balls. So both sets of
rows are valid proofs, for gauges that differ by about an ulp. Every Arb step (the dq checkpoint) is byte-identical, and
so are the certified row and the verdict. Row ρ = 4 matching exactly is consistent with this: an ulp difference in the
product need not survive rounding in every row.

**What this does not establish.** It does not show that a 3.14 run on the Mac mini would reproduce the Air rows byte
for byte, though the operation table predicts it would. That is a ~2 h run (`repro.sh` under the repo venv on the Mac mini,
which would need python-flint 0.9.0 installed there) and has not been done.

## Bearing on what comes next

- **(b), the engine check, and P1 are on hold**, per the Bridge's rule ("if it differs, stop and tell me before (b)").
- **T1** (v5 rows equal to v4 rows) must hold the Python version fixed as well as the machine, or it will fail for this
  reason alone. A1 already puts the Python version into the v5 code hash, so a v5 checkpoint from 3.13 is refused under
  3.14. That is the intended behaviour, and this run is direct evidence that it is needed.
- Python 3.13 is not installed on the Air. A byte-for-byte reproduction of the committed files on the Air would need it.

## Run notes

- `guard_repro.log` and `repro.log` include lines from the first launch, before the v1 runner was replaced: "repro pid
  6336 exited rc 143" and a "JOB_EXIT 143". That launch was stopped by me (my own PIDs, 6336 and 6344) 30 s in, and its
  partial outputs were cleared before the relaunch as PID 6431.
- Wall time per row was 1082, 1241, 1951 and 2331 s on the Air, against 936, 968, 976 and 964 s on the Mac mini.

## Follow-up (2026-11-26, the Bridge's ruling: get the exact reproduction)

- **Correction:** the Air's 3.14 venv has numpy 2.4.6, but the committed 3.13.12 run had numpy 2.5.0 (Quantum's venv,
  no numba). `README.md` said all package versions matched; it now says which one did not. numpy is not in the gauge
  path (plain Python doubles), so this does not change the diagnosis above, but it is recorded as a second difference.
- **Installed on the Air:** Homebrew python@3.13 **3.13.18** (Homebrew does not offer 3.13.12), in `.venv313` with
  python-flint 0.9.0, mpmath 1.3.0, sympy 1.14.0, numpy 2.5.0. Under 3.13.18, `float_ops_hash.py` gives the same hashes as
  3.13.12 for every operation, complex x complex included (d3b89778).
- **Rerun launched** 14:26:24 Air time as `repro313.sh` (PID 15530) from nothing, with the 3.14 outputs moved to
  `data/nve/eps/run314/`. The bar: byte-identical to the committed files, apart from the declared run-time and interpreter fields.
  If it still differs, the patch level (3.13.18 against 3.13.12) is reported before going further.

## (b) The 50-digit engine at all 44 nodes: PASS (2026-11-26, Air)

`engine.sh` under the Air's `.venv` (Python 3.14.10, mpmath 1.3.0; the engine shares no code with the Arb evaluator)
ran 14:23:46 to 15:10:13, rc 0, with the guard never pausing. Every engine value lies inside the committed Arb enclosure
for F, tr M0 and tr M1:
- spin 3/5 (v2 nodes, n = 24): **25/25** (largest F radius 6.4e-9, about 54 s per node);
- spin 9/10 (the v4 certificate's nodes, n = 18): **19/19** (largest F radius 7.4e-8, about 76 s per node).
Checked from the records themselves (every `F_inside`, `T0_inside`, `T1_inside` and `pass` field reads True), not only
from the RESULT lines. Outputs are in `air_engine/`.

## The exact reproduction under Python 3.13.18: IDENTICAL (2026-11-26, Air)

`repro313.sh` (`.venv313`: Homebrew Python 3.13.18, python-flint 0.9.0, mpmath 1.3.0, sympy 1.14.0, numpy 2.5.0) ran
from nothing, 14:26:24 to 17:00:11, rc 0, with the guard never pausing; all 46 manifest files were unchanged afterwards.
`_nve_route1_air_compare.py data/nve/route1_check/air_out313`:
- dq checkpoint: byte-identical (210a0e41…); verdict JSON: byte-identical (7276bd69…);
- rows file, v4 proof JSON, v2-format cert JSON: identical after dropping only `sec` (and `env` in the proof JSON).
  All four rows match, including the gauges of ρ = 3, 5 and 6.5 that differed under 3.14.

So the 3.14 difference was the Python version alone, and the patch level 3.13.18 against 3.13.12 changed nothing.
This closes the Air identity test. Outputs are in `air_out313/`; the 3.14 outputs stay in `air_out/`.
