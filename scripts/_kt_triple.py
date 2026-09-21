#!/usr/bin/env python3
"""Build a sealed A/B/C triple: matched deformations of Kerr differing ONLY in how Carter survives.

WHAT IT IS FOR. Another session has a legibility screen that reports "representable to degree N with
margin M" and has never met an object whose ground truth is owned elsewhere. This supplies one:
three deformations from the SAME family -- l=2 shape slots (l2tt, l2rr, l2ang) with 1/r^k radial
profiles -- same coordinates, same angular patterns, comparable magnitudes, differing only in the
property under test.

    A   keeps Carter exactly            (in the rank-2 compatible space, §139)
    B   does not keep Carter at all     (same span, outside that subspace)
    C   keeps Carter only RATIONALLY    (pole order 1: dies at rank 2, Q^2 survives at rank 4, §141)

WHY MATCHING MATTERS MORE THAN THE OBJECTS. If B differed from A in fall-off or multipole content as
well, their screen could separate the two for a reason unrelated to Carter and it would read as
success -- a test that can only pass. So A and B are drawn from the SAME span with the same support,
and every verdict below is re-measured ON THE EXACT OBJECTS EMITTED rather than inherited from the
ancestors they were derived from. An ancestor is not the object.

THE KEY IS COMMITTED HERE AND THE RELAY NEVER SEES IT. Labels are permuted by a seed printed only
into the key file.

Repro:  .venv/bin/python scripts/_kt_triple.py [--prime 0]
"""
import os
import random
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402
import sympy as sp  # noqa: E402

import _kt_double as KD  # noqa: E402
from _kt_carter_space import arg, build_space, compatible_space, setup, x, y  # noqa: E402
from _kt_q2_candidate import combine  # noqa: E402

chi = KD.chi
FAMILY = ("l2tt", "l2rr", "l2ang")
KMAX = 6
D1 = {"l2rr_3": 1, "l2ang_3": 1, "l2ang_4": sp.Rational(3, 2)}     # pole order 1 (§140)


def slot_table(GI):
    names, gis, roles = build_space(GI, KMAX, slots=FAMILY)
    keep = [i for i, r_ in enumerate(roles) if r_ == "slot"]
    return [names[i] for i in keep], [gis[i] for i in keep]


