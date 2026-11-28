#!/usr/bin/env python3
"""Controls for the base2 fix (C2 ruling (B); data/nve/route1_check/C2_B2FIX_REGISTRATION.md). Fast, no CAPD:
  B1 (must-fail)  the OLD base2 (the committed code at 408b56e, exec'd from git) refuses at k = 30/7 - 5e-6
                  (Pend's mechanism), and returns a non-finite value at 30/7 - 1e-5. The NEW one is finite at both.
  B2 (truth)      at point k = 30/7 - d, d in {1e-3, 1e-5, 1e-6, 1e-9, 1e-11, 7e-15}, the NEW enclosures contain an
                  independent Arb quadrature (acb.integral, rel_tol 2^-60) of the same two integrals.
  B3 (agreement)  where the old code is finite (d = 1e-3, and P3's 25 R/5 cover cells), old and new enclosures overlap;
                  the old code is non-finite exactly on P3's two refined cells (L0_21, L0_23), where its NaN failed closed.
  B4 (cells)      the worst R/5 cover cell (nearest 30/7, on and off the real axis) of every dyadic segment j = 1..27 gives
                  a finite enclosure, so H1 no longer refuses there.
(The fifth control, P3 still certifying with the changed code, is a full C2-M pilot run: air/c2m_pilot.sh P3 from
this worktree, recorded separately.)
    BOX=P3 <P3's R1_* env> .venv313/bin/python -I -u scripts/_nve_base2_fix_controls.py
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import _nve_route1_segment_v7B as N        # noqa: E402
from flint import acb, arb                  # noqa: E402

ROOT = os.path.dirname(HERE)
OUT = os.path.join(ROOT, "data", "nve", "route1_check", "c2", "b2fix_controls.json")
K30 = arb(30) / 7


def old_base2():
    src = subprocess.run(["git", "-C", ROOT, "show", "408b56e:scripts/_nve_route1_segment_v7B.py"],
                         capture_output=True, text=True, check=True).stdout
    i0, i1 = src.index("def base2(K):"), src.index("LAST = dict(refused=None)")
    ns = dict(N.__dict__)
    ns["_BASE2"] = {}
    exec(src[i0:i1], ns)
    return ns["base2"], ns["_BASE2"]


def new(K):
    N._BASE2.clear()
    return N.base2(K)


def finite(b):
    return b is not None and all(x.is_finite() for x in b)


def quad(K):
    lim, a2 = 1 / N.BB, N.A * N.A

    def f(weight):
        def g(s, analytic):
            a2s2 = a2 * s * s
            P = (90 - 21 * K) - (60 - 18 * K) * a2s2 + (10 - K) * a2s2 * a2s2
            if analytic and not (P.real > 0):
                return acb("nan")
            dP = -21 + 18 * a2s2 - a2s2 * a2s2
            return weight(s) * (-(dP * dP) / (4 * P * P.sqrt())) / ((1 + a2s2) ** 3)
        return g
    I1 = acb.integral(f(lambda s: s * s), 0, lim, rel_tol=arb(2) ** -60)
    I0 = acb.integral(f(lambda s: s - N.BB * s * s), 0, lim, rel_tol=arb(2) ** -60)
    return N.K8 * I1, -N.K8 * I0


def main():
    ob, ocache = old_base2()
    rec = {}
    # B1
    ocache.clear()
    o5 = ob(acb(K30 - arb("5e-6")))
    ocache.clear()
    o1 = ob(acb(K30 - arb("1e-5")))
    rec["B1"] = dict(old_refuses_5e6=o5 is None, old_nonfinite_1e5=(o1 is not None and not finite(o1)),
                     new_finite_5e6=finite(new(acb(K30 - arb("5e-6")))), new_finite_1e5=finite(new(acb(K30 - arb("1e-5")))))
    rec["B1"]["pass"] = all(rec["B1"].values())
    # B2
    b2 = {}
    for d in ("1e-3", "1e-5", "1e-6", "1e-9", "1e-11", "7e-15"):
        K = acb(K30 - arb(d))
        ref, bn = quad(K), new(K)
        b2[d] = dict(contains=[bool(b.contains(r)) for b, r in zip(bn, ref)],
                     overestimate=[float(b.rad() / abs(r.real.mid())) for b, r in zip(bn, ref)])
    rec["B2"] = dict(points=b2, pass_=all(all(v["contains"]) for v in b2.values()))
    # B3: d = 1e-3 and P3's 25 R/5 cells (k_c 59979/14000, half 1/2000, rho 4)
    pairs = [acb(K30 - arb("1e-3"))]
    kc = arb(59979) / 14000
    R = (arb(1) / 2000 * (arb(4) + arb(1) / 4) / 2)
    _K, subs = N.V.kbox(acb(kc), R)
    pairs += [acb(kc) + d for d in subs]
    agree, old_nonfinite = [], []
    for i, K in enumerate(pairs):
        ocache.clear()
        bo, bn = ob(K), new(K)
        if not finite(bn):
            agree.append(False)
        elif finite(bo):
            agree.append(bool(all(x.overlaps(y) for x, y in zip(bo, bn))))
        else:
            old_nonfinite.append(i - 1)            # an R/5 cell index (i = 0 is the point d = 1e-3)
    # the old code's NaN (the second artefact) on P3's own cells: P3's cover refused exactly L0_21 and L0_23 and refined
    # them (C2_M_P3_RESULT.md, the c2m_P3_cellL0_21.* / L0_23.* records), so the old NaN failed closed there
    rec["B3"] = dict(n=len(pairs), compared=len(agree), overlap_where_old_finite=all(agree),
                     old_nonfinite_cells=old_nonfinite, matches_P3_refined=old_nonfinite == [21, 23],
                     pass_=all(agree) and old_nonfinite == [21, 23])
    # B4
    b4 = {}
    for j in range(1, 28):
        d = arb(1) / (1000 * 2 ** j)
        kcj = K30 - 3 * d / 2
        Rj = d / 2 * (arb(4) + arb(1) / 4) / 2
        hs = Rj / 5
        c = kcj + 4 * hs
        b4[j] = [finite(new(acb(c, im * hs) + hs * acb(arb(0, 1), arb(0, 1)))) for im in (0, 4)]
    rec["B4"] = dict(cells=b4, pass_=all(all(v) for v in b4.values()))
    rec["verdict"] = "PASS" if all(rec[k].get("pass", rec[k].get("pass_")) for k in ("B1", "B2", "B3", "B4")) else "FAIL"
    json.dump(rec, open(OUT, "w"), indent=1)
    print(f"base2-fix controls: {rec['verdict']}; B1 {rec['B1']['pass']}; B2 {rec['B2']['pass_']}; "
          f"B3 {rec['B3']['pass_']} ({rec['B3']['n']} k-sets); B4 {rec['B4']['pass_']}", flush=True)


if __name__ == "__main__":
    main()
