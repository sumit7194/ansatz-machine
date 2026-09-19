#!/usr/bin/env python3
"""Bridge to the Rust nullspace solver (rust/ktsolve), with a validation suite.

The Rust binary runs as its own process: Python writes the matrix to a binary file, runs
`ktsolve`, reads the nullspace back. That keeps the heavy solve out of Python's memory, lets the
solve be paused and resumed from outside (kill -STOP / kill -CONT), and lets its thread count be
chosen per run -- few on weekdays while the machine is in use, more at weekends.

VALIDATION RULE, same as _kt_fast: the free-column-indexed nullspace basis is unique, so the Rust
port must reproduce the numba reference and the original solver vector for vector, and must give
the same answer at every thread count. Anything else is a bug, not a different valid answer.
"""
import json
import os
import subprocess
import sys
import tempfile
import time

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _kt_fast import P, _coo_from_col_dicts  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
BINARY = os.path.join(HERE, "..", "rust", "ktsolve", "target", "release", "ktsolve")


def write_ktm(path, ri, ci, vi, nrows, ncols, p=P):
    with open(path, "wb") as f:
        f.write(b"KTM1")
        f.write(np.array([nrows, ncols, ri.shape[0], p], dtype="<u8").tobytes())
        f.write(ri.astype("<u4").tobytes())
        f.write(ci.astype("<u4").tobytes())
        f.write(vi.astype("<u4").tobytes())


def read_kts(path):
    with open(path, "rb") as f:
        if f.read(4) != b"KTS1":
            raise ValueError(f"{path} is not a KTS1 result file")
        ncols, nfree = np.frombuffer(f.read(16), dtype="<u8")
        free = np.frombuffer(f.read(8 * int(nfree)), dtype="<u8")
        vecs = np.frombuffer(f.read(4 * int(nfree) * int(ncols)), dtype="<u4")
    vecs = vecs.reshape(int(nfree), int(ncols)).astype(np.int64)
    return [int(x) for x in free], list(vecs)


def nullspace_rust(col_dicts, ncols, p=P, threads=1, verbose=False, label="", workdir=None):
    """Drop-in replacement for nullspace_fast / nullspace_sparse: returns (vectors, stats)."""
    if not os.path.exists(BINARY):
        raise FileNotFoundError(f"{BINARY} missing -- build it: cargo build --release in rust/ktsolve")
    ri, ci, vi, nrows = _coo_from_col_dicts(col_dicts, p)
    with tempfile.TemporaryDirectory(dir=workdir) as d:
        mpath, spath = os.path.join(d, "m.ktm"), os.path.join(d, "ns.kts")
        write_ktm(mpath, ri, ci, vi, nrows, ncols, p)
        out = subprocess.run([BINARY, "--input", mpath, "--output", spath, "--threads", str(threads)],
                             capture_output=True, text=True)
        if out.returncode != 0:
            raise RuntimeError(f"ktsolve failed ({out.returncode}): {out.stderr.strip()}")
        stats = json.loads(out.stdout.strip().splitlines()[-1])
        _, vecs = read_kts(spath)
    if verbose:
        print(f"    {label}rust nullspace: {stats['blocks']} blocks (largest {stats['largest_block_cols']} "
              f"cols), nnz {stats['nnz_in']:,} -> peak {stats['peak_nnz_max']:,}, nullity "
              f"{stats['nullity']}, {threads} thread(s), {stats['seconds']:.1f}s", flush=True)
    return vecs, stats


if __name__ == "__main__":
    from _kt_fast import nullspace_fast
    from _kt_sparse import nullspace_sparse

    rng = np.random.default_rng(7)
    ok = True

    def rand_cols(nkeys, ncols, lo, hi, off=0):
        out = []
        for _ in range(ncols):
            d = {}
            for _ in range(int(rng.integers(lo, hi + 1))):
                d[("k", int(rng.integers(0, nkeys)) + off)] = int(rng.integers(1, P))
            out.append(d)
        return out

    def same(a, b):
        return len(a) == len(b) and all(np.array_equal(x % P, y % P) for x, y in zip(a, b))

    def check(name, cols, with_old=True):
        global ok
        n = len(cols)
        ref, _ = nullspace_fast(cols, n)
        r1, s1 = nullspace_rust(cols, n, threads=1)
        r4, s4 = nullspace_rust(cols, n, threads=4)
        line = (f"  {name:32s} nullity {len(r1):5d}  rust==numba {same(r1, ref)}  "
                f"1thr==4thr {same(r1, r4)}  blocks {s1['blocks']:3d}  rust {s1['seconds']:.3f}s")
        good = same(r1, ref) and same(r1, r4)
        if with_old:
            old, _ = nullspace_sparse(cols, n, P, track=False)
            line += f"  rust==old {same(r1, old)}"
            good &= same(r1, old)
        print(line, flush=True)
        ok &= good

    print("VALIDATION: Rust vs the numba reference and the original solver (identical vectors)\n")
    check("tall, ~7 nz/col", rand_cols(160, 400, 3, 11))
    check("wide, big nullspace", rand_cols(120, 500, 2, 8))
    check("dense-ish", rand_cols(80, 150, 20, 40))
    a, b = rand_cols(100, 250, 2, 7, 0), rand_cols(100, 250, 2, 7, 10_000)
    check("interleaved 2 blocks", [x for pr in zip(a, b) for x in pr])
    blocks4 = [rand_cols(300, 700, 2, 8, 10_000 * k) for k in range(4)]
    check("interleaved 4 blocks", [x for grp in zip(*blocks4) for x in grp])
    withempty = rand_cols(90, 200, 2, 7)
    for j in (0, 17, 199):
        withempty[j] = {}
    check("with empty columns", withempty)
    check("larger (numba ref only)", rand_cols(4000, 9000, 3, 9), with_old=False)
    print("\n  " + ("VALIDATED: Rust reproduces both reference solvers exactly, at 1 and 4 threads."
                    if ok else "FAILED -- do not use"))
    sys.exit(0 if ok else 1)