if __name__ == "__main__":
    t0 = time.time()
    prime = arg("--prime", 0)
    ctx = setup(2, 8, 10, prime)
    names, gis = slot_table(ctx["GI"])
    print(f"family {FAMILY} x 1/r^1..{KMAX}: {len(names)} slots, rank 2, prime {prime} "
          f"[{time.time()-t0:.0f}s]", flush=True)

    W = compatible_space(ctx, names, gis)
    print(f"  Carter-compatible subspace: dim {W.shape[0]} of {len(names)}", flush=True)
    if W.shape[0] == 0:
        sys.exit("no compatible directions in this family -- cannot build A")

    p = ctx["p"]
    from _kt_carter_space import ratrec
    def to_rat(vec):
        out = {}
        for nm, c in zip(names, vec):
            c = int(c) % p
            if c:
                q = ratrec(c, p)
                out[nm] = sp.Rational(q[0], q[1]) if q else sp.Integer(c)
        return out

    A_coef = to_rat(W[0])
    # B: same span, same support pattern, but OUTSIDE the compatible subspace. Built by perturbing
    # one coefficient of A, then CHECKED to be outside rather than assumed to be.
    rng = random.Random(20260922)
    B_coef = dict(A_coef)
    bump = sorted(B_coef)[len(B_coef) // 2]
    B_coef[bump] = sp.nsimplify(B_coef[bump] + sp.Rational(1, 3))
    C_coef = {k: sp.Rational(v) for k, v in D1.items()}

    print(f"\n  A (keeps Carter)        : {A_coef}", flush=True)
    print(f"  B (A with {bump} bumped) : {B_coef}", flush=True)
    print(f"  C (rational, pole 1)    : {C_coef}", flush=True)

    idx = {nm: i for i, nm in enumerate(names)}
    def build(coef):
        w = [sp.Rational(coef.get(nm, 0)) for nm in names]
        return combine(gis, w)

    print("\n  RE-VERIFYING each on the exact object emitted:", flush=True)
    verdict = {}
    for lab, coef in (("A", A_coef), ("B", B_coef), ("C", C_coef)):
        Wl = compatible_space(ctx, [lab], [build(coef)])
        verdict[lab] = int(Wl.shape[0])
        print(f"    {lab}: Carter survives at rank 2 = {Wl.shape[0] == 1}", flush=True)
    ok = verdict["A"] == 1 and verdict["B"] == 0 and verdict["C"] == 0
    print(f"\n  matched pair valid (A keeps, B does not, C does not): {ok}", flush=True)
    if not ok:
        sys.exit("the triple is not correctly differentiated -- not emitting it")

    # ---- emit the metrics, labels permuted ----
    t_, r_, th_, ph_ = sp.symbols("t r theta phi", real=True)
    eps, a_ = sp.symbols("epsilon a", real=True)
    def metric_text(coef):
        from _kt_carter_space import slot_h
        h = sp.zeros(4, 4)
        for nm, c in coef.items():
            slot, k = nm.rsplit("_", 1)
            h += sp.Rational(c) * slot_h(slot, x ** -int(k))
        Sig = r_**2 + a_**2 * sp.cos(th_)**2
        Dl = r_**2 - 2 * r_ + a_**2
        g = sp.zeros(4, 4)
        g[0, 0] = -(1 - 2 * r_ / Sig)
        g[0, 3] = g[3, 0] = -2 * a_ * r_ * sp.sin(th_)**2 / Sig
        g[1, 1] = Sig / Dl
        g[2, 2] = Sig
        g[3, 3] = (r_**2 + a_**2 + 2 * a_**2 * r_ * sp.sin(th_)**2 / Sig) * sp.sin(th_)**2
        conv = {x: r_, y: sp.cos(th_), chi: a_}
        lines = []
        for i, j in ((0, 0), (0, 3), (1, 1), (2, 2), (3, 3)):
            e = sp.cancel(sp.together(g[i, j] + eps * h[i, j].subs(conv)))
            if i == 2:      # h_yy -> h_(theta theta)
                e = sp.cancel(sp.together(g[i, j] + eps * h[i, j].subs(conv) * sp.sin(th_)**2))
            lines.append(f"g[{i}][{j}] = {sp.sstr(sp.simplify(e))}")
        return "\n".join(lines)

    perm = ["A", "B", "C"]
    rng.shuffle(perm)
    payload = {}
    for out_lab, src in zip(("A", "B", "C"), perm):
        payload[out_lab] = metric_text({"A": A_coef, "B": B_coef, "C": C_coef}[src])
    os.makedirs("data/triple", exist_ok=True)
    with open("data/triple/objects.txt", "w") as fh:
        fh.write("Three stationary axisymmetric metrics, coordinates (t, r, theta, phi),\n"
                 "spin parameter a, deformation parameter epsilon. Components not listed are zero.\n"
                 "g[0][3] = g[3][0]. No further information is supplied.\n")
        for lab in ("A", "B", "C"):
            fh.write(f"\n===== OBJECT {lab} =====\n{payload[lab]}\n")
    with open("data/triple/KEY.txt", "w") as fh:
        fh.write("SEALED KEY -- do not transmit.\n")
        fh.write(f"emitted {time.strftime('%Y-%m-%d %H:%M:%S')}, permutation seed 20260922\n")
        fh.write(f"label mapping (emitted -> truth): {dict(zip(('A','B','C'), perm))}\n")
        fh.write(f"truth A = keeps Carter exactly (rank-2 compatible), coefficients {A_coef}\n")
        fh.write(f"truth B = does NOT keep Carter, coefficients {B_coef}\n")
        fh.write(f"truth C = keeps Carter only rationally, pole order 1, coefficients {C_coef}\n")
        fh.write(f"re-verified on the emitted objects: {verdict}\n")
    print(f"\n  wrote data/triple/objects.txt and data/triple/KEY.txt", flush=True)
    print(f"  total {time.time()-t0:.0f}s")
