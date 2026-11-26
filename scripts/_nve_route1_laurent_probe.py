"""Probe (a) of the P1-P3 cost redo: where the route-(i) Laurent bound stops, between k = 3 and 3.9.

[ansatz-machine-personal, 2026-11-26. Seal: data/nve/route1_check/PROBE_A_SEAL.md, committed before this runs.]

Calls V.laurent(acb(k)) and V.laurent(acb(k), True) of _nve_route1_segment_v2.py UNCHANGED, the evaluator that
v5's prove calls first, at k = 3.0 (a known pass), 3.1 .. 3.8 (the probe), 3.85, and 3.9 (a known failure; a control
that must fail). The spin comes from NVE_SPIN as in every other run. Per k: pass/fail, and on a pass the Cauchy bound M.

A DIAGNOSTIC beside it, not part of any proof: the same 400-arc loop as V.laurent, with the same expressions and
names, recording per arc the balls of 1 - k phi and of s = sqrt(1 - k phi). It reports the arc where s comes closest
to containing 0 (rad(s) / |mid(s)|), whether s contains 0, whether 1 - k phi's real interval reaches <= 0 while its
imaginary interval contains 0 (the principal branch cut), and the first factor that is non-finite. Reading only.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_route1_segment_v2 as V                  # noqa: E402
from flint import acb, arb                           # noqa: E402

KS = ["3", "31/10", "32/10", "33/10", "34/10", "35/10", "36/10", "37/10", "38/10", "385/100", "39/10"]


def arcs(k):
    """V.laurent's arc loop (deriv=True), verbatim in its expressions, with each arc's balls recorded."""
    A, I01 = V.A, V.I01
    rw = arb("0.9") / A
    NA = 400
    out = []
    for j in range(NA):
        th = arb.pi() * (2 * j + 1) / NA + I01 * arb.pi() / NA
        ww = acb(0, th).exp() * rw
        x = ww * ww * (A * A)
        ph = (21 - 18 * x + x * x) / (10 * (3 - x) * (3 - x))
        f = 1 - k * ph
        s = f.sqrt()
        val = ww * ww * ww * ww * (-4 * A) * (3 - x) / ((1 + x) * (1 + x) * (1 + x)) * (ph / (s * 2))
        fm = complex(float(f.real.mid()), float(f.imag.mid()))
        frad = float(f.rad())
        sm = abs(complex(float(s.real.mid()), float(s.imag.mid()))) if s.is_finite() else float("nan")
        srad = float(s.rad()) if s.is_finite() else float("inf")
        cut = (not f.real > 0) and f.imag.contains(0)
        first_bad = next((nm for nm, b in (("x", x), ("phi", ph), ("1-k phi", f), ("s", s), ("val", val))
                          if not b.is_finite()), None)
        out.append(dict(j=j, f=fm, frad=frad, s_abs=sm, srad=srad, s_has0=bool(s.contains(0)), cut=bool(cut),
                        first_bad=first_bad, val_finite=bool(val.is_finite())))
    return out


def main():
    print(f"== probe (a): V.laurent at k = 3 .. 3.9 == spin {V.SPIN}; python {sys.version.split()[0]}; "
          f"python-flint {__import__('flint').__version__}; prec {__import__('flint').ctx.prec}")
    for ks in KS:
        k = acb(arb(ks.split("/")[0]) / arb(ks.split("/")[1])) if "/" in ks else acb(int(ks))
        res = []
        for deriv in (False, True):
            try:
                _d, M, _rw = V.laurent(k, deriv)
                res.append(f"pass (M <= {V.hi_sci(M)})")
            except RuntimeError as e:
                res.append(f"FAIL ({e})")
        A = arcs(k)
        worst = max(A, key=lambda a: a["srad"] / a["s_abs"] if a["s_abs"] == a["s_abs"] and a["s_abs"] > 0 else float("inf"))
        nbad = sum(not a["val_finite"] for a in A)
        bad = [a for a in A if not a["val_finite"]]
        print(f"k = {ks}: laurent {res[0]}; deriv {res[1]}")
        print(f"   arcs with a non-finite deriv value: {nbad}; with s containing 0: {sum(a['s_has0'] for a in A)}; "
              f"with 1 - k phi on the branch cut: {sum(a['cut'] for a in A)}; min Re(1 - k phi) at the arc centres "
              f"{min(a['f'].real for a in A):+.5f}")
        w = worst
        print(f"   worst arc {w['j']}: 1 - k phi = {w['f']:.5f} +/- {w['frad']:.2e}; |s| {w['s_abs']:.4f} +/- {w['srad']:.2e}; "
              f"s contains 0 {w['s_has0']}; on the cut {w['cut']}; first non-finite factor {w['first_bad']}")
        for a in bad[:3]:
            print(f"   failing arc {a['j']}: 1 - k phi = {a['f']:.5f} +/- {a['frad']:.2e}; |s| {a['s_abs']:.4f} +/- "
                  f"{a['srad']:.2e}; s contains 0 {a['s_has0']}; on the cut {a['cut']}; first non-finite {a['first_bad']}")
    print("== PROBE_A_DONE")


if __name__ == "__main__":
    main()
