#!/usr/bin/env python3
"""Matched-control comparison TS vs Kerr (the Bridge, after milestone 6): bin every scanned level by energy E and by
its distance to the separatrix eps = (|L| - L_sep(E, sign)) / L_sep, where L_sep is the smallest |L| with a closed
equatorial pocket (eps < 0: an open level, connected to the plunge). Per bin: boundary orbits, candidates, A5-CONFIRMED,
and the fd distribution at tol 1e-13 of the candidates. The same L/m sits at different eps in TS and Kerr, so this is
the fair comparison.
    .venv/bin/python scripts/_ts_chaos_matched.py
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np  # noqa: E402

from _ts_chaos_scan import SYSTEMS, _engine, find_Lsep  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
D = os.path.join(ROOT, "data", "ts_chaos")
BINS = [-1.0, -0.6, -0.45, -0.3, -0.15, 0.0, 0.15, 1.0]


def main():
    rows = {}
    for sysname in ("kerr45", "kerr35", "ts45", "ts35"):
        scan = json.load(open(os.path.join(D, f"bscan_{sysname}_v2.json")))
        conf = json.load(open(os.path.join(D, f"bscan_{sysname}_v2_confirm.json")))
        cset = {(round(c["E"], 4), round(c["L"], 4), round(c["x0"], 6)): c for c in conf}
        spec, m, x_in = SYSTEMS[sysname]
        import _ts_chaos_scan as S
        S._ENG = None
        eng = _engine(spec)
        lsep = {}
        for E in scan["Es"]:
            for sign in (+1, -1):
                lsep[(E, sign)] = find_Lsep(eng, E, m, x_in, sign)
        tab = {}
        for lv in scan["levels"]:
            E, L = lv["E"], lv["L"]
            Ls = lsep[(E, 1 if L > 0 else -1)]
            if Ls is None:
                continue
            eps = (abs(L) - abs(Ls)) / abs(Ls)
            b = np.digitize([eps], BINS)[0]
            key = (E, b)
            t = tab.setdefault(key, dict(orbits=0, cand=0, conf=0, fd13=[]))
            for o in lv["orbits"]:
                t["orbits"] += 1
                if o["cand"]:
                    t["cand"] += 1
                    c = cset.get((round(E, 4), round(L, 4), round(o["x0"], 6)))
                    if c:
                        t["fd13"].append(c["fd13"])
                        if c["verdict"] == "CONFIRMED":
                            t["conf"] += 1
        rows[sysname] = tab
    print("matched comparison by (E, eps-bin); eps = (|L| - L_sep)/L_sep; per bin: orbits / candidates / A5-confirmed;"
          " median fd@1e-13 of candidates")
    keys = sorted(set().union(*[set(t) for t in rows.values()]))
    for (E, b) in keys:
        lo, hi = BINS[b - 1] if b >= 1 else -9, BINS[b] if b < len(BINS) else 9
        line = f"  E={E} eps in [{lo:+.2f},{hi:+.2f}):"
        for s in ("kerr45", "ts45", "kerr35", "ts35"):
            t = rows[s].get((E, b))
            if t is None:
                line += f" | {s}: -"
                continue
            med = f"{np.median(t['fd13']):.4f}" if t["fd13"] else "-"
            line += f" | {s}: {t['orbits']}/{t['cand']}/{t['conf']} fd~{med}"
        print(line)
    tot = {s: (sum(t["orbits"] for t in rows[s].values()), sum(t["cand"] for t in rows[s].values()),
               sum(t["conf"] for t in rows[s].values())) for s in rows}
    print("TOTALS (orbits / candidates / A5-confirmed):", {s: v for s, v in tot.items()})
    json.dump({s: {f"{E}|{b}": v for (E, b), v in t.items()} for s, t in rows.items()},
              open(os.path.join(D, "matched_table.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
