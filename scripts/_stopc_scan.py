#!/usr/bin/env python3
"""Stop-(c) scan at spin 9/10 (seal: data/nve/route1_check/CLOSURE_STOPC_SEAL.md §3). Float only, no certificate.

Region A's own machinery: Laurent c0 for complex k (_nve_lower_kc.ProblemC), the outer singular points r+-, p+-
tracked by Newton from Kerr's (as _nve_spin_scan), the capsule lasso built at the real k_c exactly as LauA.loops, and
the circle R0 = 1.2639. For k on a 9 x 9 grid over the route-(i) square [k_c +- R] x [+-R]i, R = (1/20)(4 + 1/4)/2:
  - max |w_root(k)| (B's roots; the route-(i) Laurent precondition needs < 1/0.81) and rho_c;
  - the tracked points' distances to the circle and the lasso;
  - zeros of G1 and G2 in r_in < |z| < 2.5 (r_in = max(1.05, rho_c + 0.12)), counted by winding and located by Newton
    from a grid, with their distances to the circle and the lasso.
    NVE_SPIN=9/10 python scripts/_stopc_scan.py [k_c ...]      (default 2 2.5 3; one process per k_c in parallel)
"""
import os
import sys
import time

os.environ.setdefault("NVE_SPIN", "9/10")
import mpmath as mp                      # noqa: E402

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_lower as L                   # noqa: E402
import _nve_lower_kc as KC               # noqa: E402
import _nve_spin_scan as SS              # noqa: E402

assert SS.SPIN == "9/10", SS.SPIN
mp.mp.dps = 50                        # the Laurent builder's relative thresholds (1e-35) need 50 digits
R0 = mp.mpf("1.2639")
HALF = mp.mpf(1) / 20
RSQ = HALF * (4 + mp.mpf(1) / 4) / 2
CIRCLE = L.arc(R0, 0, 2 * mp.pi, mp.pi / 180)
GRID = 9
RMAX = mp.mpf("2.5")


def wmax(k):
    a_, b_, c_ = 90 - 21 * k, -(60 - 18 * k), 10 - k
    d = mp.sqrt(b_ * b_ - 4 * a_ * c_)
    return max(abs((-b_ + d) / (2 * a_)), abs((-b_ - d) / (2 * a_)))


def winding_G(pr, which, rad, N=1500):
    idx = 0 if which == 1 else 2
    tot, prev = mp.mpf(0), None
    for j in range(N + 1):
        v = pr.G(rad * mp.expj(2 * mp.pi * j / N))[idx]
        if prev is not None:
            tot += mp.arg(v / prev)
        prev = v
    return int(mp.nint(tot / (2 * mp.pi)))


def zeros_G(pr, which, rin):
    found = []
    for ir in range(10):
        rr = rin * (RMAX / rin) ** ((ir + mp.mpf("0.5")) / 10)
        for it in range(24):
            x = rr * mp.expj(2 * mp.pi * (it + mp.mpf("0.5")) / 24)
            try:
                y = KC.newton(pr, x, which, tol=mp.mpf(10) ** -20)
            except (RuntimeError, ZeroDivisionError):
                continue
            if rin < abs(y) < RMAX and all(abs(y - f) > mp.mpf(10) ** -8 for f in found):
                found.append(y)
    return found


