#!/usr/bin/env python3
"""Figure data for the paper: the certified lower bound on |F| = |tr[M1, M0] - 2| per route-(i) segment.

Reads the committed production logs straight from git (branch personal/2026-11-26-route1-check), so the figure is
reproducible from the repository alone:
    python3 paper/make_figure_data.py            # writes paper/fig_bounds_3_5.dat and paper/fig_bounds_3_10.dat
Dyadic (F/k^2) segments certify |F/k^2| >= b on [k_lo, k_hi]; they are plotted as |F| >= b * k_lo^2 (a valid, slightly
weaker bound). Each segment is a horizontal step; blank lines separate the steps.
"""
import os
import re
import subprocess
from fractions import Fraction

BRANCH = "personal/2026-11-26-route1-check"
SRC = {"3_5": "data/nve/route1_check/air_prod_3_5/data/nve/eps/route1_prod_3_5.out",
       "3_10": "data/nve/route1_check/air_prod_3_10/data/nve/eps/route1_prod_3_10.out"}
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PAT = re.compile(r"CERTIFIED \[([0-9/]+), ([0-9/]+)\]: n = (\d+), \|f\| >= ([0-9.]+)")


def main():
    for tag, path in SRC.items():
        text = subprocess.run(["git", "-C", ROOT, "show", f"{BRANCH}:{path}"], check=True, capture_output=True,
                              text=True).stdout
        segs = {}
        for line in text.splitlines():
            m = PAT.search(line)
            if not m or not line.startswith("["):
                continue
            lo, hi, b = Fraction(m.group(1)), Fraction(m.group(2)), float(m.group(4))
            fk2 = hi <= Fraction(1, 10) and lo < Fraction(1, 10) and hi != Fraction(1, 5)
            bound = b * float(lo) ** 2 if fk2 else b
            segs[(lo, hi)] = bound                      # a resumed segment logs twice; the values are identical
        out = os.path.join(ROOT, "paper", f"fig_bounds_{tag}.dat")
        with open(out, "w") as f:
            f.write("k bound\n")
            for (lo, hi), bound in sorted(segs.items()):
                f.write(f"{float(lo):.6g} {bound:.6g}\n{float(hi):.6g} {bound:.6g}\n\n")
        print(f"{tag}: {len(segs)} segments, k in [{float(min(segs)[0]):.6g}, {float(max(segs)[1]):.6g}] -> {out}")


if __name__ == "__main__":
    main()
