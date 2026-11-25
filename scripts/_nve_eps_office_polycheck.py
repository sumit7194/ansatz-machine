"""Office check (2026-11-26) of Fable's eps certifier (75957fd), item 5: the fixed k = 0 lasso polygon, EXACTLY.
The certifier's own polygon (capsule_polygon(), float vertices = exact binary rationals) is tested in rational
arithmetic (fractions.Fraction):
  (a) the ring (the capsule, closed) is a strictly convex polygon with consistent orientation, so a simple closed curve;
  (b) r+ and p+ lie strictly inside the ring, r- and p- strictly outside (orientation tests against every edge), with
      the distance margins printed (they dwarf the 1e-16 float error in r+-);
  (c) the base point b lies outside the ring, and the tail segment [b, v0] meets the ring only at its endpoint v0;
  (d) so the lasso is (tail) * (simple loop around exactly {r+, p+}) * (tail)^-1, a based loop with winding numbers
      1, 0, 1, 0 about r+, r-, p+, p-.
    NVE_SPIN=3/5 [EPS_DELTA=wide] EPSDIR=<checkout>/scripts .venv/bin/python scripts/_nve_eps_office_polycheck.py"""
import os
import sys
from fractions import Fraction as Fr

sys.path.insert(0, os.environ["EPSDIR"])
import _nve_eps_certify as EC          # noqa: E402

poly, delta = EC.capsule_polygon()
b, ring = poly[0], poly[1:-1]          # ring: cap[i0] ... cap[i0] (closed)
assert ring[0] == ring[-1]
V = [(Fr(p.real), Fr(p.imag)) for p in ring[:-1]]
B = (Fr(b.real), Fr(b.imag))
n = len(V)


def cross(o, p, q):
    return (p[0] - o[0]) * (q[1] - o[1]) - (p[1] - o[1]) * (q[0] - o[0])


turns = [cross(V[i], V[(i + 1) % n], V[(i + 2) % n]) for i in range(n)]
orient = 1 if turns[0] > 0 else -1
convex = all(t * orient > 0 for t in turns)
distinct = len(set(V)) == n


def inside(p):
    return all(cross(V[i], V[(i + 1) % n], p) * orient > 0 for i in range(n))


def outside(p):
    return any(cross(V[i], V[(i + 1) % n], p) * orient < 0 for i in range(n))


a = Fr(EC.A.numerator, EC.A.denominator)
rp = Fr(EC.fl(EC.r_plus.mid))
rm = Fr(EC.fl(EC.r_minus.mid))
pts = {"r+": (rp, Fr(0)), "r-": (rm, Fr(0)), "p+": (Fr(2), a), "p-": (Fr(2), -a)}
ins = {k: inside(v) for k, v in pts.items()}
outs = {k: outside(v) for k, v in pts.items()}


def seg_inter(p1, p2, q1, q2):
    d1, d2 = cross(q1, q2, p1), cross(q1, q2, p2)
    d3, d4 = cross(p1, p2, q1), cross(p1, p2, q2)
    if ((d1 > 0) != (d2 > 0)) and d1 != 0 and d2 != 0 and ((d3 > 0) != (d4 > 0)) and d3 != 0 and d4 != 0:
        return True
    return any(d == 0 for d in (d1, d2, d3, d4))     # touching/collinear counts as an intersection (conservative)


v0 = V[0]
tail_hits = [i for i in range(n) if seg_inter(B, v0, V[i], V[(i + 1) % n]) and v0 not in (V[i], V[(i + 1) % n])]
# margins: float distances from the four points to the ring (for the record)
import math                             # noqa: E402


def dseg(p, a_, b_):
    px, py, ax, ay, bx, by = map(float, (p[0], p[1], a_[0], a_[1], b_[0], b_[1]))
    dx, dy = bx - ax, by - ay
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)))
    return math.hypot(ax + t * dx - px, ay + t * dy - py)


marg = {k: min(dseg(v, V[i], V[(i + 1) % n]) for i in range(n)) for k, v in pts.items()}
ok = (convex and distinct and ins["r+"] and ins["p+"] and outs["r-"] and outs["p-"] and outside(B) and not tail_hits)
print(f"spin {EC.A}{' wide' if EC.DELTA else ''}: ring {n} vertices, capsule radius {delta:.4f}; strictly convex {convex}, "
      f"vertices distinct {distinct}; inside: r+ {ins['r+']}, p+ {ins['p+']}; outside: r- {outs['r-']}, p- {outs['p-']}; "
      f"base outside {outside(B)}; tail meets ring only at v0 {not tail_hits}; distances to ring: "
      + ", ".join(f"{k} {v:.4f}" for k, v in marg.items()) + f"  -> {'PASS' if ok else 'FAIL'}")
