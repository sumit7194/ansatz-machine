# The Air run folder for ansatz (ansatz-machine-personal), 2026-11-26

- **Where:** `air:~/GitHub/ansatz-air/`, created for this work. It is not a clone; no commits are made from the Air.
- **Files:** a minimal pinned copy at 43a2de1 (`personal/2026-11-26-route1-check`): the local-import closure of the
  route-(i) scripts plus the five data files they read. Every file's sha256 is in `MANIFEST_43a2de1.sha256`, and all
  46 verified on the Air after unpacking.
- **Environment:** its own venv (`.venv`), Homebrew Python 3.14.10, with `requirements-pinned.txt`: python-flint
  0.9.0, mpmath 1.3.0, sympy 1.14.0, numpy 2.4.6, numba 0.65.1, llvmlite 0.47.0.
  - CORRECTION (2026-11-26): these match the Mac mini's package versions EXCEPT numpy. The committed Arb runs used
    Quantum's venv with numpy 2.5.0 (and no numba); 2.4.6 and numba are the repo venv's, which the engine uses.
  - The Python version differs from the Mac mini: the Arb runs there used Quantum's Python 3.13.12; the engine used the
    repo venv's 3.14.5. Python 3.13 is not installed on the Air.
  - `~/GitHub/fleet-air/.venv` (Cuspis) is neither used nor modified.
- **Running:** `job.sh NAME script.sh`, detached. It runs one process at nice 15, under a pause-only guard: SIGSTOP on
  critical memory pressure or free disk < 5 GB, SIGCONT on recovery, nothing ever killed.
- **Outputs** are copied back to the Mac mini and committed there.
- **Second venv, `.venv313` (2026-11-26, the Bridge's ruling):** Homebrew python@3.13 3.13.18 (`/opt/homebrew/opt/python@3.13`;
  3.13.12 is not offered by Homebrew), with python-flint 0.9.0, mpmath 1.3.0, sympy 1.14.0, numpy 2.5.0, the committed
  3.13.12 run's packages. Used by `repro313.sh`. The 3.14 run's outputs were moved to `data/nve/eps/run314/` first.

## Ownership
- **From 2026-11-27 (afternoon), the office ansatz-machine session owns `~/GitHub/ansatz-air`:** the folder, the
  guards (`job.sh`, `fp.sh`), the two running productions (`prod_3_5`, `prod_9_10`) and the new runs at spins 3/10
  and 4/5. This is on Sumit's go, relayed by the Bridge.
- The previous owner was ansatz-machine-personal (now idle). Its runs and records are unchanged.
- Launch records are kept in `logs/<name>.pid` and `logs/guard_<name>.log`, as before.
