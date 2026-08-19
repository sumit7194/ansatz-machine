#!/usr/bin/env python3
"""P0 PHASE 1 -- where does the Cartan-Karlhede order-2 wall actually live?

THE PROBLEM. Section 122 walls. Schwarzschild completes an order-2 signature in ~32s; the
isotropic chart of the SAME spacetime walls past 80s; Kerr a=1/2 has never once been reached
in a completed run (two attempts: 4.6h killed by a gate, 6h+ killed by a shutdown). We have
been guessing which stage is responsible, and guessed wrong three times in a row -- each
correction came from a measurement, never from reasoning about the code. So: measure.

THE HYPOTHESIS UNDER TEST (the GHP-representation hypothesis). The cost is not intrinsic to
the derivative ORDER but to the coordinate REPRESENTATION we differentiate in: the swell is
in the size of the intermediate expressions, not in the number of them. If true, ONE stage --
the second covariant derivative and the frame contractions that follow it -- should dominate,
and the expression-size ratio Kerr/Schwarzschild at that stage should be far larger than the
ratio of component COUNTS (which is identical: both are 4^5 = 1024 entries of nabla-nabla-C).
If instead the time is spread evenly across stages in proportion to component counts, the
hypothesis is FALSE and the problem is bulk, not representation -- a different fix entirely.

WHAT IT PRODUCES. A per-stage table -- wall-clock, share of total, output expression size --
for one Kerr a=1/2 order-2 signature, with Schwarzschild M=1 profiled first as a CONTROL.
The control is the whole point: an absolute time for Kerr says nothing on its own, whereas
"stage X is 900x the control while every other stage is 3x" names the culprit. The
deliverable is >=80% of wall-clock attributed to named stages.

NOT A BATTERY. This is a measuring instrument, hence the leading underscore -- it asserts
nothing and gates nothing. It never kills anything and never budgets: a self-imposed wall
would distort the very quantity being measured (see the memory-misread correction in the
journal for how nearly that happened).

Progress is fsync'd per stage to data/p0_stage_profile.log, because this run is expected to
be long and has a history of being killed before it can report.

Repro:  .venv/bin/python scripts/_p0_stage_profile.py            (control + Kerr)
        .venv/bin/python scripts/_p0_stage_profile.py --control  (control only, ~1 min)
"""
import os
import resource
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import sympy as sp

import ck
from ck import (canonical_frame, cartan_order1, cartan_order2, covariant_derivative_weyl,
                functional_rank, isotropy_invariants, null_tetrad, residual_isotropy,
                ricci_invariants, segre_type, weight_invariants, zsimp, FRAME_WEIGHT)
from analyzer import weyl_tensor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
_mod = __import__("122_ck_order2")
kerr, schwarzschild, DOMAINS = _mod.kerr, _mod.schwarzschild, _mod.DOMAINS
taub_nut = _mod.taub_nut

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG = os.path.join(ROOT, "data", "p0_stage_profile.log")


def _rss_mb():
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / (1024.0 * 1024.0)


def _note(line):
    print(line, flush=True)
    with open(LOG, "a") as fh:
        fh.write(line + "\n")
        fh.flush()
        os.fsync(fh.fileno())


def size_of(obj):
    """Expression size in sympy ops -- the quantity the representation hypothesis is about.

    Counts ops over a scalar, a flat list, or a nested list/dict of scalars. Returns 0 rather
    than raising on anything it cannot walk, since this is instrumentation and must never be
    the reason a profiling run dies."""
    try:
        if isinstance(obj, dict):
            return sum(size_of(v) for v in obj.values())
        if isinstance(obj, (list, tuple)):
            return sum(size_of(v) for v in obj)
        if isinstance(obj, sp.Basic):
            return int(sp.count_ops(obj))
        return 0
    except Exception:
        return 0


# ------------------------------------------------------- sub-profiling the hot stage
# cartan_order2 is one stage in the table but ~20 internal calls per component, so a stage-level
# number cannot say WHICH part swells. We instrument by WRAPPING ck's functions rather than
# editing ck.py: the instrument must not change the thing it measures, and a profiling run must
# leave the frozen batteries bit-identical.
COUNTERS = {}


def _wrap(mod, name):
    orig = getattr(mod, name)
    COUNTERS[name] = {"n": 0, "sec": 0.0}

    def wrapped(*a, **kw):
        t0 = time.time()
        try:
            return orig(*a, **kw)
        finally:
            c = COUNTERS[name]
            c["n"] += 1
            dt = time.time() - t0
            c["sec"] += dt
            # The hot stage can run for hours on Kerr. Emit a durable line per outer call so a
            # run that is killed still leaves evidence of how far it got and how fast.
            if name == "second_frame_component":
                _note(f"      . {name} #{c['n']:<3d} {dt:8.2f}s  "
                      f"(cumulative {c['sec']:.1f}s, rss {_rss_mb():.0f}MB)")
    setattr(mod, name, wrapped)
    return orig


def reset_counters():
    for c in COUNTERS.values():
        c["n"], c["sec"] = 0, 0.0


