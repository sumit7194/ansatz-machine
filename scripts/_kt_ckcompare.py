#!/usr/bin/env python3
"""Compare two solver checkpoints: is a rerun on the new solver IDENTICAL to the legacy run?

Checkpoints store every chain (and, for the zeta tower, every zeta-chain) as srepr strings. The
chains are built from nullspace basis vectors, and that basis is unique, so a correct new solver
must reproduce them. Two levels of check:

  1. exact string equality of every stored expression -- the strong test;
  2. for any that differ as strings, the difference evaluated at random rational points mod p --
     SymPy can print one expression two ways, and that is not a solver disagreement.

SAFE LOADING. The checkpoint files are this repo's own pickles, but they are read here through an
unpickler that refuses every class lookup: the files only ever contain lists, dicts, strings and
ints, which need none, so a tampered file fails loudly instead of executing anything.

Usage:  _kt_ckcompare.py NEW.pkl LEGACY.pkl
"""
import io
import pickle
import random
import sys

import sympy as sp

P = 2147483647


class _PlainDataOnly(pickle.Unpickler):
    def find_class(self, module, name):
        raise pickle.UnpicklingError(f"refusing to load {module}.{name}: checkpoints are plain data")


def load(path):
    with open(path, "rb") as f:
        d = _PlainDataOnly(io.BytesIO(f.read())).load()
    if isinstance(d, dict):
        return {"chains": d["chains"], "zchains": d["zchains"], "zdim": d["zdim"]}
    return {"chains": d, "zchains": None, "zdim": None}


def flat(obj, prefix=""):
    """(path, string) for every stored expression, in a fixed order."""
    out = []
    for k, ch in enumerate(obj):
        for lvl, row in enumerate(ch):
            for mi, e in enumerate(row):
                out.append((f"{prefix}[{k}][{lvl}][{mi}]", e))
    return out


def numerically_equal(a, b, trials=3):
    diff = sp.sympify(a) - sp.sympify(b)
    syms = sorted(diff.free_symbols, key=str)
    rng = random.Random(12345)
    for _ in range(trials):
        pt = {s: sp.Rational(rng.randint(3, 10**6), rng.randint(3, 10**6)) for s in syms}
        num, _ = sp.fraction(sp.together(diff.subs(pt)))
        if int(num) % P != 0:
            return False
    return True


def main(new_path, old_path):
    new, old = load(new_path), load(old_path)
    ok = True
    if new["zdim"] != old["zdim"]:
        print(f"  zdim differs: new {new['zdim']} vs legacy {old['zdim']}")
        ok = False
    for name in ("chains", "zchains"):
        if new[name] is None and old[name] is None:
            continue
        a, b = flat(new[name], name), flat(old[name], name)
        if len(a) != len(b):
            print(f"  {name}: different shape ({len(a)} vs {len(b)} expressions)")
            ok = False
            continue
        exact = sum(1 for (_, x), (_, y) in zip(a, b) if x == y)
        differ = [(pa, x, y) for (pa, x), (_, y) in zip(a, b) if x != y]
        bad = [pa for pa, x, y in differ if not numerically_equal(x, y)]
        print(f"  {name}: {len(a)} expressions, {exact} identical as strings, "
              f"{len(differ) - len(bad)} equal numerically, {len(bad)} DIFFERENT")
        if bad:
            print(f"    first differing: {bad[:5]}")
            ok = False
    print("  " + ("IDENTICAL to legacy." if ok else "MISMATCH -- the new solver disagrees."))
    return ok


if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1], sys.argv[2]) else 1)
