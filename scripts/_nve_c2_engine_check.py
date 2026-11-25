"""Office check of Fable's c2 (C2_ANALYTIC.md, branch fable/2026-11-25-c2-analytic, 5b6110b) with the registered
50-digit engine (2026-11-25). Independent of Fable's script: it shares only the stored engines.
For one spin (NVE_SPIN), E = 4/5: F(k) = tr[M1, M0] - 2 by the spin-scan region-A pipeline (circle R0, capsule lasso
around r+, p+, based at R0), at the 8 points k_j = rho * exp(2 pi i j / 8), rho = C2_RHO (default 1/100). Cauchy:
    c2 ~ mean_j F(k_j)/k_j^2   (alias c10 rho^8),     c3 ~ mean_j F(k_j)/k_j^3   (alias c11 rho^8),
and the same for (tr M0 - 2): its k^2 coefficient is x11^2 + x12 x21 in Fable's notation. Also tr M1 at k = 0.
Declared peak < 300 MB; guard 1.5 GB; 1 core, nice 12.
    NVE_SPIN=9/10 C2_R0=1.2639 nice -n 12 .venv/bin/python scripts/_nve_c2_engine_check.py   (appends to c2_engine_check.out)"""
import os
import resource
import sys
import time

import mpmath as mp

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_spin_scan as S      # noqa: E402  (sets mp.dps = 50, E = 4/5, spin from NVE_SPIN)
import _nve_lower_kc as KC      # noqa: E402

R0 = mp.mpf(os.environ["C2_R0"])
RHO = mp.mpf(os.environ.get("C2_RHO", "0.01"))
NP = 8
OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "nve", "c2_engine_check.out")


def guard():
    if resource.getrusage(resource.RUSAGE_SELF).ru_maxrss > 1.5 * 1024**3:
        print("ABORT: memory"); sys.exit(2)


t0 = time.time()
lau = S.LauA(R0)
st = S.kerr_points()
rows, Fs, T0s, ks = [], [], [], []


def one(k, st, step="0.35"):
    pr, outer, extras = lau.state(k, st)
    lasso, g = lau.loops(pr, outer, extras)
    r = lau.evaluate(pr, outer, extras, lasso, step=step)
    return r, g, outer


# k = 0 itself: tr M1(0) (to compare with -2 cosh(kappa omega)); F(0) must be ~0
r0, g0, _ = one(mp.mpf(0), st)
rows.append(f"spin {S.SPIN}, R0 {mp.nstr(R0, 6)}, rho {mp.nstr(RHO, 3)}: k=0: F = {mp.nstr(r0['F'], 3)}, "
            f"tr M0 - 2 = {mp.nstr(r0['T0'] - 2, 3)}, tr M1(0) = {mp.nstr(r0['T1'], 15)}, geometry ok {g0['ok']}")
print(rows[-1], flush=True)
for j in range(NP):
    k = RHO * mp.expj(2 * mp.pi * j / NP)
    r, g, _ = one(k, st)
    if not g["ok"]:
        rows.append(f"  GEOMETRY GUARD FAILED at k = {mp.nstr(k, 5)}: {g}")
    Fs.append(r["F"]); T0s.append(r["T0"] - 2); ks.append(k)
    print(f"  j={j} k={mp.nstr(k, 5)} F={mp.nstr(r['F'], 12)} ({time.time() - t0:.0f}s)", flush=True)
    guard()
# step control at one point
rs, _, _ = one(ks[1], st, step="0.2")
c2 = mp.fsum(F / k**2 for F, k in zip(Fs, ks)) / NP
c3 = mp.fsum(F / k**3 for F, k in zip(Fs, ks)) / NP
t2 = mp.fsum(T / k**2 for T, k in zip(T0s, ks)) / NP
lin = mp.fsum(F / k for F, k in zip(Fs, ks)) / NP          # the k^1 coefficient: must be ~0 (F = O(k^2))
rows.append(f"  c1 (must be ~0) = {mp.nstr(lin, 3)};  c2 = {mp.nstr(c2, 15)};  c3 = {mp.nstr(c3, 12)};  "
            f"-c2/c3 = {mp.nstr(-c2 / c3, 8)};  [tr M0 - 2]_k^2 = {mp.nstr(t2, 15)}")
rows.append(f"  step control at k_1: |F(0.35) - F(0.2)| / |F| = {mp.nstr(abs(Fs[1] - rs['F']) / abs(Fs[1]), 3)};  "
            f"time {time.time() - t0:.0f}s;  peak {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1e6:.0f} MB")
print("\n".join(rows[-2:]), flush=True)
with open(OUT, "a") as fh:
    fh.write("\n".join(rows) + "\n\n")