def counter_table(label, stage_sec):
    """NOTE these are NOT disjoint -- second_frame_component CONTAINS frame_component5 and zsimp,
    so the columns nest and must not be summed. Read each against the stage total instead."""
    _note(f"\n  INSIDE THE HOT STAGE -- {label}   (stage took {stage_sec:.1f}s)")
    _note(f"    {'function (nested, do not sum)':34s} {'calls':>8s} {'seconds':>10s} {'share':>7s}"
          f" {'us/call':>10s}")
    for nm in sorted(COUNTERS, key=lambda k: -COUNTERS[k]["sec"]):
        c = COUNTERS[nm]
        if not c["n"]:
            continue
        share = 100.0 * c["sec"] / stage_sec if stage_sec else 0.0
        _note(f"    {nm:34s} {c['n']:8d} {c['sec']:10.2f} {share:6.1f}% "
              f"{1e6 * c['sec'] / c['n']:10.0f}")


class Profile:
    """Times each named stage and records the size of what it produced."""

    def __init__(self, label):
        self.label, self.rows, self.t_start = label, [], time.time()

    def stage(self, name, fn, count=None):
        t0, m0 = time.time(), _rss_mb()
        out = fn()
        dt, dm = time.time() - t0, _rss_mb() - m0
        sz = size_of(out)
        self.rows.append({"name": name, "sec": dt, "ops": sz, "count": count, "d_rss": dm})
        _note(f"    [{self.label}] {name:34s} {dt:9.2f}s  ops={sz:<9d} "
              f"peak_rss={_rss_mb():6.0f}MB  (+{dm:.0f})")
        return out

    def total(self):
        return time.time() - self.t_start

    def table(self):
        tot = sum(r["sec"] for r in self.rows)
        _note(f"\n  PER-STAGE PROFILE -- {self.label}   (accounted {tot:.1f}s)")
        _note(f"    {'stage':34s} {'seconds':>10s} {'share':>7s} {'output ops':>11s}")
        for r in sorted(self.rows, key=lambda r: -r["sec"]):
            share = 100.0 * r["sec"] / tot if tot else 0.0
            _note(f"    {r['name']:34s} {r['sec']:10.2f} {share:6.1f}% {r['ops']:11d}")
        top = sorted(self.rows, key=lambda r: -r["sec"])
        acc, named = 0.0, []
        for r in top:
            if acc / tot >= 0.80 if tot else True:
                break
            acc += r["sec"]
            named.append(r["name"])
        _note(f"    >=80% of wall-clock is in {len(named)} stage(s): {', '.join(named)}")
        return {r["name"]: r for r in self.rows}, tot


def profile_signature(name, build, order2=True):
    """Replay ck_signature stage by stage. Mirrors ck.ck_signature exactly -- if that function
    changes, this must be re-checked against it, which is why each stage is named after the
    call it wraps rather than after what it conceptually does."""
    _note(f"\n  === {name} (order2={order2}) ===")
    geo, tet_seed = build()
    ck.set_domain(*DOMAINS[name])
    p = Profile(name)

    C = p.stage("weyl_tensor", lambda: weyl_tensor(geo), count=256)
    tet = p.stage("null_tetrad", lambda: null_tetrad(geo) if tet_seed is None else tet_seed)
    cf = p.stage("canonical_frame", lambda: canonical_frame(geo, C, tet, verbose=False))
    tet, P, ty, iso, note = cf
    _note(f"    -> Petrov type {ty}, isotropy dim {iso}")

    Rs = p.stage("ricci_scalar (zsimp)", lambda: zsimp(geo.ricci_scalar))
    ric = p.stage("ricci_invariants", lambda: ricci_invariants(geo))
    ric_tr, Rmix = ric
    p.stage("segre_type", lambda: segre_type(geo, Rmix))
    p.stage("riemann_zero scan", lambda: all(
        zsimp(geo.riemann[a][b][c][d]) == 0
        for a in range(geo.n) for b in range(geo.n)
        for c in range(geo.n) for d in range(geo.n)), count=256)

    inv0 = ([q for q in P if q != 0] + ([Rs] if Rs != 0 else [])
            + [e for e in ric_tr[1:] if e != 0])
    t0 = p.stage("functional_rank order 0",
                 lambda: functional_rank(inv0, geo.coords))[0]

    DC = p.stage("covariant_derivative_weyl (order 1)",
                 lambda: covariant_derivative_weyl(geo, C), count=4**5)
    p.stage("nabla_C_zero scan", lambda: all(
        zsimp(DC[e][a][b][c][d]) == 0
        for e in range(4) for a in range(4) for b in range(4)
        for c in range(4) for d in range(4)), count=4**5)

    comp1 = p.stage("cartan_order1 (frame components)",
                    lambda: cartan_order1(geo, tet, C, DC))
    inv1 = p.stage("isotropy_invariants order 1", lambda: isotropy_invariants(comp1, ty))
    live1 = [v for v in inv1.values() if v != 0]
    t1 = p.stage("functional_rank order 1",
                 lambda: functional_rank(inv0 + live1, geo.coords))[0]

    comp2, inv2, t2 = {}, {}, t1
    if order2 and ty in ("D", "N"):
        reset_counters()
        c2 = p.stage("cartan_order2 (nabla-nabla-C + frame)",
                     lambda: ck.cartan_order2(geo, tet, DC, ty), count=4**6)
        counter_table(name, p.rows[-1]["sec"])
        comp2, w2 = c2
        inv2 = p.stage("weight_invariants order 2",
                       lambda: weight_invariants(comp2, w2, tag="K:"))
        live2 = [v for v in inv2.values() if v != 0]
        t2 = p.stage("functional_rank order 2",
                     lambda: functional_rank(inv0 + live1 + live2, geo.coords))[0]
        w1 = {}
        for tag in ("Psi2", "Psi4", "Psi0"):
            w1.update({f"D_{a}_{tag}": FRAME_WEIGHT[a] for a in FRAME_WEIGHT})
        p.stage("residual_isotropy", lambda: residual_isotropy(ty, iso, [(comp1, w1),
                                                                         (comp2, w2)]))
    _note(f"    -> t0={t0} t1={t1} t2={t2}   order-1 comps={len(comp1)} "
          f"order-2 comps={len(comp2)}")
    rows, tot = p.table()
    return {"name": name, "rows": rows, "total": tot, "type": ty,
            "t": (t0, t1, t2), "n1": len(comp1), "n2": len(comp2)}


