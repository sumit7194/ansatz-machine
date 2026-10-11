#!/usr/bin/env python3
"""Environment stamp, for reproducibility (fleet policy 2026-10-11: "someone needs to be able to replicate it").

stamp() returns a JSON-able dict that can be embedded in any results file:
- the interpreter (version, executable), platform and macOS version, the git commit and dirty flag;
- the versions of numpy, scipy, sympy, mpmath, numba and llvmlite;
- the BLAS/LAPACK backend of BOTH numpy and scipy;
- the native toolchains: rustc/cargo, FLINT/GMP/MPFR (Homebrew), and the dylibs that native/flint_rank links.

    .venv/bin/python scripts/envstamp.py            # writes ENVIRONMENT/stamp.json and ENVIRONMENT/requirements-lock.txt
"""
import importlib
import json
import os
import platform
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _run(cmd):
    try:
        return subprocess.run(cmd, capture_output=True, text=True, cwd=ROOT, timeout=60).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def _blas(modname):
    try:
        m = importlib.import_module(modname)
        cfg = m.show_config(mode="dicts")
        deps = cfg.get("Build Dependencies", {})
        return {k: {kk: v.get(kk) for kk in ("name", "version", "found") if kk in v} for k, v in deps.items()
                if k in ("blas", "lapack")}
    except Exception as e:                                  # noqa: BLE001 -- a stamp must never crash a run
        return f"unavailable: {type(e).__name__}"


def stamp():
    pk = {}
    for name in ("numpy", "scipy", "sympy", "mpmath", "numba", "llvmlite"):
        try:
            pk[name] = importlib.import_module(name).__version__
        except Exception:                                    # noqa: BLE001
            pk[name] = None
    return {
        "python": sys.version.split()[0],
        "executable": sys.executable,
        "executable_resolved": os.path.realpath(sys.executable),
        "platform": platform.platform(),
        "machine": platform.machine(),
        "macos": platform.mac_ver()[0] or None,
        "git_commit": _run(["git", "rev-parse", "HEAD"]),
        "git_dirty": bool(_run(["git", "status", "--porcelain", "--untracked-files=no"])),
        "packages": pk,
        "blas_lapack": {"numpy": _blas("numpy"), "scipy": _blas("scipy")},
        "native": {
            "rustc": _run(["rustc", "-V"]),
            "cargo": _run(["cargo", "-V"]),
            "brew": _run(["brew", "list", "--versions", "flint", "gmp", "mpfr"]),
            "flint_rank_links": _run(["otool", "-L", os.path.join(ROOT, "native", "flint_rank")]),
        },
    }


def main():
    out = os.path.join(ROOT, "ENVIRONMENT")
    os.makedirs(out, exist_ok=True)
    s = stamp()
    with open(os.path.join(out, "stamp.json"), "w") as fh:
        json.dump(s, fh, indent=1)
    lock = _run([sys.executable, "-m", "pip", "freeze"])
    with open(os.path.join(out, "requirements-lock.txt"), "w") as fh:
        fh.write(f"# pip freeze of {os.path.realpath(sys.executable)} (Python {s['python']}), at {s['git_commit']}\n")
        fh.write((lock or "") + "\n")
    print(json.dumps({k: s[k] for k in ("python", "macos", "git_commit", "packages")}, indent=1))
    print("BLAS/LAPACK:", json.dumps(s["blas_lapack"]))


if __name__ == "__main__":
    main()
