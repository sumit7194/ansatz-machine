# The Air run folder for ansatz (ansatz-machine-personal), 2026-11-26

- **Where:** `air:~/GitHub/ansatz-air/`, created for this work. It is not a clone; no commits are made from the Air.
- **Files:** a minimal pinned copy at 43a2de1 (`personal/2026-11-26-route1-check`): the local-import closure of the
  route-(i) scripts plus the five data files they read. Every file's sha256 is in `MANIFEST_43a2de1.sha256`, and all
  46 verified on the Air after unpacking.
- **Environment:** its own venv (`.venv`), Homebrew Python 3.14.10, with `requirements-pinned.txt`: python-flint
  0.9.0, mpmath 1.3.0, sympy 1.14.0, numpy 2.4.6, numba 0.65.1, llvmlite 0.47.0.
  - These match the Mac mini's package versions.
  - The Python version differs from the Mac mini: the Arb runs there used Quantum's Python 3.13.12; the engine used the
    repo venv's 3.14.5. Python 3.13 is not installed on the Air.
  - `~/GitHub/fleet-air/.venv` (Cuspis) is neither used nor modified.
- **Running:** `job.sh NAME script.sh`, detached. It runs one process at nice 15, under a pause-only guard: SIGSTOP on
  critical memory pressure or free disk < 5 GB, SIGCONT on recovery, nothing ever killed.
- **Outputs** are copied back to the Mac mini and committed there.
