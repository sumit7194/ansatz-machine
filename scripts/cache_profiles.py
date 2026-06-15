#!/usr/bin/env python3
"""Backfill curvature-invariant profiles into catalog_discoveries.json,
one family at a time, writing after each.

Why this exists: build_catalog() in 02_fingerprints.py self-heals missing
profiles but writes the file only ONCE at the very end, so an interrupted
run (the high-dimension Kretschmann is minutes-to-an-hour per family)
persists nothing. This computes each profile via the SAME CatalogEntry
path and writes immediately — resumable: re-running skips families that
already have a profile, so a kill loses only the family in flight.

Easiest (lowest-dimension) families first, so quick wins land before the
expensive 12+1 rungs. Run detached for long backfills:
    nohup .venv/bin/python -u scripts/cache_profiles.py >> cache.log 2>&1 &
"""

import importlib.util
import json
import os
import sys
import time

import sympy as sp


def _atomic_write_json(path, data):
    """Write to a temp file in the same dir, then os.replace() — an
    atomic swap on POSIX. A power loss leaves either the old complete
    file or the new complete file, never a truncated one (the failure
    that nearly cost us the catalog, 2026-06-13)."""
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(data, fh, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)

_here = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _here)  # gr_engine resolves as if run from scripts/

_spec = importlib.util.spec_from_file_location(
    "fingerprints", os.path.join(_here, "02_fingerprints.py"))
fp = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(fp)

PATH = fp.DISCOVERIES_PATH
# leave headroom on the (shared, interactive) dev box; override with env
WORKERS = int(os.environ.get("CACHE_WORKERS", "4"))
# optional dimension window, for splitting work across machines:
# CACHE_NMAX caps the largest n this run will attempt (e.g. keep the
# power-risky multi-hour giants off a machine that loses power); CACHE_NMIN
# floors it. 0 = unbounded.
NMAX = int(os.environ.get("CACHE_NMAX", "0"))
NMIN = int(os.environ.get("CACHE_NMIN", "0"))


def _compute_profile(d):
    """Compute one family's (R, K, G1) fingerprint. Runs in a worker
    process — pure compute, NO file writing (the parent is the only
    writer, so concurrent workers can't race on the catalog file)."""
    t0 = time.time()
    psym = sp.Symbol(d["params"][0], real=True)
    f = sp.sympify(d["f"], locals={"r": fp.R_SYM, d["params"][0]: psym})
    metric, coords, _ = fp.build_ansatz_metric(d["n"], f)
    entry = fp.CatalogEntry(d["name"], metric, coords, shape_param=psym)
    profile = {"R": sp.srepr(entry.profile.R),
               "K": sp.srepr(entry.profile.K),
               "G1": sp.srepr(entry.profile.G1)}
    return d["name"], profile, time.time() - t0


def main():
    import multiprocessing as mp

    with open(PATH) as fh:
        data = json.load(fh)

    by_name = {d["name"]: d for d in data}
    todo = [d for d in data
            if "profile" not in d and len(d.get("params", [])) == 1
            and (NMAX == 0 or d["n"] <= NMAX)
            and (NMIN == 0 or d["n"] >= NMIN)]
    # smallest dimension first: the cheap families bank within minutes, so
    # a power loss costs only the in-flight giants — never the easy wins
    # already saved. (Measured: an n=12 family takes ~2.2h; n=13 far more.)
    todo.sort(key=lambda d: d["n"])
    if not todo:
        print("all families already have cached profiles — nothing to do")
        return 0

    workers = max(1, min(WORKERS, len(todo)))
    print(f"caching {len(todo)} missing profile(s) of {len(data)} families "
          f"on {workers} worker(s)...", flush=True)
    t_all = time.time()
    ctx = mp.get_context("fork")  # children inherit the loaded SymPy modules
    done = 0
    with ctx.Pool(workers) as pool:
        for name, profile, secs in pool.imap_unordered(_compute_profile, todo):
            by_name[name]["profile"] = profile
            # single writer (the parent), atomic swap: a kill or power loss
            # loses at most the families still computing, never the file.
            _atomic_write_json(PATH, data)
            done += 1
            print(f"  [{done}/{len(todo)}] {name[:50]} ({secs:.0f}s)",
                  flush=True)

    print(f"done — {len(todo)} profiles cached in "
          f"{time.time() - t_all:.0f}s", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