def main():
    t0 = time.time()
    print(f"== stop-(c) scan == spin 9/10, R0 {R0}, square half-side {mp.nstr(RSQ, 6)}, grid {GRID}x{GRID}", flush=True)
    seeds = SS.kerr_points()
    worst = {}
    for kc in [mp.mpf(a) for a in (sys.argv[1:] or ["2", "2.5", "3"])]:
        path = [kc * j / 40 for j in range(1, 41)]
        pr_c, st_c = SS.track_laurent(path, seeds)
        rp, rm, pp, pm = [x for x, _ in st_c]
        lasso, delta = KC.capsule_lasso(rp, pp, [rm, pm], b=R0)
        print(f"-- k_c = {kc}: rho_c {mp.nstr(pr_c.rho, 5)}; r+ {mp.nstr(rp, 6)}, r- {mp.nstr(rm, 6)}, "
              f"p+ {mp.nstr(pp, 6)}, p- {mp.nstr(pm, 6)}; lasso delta {mp.nstr(delta, 4)}", flush=True)
        w = dict(wmax=mp.mpf(0), rho=mp.mpf(0), d_circle=mp.mpf(99), d_lasso=mp.mpf(99), at_c=None, at_l=None,
                 counts=set())
        for iy in range(GRID):
            st_row = st_c
            for ix in range(GRID):
                k = mp.mpc(kc - RSQ + 2 * RSQ * ix / (GRID - 1), -RSQ + 2 * RSQ * iy / (GRID - 1))
                try:
                    pr, st_row = SS.track_laurent([kc + (k - kc) * j / 6 for j in range(1, 7)], st_c)
                except Exception as e:     # noqa: BLE001  (report and continue: a failure is itself a finding)
                    print(f"   k = {mp.nstr(k, 6)}: FAILED {type(e).__name__}: {e}", flush=True)
                    continue
                rin = max(mp.mpf("1.05"), pr.rho + mp.mpf("0.12"))
                pts = [(x, f"tracked{i}") for i, (x, _) in enumerate(st_row)]
                zs = [(y, "G1") for y in zeros_G(pr, 1, rin)] + [(y, "G2") for y in zeros_G(pr, 2, rin)]
                allp = pts + [(y, t) for y, t in zs if all(abs(y - x) > mp.mpf(10) ** -6 for x, _ in pts)]
                cnt = (winding_G(pr, 1, RMAX) - winding_G(pr, 1, rin), winding_G(pr, 2, RMAX) - winding_G(pr, 2, rin))
                w["counts"].add(cnt)
                w["wmax"] = max(w["wmax"], wmax(k))
                w["rho"] = max(w["rho"], pr.rho)
                for y, tag in allp:
                    dc = abs(abs(y) - R0)
                    on_lasso = tag in ("tracked0", "tracked2")       # r+, p+ are inside the lasso by design
                    dl = KC.path_dist(y, lasso)
                    if dc < w["d_circle"]:
                        w["d_circle"], w["at_c"] = dc, (mp.nstr(k, 6), tag, mp.nstr(y, 6))
                    if not on_lasso and dl < w["d_lasso"]:
                        w["d_lasso"], w["at_l"] = dl, (mp.nstr(k, 6), tag, mp.nstr(y, 6))
                    if on_lasso and dl < w["d_lasso"]:
                        w["d_lasso"], w["at_l"] = dl, (mp.nstr(k, 6), tag + " (enclosed)", mp.nstr(y, 6))
            print(f"   row {iy + 1}/{GRID} done ({time.time() - t0:.0f} s)", flush=True)
        dmin = min(w["d_circle"], w["d_lasso"])
        cls = "FOUND (< 0.05)" if dmin < mp.mpf("0.05") or w["wmax"] >= 1 / mp.mpf("0.81") else \
            ("close (< 0.15)" if dmin < mp.mpf("0.15") else "clear")
        print(f"   SUMMARY k_c = {kc}: max |w_root| {mp.nstr(w['wmax'], 5)} (limit {mp.nstr(1 / mp.mpf('0.81'), 5)}), "
              f"max rho_c {mp.nstr(w['rho'], 5)}; nearest to circle {mp.nstr(w['d_circle'], 4)} at {w['at_c']}; "
              f"nearest to lasso {mp.nstr(w['d_lasso'], 4)} at {w['at_l']}; (G1, G2) zero counts in annulus "
              f"{sorted(w['counts'])} -> {cls}", flush=True)
        worst[str(kc)] = cls
    print(f"== done, {time.time() - t0:.0f} s; {worst}", flush=True)


if __name__ == "__main__":
    main()
