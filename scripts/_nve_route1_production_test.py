#!/usr/bin/env python3
"""U5: the production driver's logic, with SIMULATED stages (no arithmetic runs). [ansatz-machine-personal, 2026-11-27]
Every scenario can fail, and each states its pass criterion. The state and log files go to a temporary directory.
    python3 scripts/_nve_route1_production_test.py"""
import os
import sys
import tempfile
from fractions import Fraction as Q

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _nve_route1_production as P      # noqa: E402

RES = []


def check(name, ok, note=""):
    RES.append(ok)
    print(f"{name}: {'PASS' if ok else 'FAIL'}  {note}")


class Sim:
    """fail(lo, hi, _) -> None (certify) | 'split' | 'stop' (a gate). rerun_same: batch rerun outcome."""
    def __init__(self, fail=lambda lo, hi, d: None, rerun_same=True, crash_after=None):
        self.fail, self.rerun_same, self.crash_after = fail, rerun_same, crash_after
        self.calls, self.fullctl = [], []

    def stage(self, lo, hi, mode, fullctl):
        if self.crash_after is not None and len(self.calls) == self.crash_after:
            raise KeyboardInterrupt("simulated crash")
        self.calls.append((lo, hi, mode))
        if fullctl:
            self.fullctl.append((lo, hi))
        f = self.fail(lo, hi, None)
        if f == "stop":
            raise P.Stop(f"simulated gate at [{lo}, {hi}]")
        if f == "split":
            return "split", "simulated not certified"
        if f == "radius":
            return "radius_limited", "simulated node-radius limit"
        return "certified", dict(base="b", n=12, abs_f_ge="1", vjson="v", vjson_sha="s", nodef="nf", nodes_sha="ns")

    def rerun_verdict(self, *a):
        return self.rerun_same


def fresh(eps="1.92e-3", top="3"):
    d = tempfile.mkdtemp(prefix="u5_")
    P.STATE, P.LOG = os.path.join(d, "state.jsonl"), os.path.join(d, "prod.out")
    os.environ.update(PROD_EPS=eps, PROD_TOP=top)
    return d


def last_run():
    return P.load_state().get("RUN", {})


# plan sizes
dn, up = P.plan(Q("1.92e-3"), Q(3))
check("U5.0 plan 3/5", len(dn) == 6 and len(up) == 29 and dn[-1][0] <= Q("1.92e-3") < dn[-2][0] and up[-1][1] == 3
      and dn[0] == (Q(1, 20), Q(1, 10)) and up[0] == (Q(1, 10), Q(2, 10)), f"{len(dn)} + {len(up)}")
dn, up = P.plan(Q("1.06e-4"), Q(2))
check("U5.0 plan 9/10", len(dn) == 10 and len(up) == 19 and dn[-1][0] <= Q("1.06e-4") and up[-1][1] == 2,
      f"{len(dn)} + {len(up)}")

# A: everything certifies
fresh()
S = Sim()
rc = P.main(S)
r = last_run()
check("U5.A all certified", rc == 0 and r.get("covers_target") and r["reach"] == ["1/640", "3"] and len(S.calls) == 35
      and S.fullctl == [(Q(1, 10), Q(2, 10))], f"rc {rc}, reach {r.get('reach')}, {len(S.calls)} stages, fullctl {S.fullctl}")

# B: one segment fails at depth 0, both halves certify -> still covers; the split is recorded
fresh()
S = Sim(fail=lambda lo, hi, d: "split" if (lo, hi) == (Q(15, 10), Q(16, 10)) else None)
rc = P.main(S)
r = last_run()
halves = [c for c in S.calls if c[0] >= Q(15, 10) and c[1] <= Q(16, 10)]
check("U5.B split then certify", rc == 0 and r.get("covers_target") and halves == [(Q(15, 10), Q(16, 10), "F"),
      (Q(15, 10), Q(31, 20), "F"), (Q(31, 20), Q(16, 10), "F")], f"rc {rc}, calls in [1.5, 1.6]: {halves}")

# C: a segment that fails at every depth stops its chain at DMAX; the other chain still runs
fresh()
bad = lambda lo, hi, d: "split" if lo >= Q(2) and hi <= Q(21, 10) else None
S = Sim(fail=bad)
rc = P.main(S)
r = last_run()
check("U5.C stop rule (up chain)", rc == 0 and r["reach"] == ["1/640", "2"] and not r["covers_target"] and r["up_stopped"]
      and not r["down_stopped"] and not any(c[0] >= Q(21, 10) for c in S.calls),
      f"reach {r.get('reach')}, up stopped {r.get('up_stopped')}, stages above 2.1: {sum(c[0] >= Q(21, 10) for c in S.calls)}")
fresh()
S = Sim(fail=lambda lo, hi, d: "split" if hi <= Q(1, 80) else None)
rc = P.main(S)
r = last_run()
check("U5.C' stop rule (down chain), the up chain still runs", rc == 0 and r["reach"] == ["1/80", "3"] and r["down_stopped"]
      and not r["up_stopped"] and any(c[1] == 3 for c in S.calls), f"reach {r.get('reach')}")

# C'': a radius-limited failure stops its chain at once, with no split
fresh()
S = Sim(fail=lambda lo, hi, d: "radius" if hi <= Q(1, 80) else None)
rc = P.main(S)
r = last_run()
check("U5.C'' radius-limited stops without splitting", rc == 0 and r["reach"] == ["1/80", "3"] and r["down_stopped"]
      and sum(1 for c in S.calls if c[1] <= Q(1, 80)) == 1, f"reach {r.get('reach')}, staged below 1/80: "
      f"{sum(1 for c in S.calls if c[1] <= Q(1, 80))}")

# D: a correctness gate stops the whole run, and a rerun refuses to resume
fresh()
S = Sim(fail=lambda lo, hi, d: "stop" if (lo, hi) == (Q(5, 10), Q(6, 10)) else None)
rc = P.main(S)
r = last_run()
S2 = Sim()
rc2 = P.main(S2)
check("U5.D gate stops the run; no resume", rc == 2 and r.get("outcome") == "stopped" and not any(c[0] >= Q(6, 10) for c in S.calls)
      and rc2 == 2 and S2.calls == [], f"rc {rc}, rerun rc {rc2}, rerun stages {len(S2.calls)}")

# E: resume after a crash: certified segments and recorded splits are not staged again
fresh()
failB = lambda lo, hi, d: "split" if (lo, hi) == (Q(15, 10), Q(16, 10)) else None
S = Sim(fail=failB, crash_after=22)
try:
    P.main(S)
    crashed = False
except KeyboardInterrupt:
    crashed = True
S2 = Sim(fail=failB)
rc = P.main(S2)
r = last_run()
again = set((a, b) for a, b, _ in S.calls) & set((a, b) for a, b, _ in S2.calls)
check("U5.E resume", crashed and rc == 0 and r.get("covers_target") and not again and len(S.calls) + len(S2.calls) == 37,
      f"first run {len(S.calls)} stages, resume {len(S2.calls)}, staged twice {sorted(again)}")

# F: a batch rerun that is not byte-identical makes the run fail
fresh()
S = Sim(rerun_same=False)
rc = P.main(S)
check("U5.F batch rerun mismatch", rc == 2 and last_run().get("batch_identical") is False, f"rc {rc}")

print("U5 RESULT:", "PASS" if all(RES) else "FAIL", f"({sum(RES)}/{len(RES)})")
sys.exit(0 if all(RES) else 1)