def main():
    for _f in ("frame_component5", "zsimp", "covariant_derivative_vector",
               "second_frame_component"):
        _wrap(ck, _f)
    control_only = "--control" in sys.argv
    # --taub-nut profiles the ONE catalog entry never timed. It is what turns the P0 gate's
    # "missed" from a lower bound into an exact factor. The first attempt was lost whole to a
    # reboot -- 27 minutes of compute and a 0-byte output file -- because nothing was written
    # until the end. Every stage here is fsync'd as it completes, so a second reboot costs only
    # the stage in flight, and the log itself says how far it got.
    if "--taub-nut" in sys.argv:
        _note("=" * 78)
        _note(f"P0 -- Taub-NUT n=1/2 order-2 signature   started "
              f"{time.strftime('%Y-%m-%dT%H:%M:%S')}")
        _note(f"pid {os.getpid()}   log {LOG}")
        _note("  WHY: the last unmeasured catalog entry. Kerr = 3501.2 s = 58.4 min; statics")
        _note("  = 101 s. The gate (whole catalog < 60 min) is already FALSE on those alone,")
        _note("  so this does not change the verdict -- it only makes the margin exact.")
        _note("=" * 78)
        r = profile_signature("Taub-NUT n=1/2", taub_nut)
        _note(f"\n  TAUB-NUT TOTAL: {r['total']:.1f} s = {r['total'] / 60:.2f} min")
        _note(f"  catalog so far: Kerr 3501.2 + Taub-NUT {r['total']:.1f} + statics 101 "
              f"= {(3501.2 + r['total'] + 101) / 60:.1f} min   vs the 60 min bar "
              f"-> MISSED by {(3501.2 + r['total'] + 101) / 3600:.2f}x")
        _note(f"finished {time.strftime('%Y-%m-%dT%H:%M:%S')}  peak RSS {_rss_mb():.0f} MB")
        return
    _note("=" * 78)
    _note(f"P0 PHASE 1 -- CK order-2 stage profile   started {time.strftime('%Y-%m-%dT%H:%M:%S')}")
    _note(f"pid {os.getpid()}   log {LOG}")
    _note("=" * 78)

    res = [profile_signature("Schwarzschild M=1", lambda: schwarzschild(1))]
    if not control_only:
        res.append(profile_signature("Kerr a=1/2", kerr))

    if len(res) == 2:
        ctrl, kerr_r = res
        _note("\n" + "=" * 78)
        _note("  THE COMPARISON THE HYPOTHESIS IS ABOUT")
        _note("  Component COUNTS are identical between the two metrics at every stage; only")
        _note("  expression SIZE differs. So a ratio far above 1 in a stage is representation")
        _note("  swell, not bulk.")
        _note(f"    {'stage':34s} {'Schw s':>9s} {'Kerr s':>10s} {'ratio':>8s} {'ops ratio':>10s}")
        for nm, r in kerr_r["rows"].items():
            c = ctrl["rows"].get(nm)
            if not c:
                continue
            rt = r["sec"] / c["sec"] if c["sec"] > 1e-9 else float("inf")
            oz = r["ops"] / c["ops"] if c["ops"] else float("inf")
            _note(f"    {nm:34s} {c['sec']:9.2f} {r['sec']:10.2f} {rt:8.1f}x {oz:9.1f}x")
        _note(f"\n  totals: Schwarzschild {ctrl['total']:.1f}s   Kerr {kerr_r['total']:.1f}s "
              f"({kerr_r['total'] / ctrl['total']:.0f}x)")
    _note(f"\nfinished {time.strftime('%Y-%m-%dT%H:%M:%S')}  peak RSS {_rss_mb():.0f} MB")


if __name__ == "__main__":
    main()
