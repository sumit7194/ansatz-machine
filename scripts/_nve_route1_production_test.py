#!/usr/bin/env python3
"""U5: the production driver's logic, with SIMULATED stages (no arithmetic runs). [ansatz-machine-personal, 2026-11-27;
extended after the Bridge's read of 10707e1 (S1, S2, S4)]
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
    RES.append(bool(ok))
    print(f"{name}: {'PASS' if ok else 'FAIL'}  {note}")


class Sim:
    """fail(lo, hi) -> None (certify) | 'split' | 'radius' | 'stop' (a gate). code: the simulated code hash, so a
    record written by one Sim is foreign to a Sim with another code. rerun_bad: segments whose batch rerun differs.
    full_never: the full-controls verdict never happens (to test S2's end assertion)."""
    def __init__(self, fail=lambda lo, hi: None, code="c1", rerun_bad=(), crash_after=None, full_never=False):
        self.fail, self.code, self.rerun_bad, self.crash_after, self.full_never = fail, code, set(rerun_bad), crash_after, full_never
        self.calls, self.full = [], []

    def base_of(self, lo, hi, mode):
        return f"v6_{P.segkey(lo, hi)}_{mode}_{self.code}"

    def stage(self, lo, hi, mode, want_full):
        if self.crash_after is not None and len(self.calls) == self.crash_after:
            raise KeyboardInterrupt("simulated crash")
        self.calls.append((lo, hi, mode))
        f = self.fail(lo, hi)
        base = self.base_of(lo, hi, mode)
        if f == "stop":
            raise P.Stop(f"simulated gate at [{lo}, {hi}]")
        if f == "split":
            return "split", dict(base=base, reason="simulated not certified")
        if f == "radius":
            return "radius_limited", dict(base=base, reason="simulated node-radius limit")
        full = bool(want_full and not self.full_never)
        if full:
            self.full.append((lo, hi, mode))
        return "certified", dict(base=base, n=12, abs_f_ge="1", abs_F_ge=None, fullctl=full, vjson="v", vjson_sha="s",
                                 nodef="nf", nodes_sha="ns", mjson="m")

    def rerun_verdict(self, lo, hi, mode, r):
        ok = (lo, hi) not in self.rerun_bad and r["base"] == self.base_of(lo, hi, mode)
        return ok, "identical" if ok else "simulated difference"


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

# A: everything certifies; full controls on the first certified segment of each mode
fresh()
S = Sim()
rc = P.main(S)
r = last_run()
check("U5.A all certified", rc == 0 and r.get("covers_target") and r["reach"] == ["1/640", "3"] and len(S.calls) == 35
      and S.full == [(Q(1, 20), Q(1, 10), "Fk2"), (Q(1, 10), Q(2, 10), "F")] and r["full_controls"],
      f"rc {rc}, reach {r.get('reach')}, {len(S.calls)} stages, full controls on {S.full}")

# B: one up segment fails at depth 0, both halves certify -> still covers; the split is recorded
fresh()
S = Sim(fail=lambda lo, hi: "split" if (lo, hi) == (Q(15, 10), Q(16, 10)) else None)
rc = P.main(S)
r = last_run()
halves = [c for c in S.calls if c[0] >= Q(15, 10) and c[1] <= Q(16, 10)]
check("U5.B split then certify", rc == 0 and r.get("covers_target") and halves == [(Q(15, 10), Q(16, 10), "F"),
      (Q(15, 10), Q(31, 20), "F"), (Q(31, 20), Q(16, 10), "F")], f"rc {rc}, calls in [1.5, 1.6]: {halves}")

# B': [0.1, 0.2] itself splits: the full controls go to the first certified F segment, [0.1, 0.15] (S2)
fresh()
S = Sim(fail=lambda lo, hi: "split" if (lo, hi) == (Q(1, 10), Q(2, 10)) else None)
rc = P.main(S)
r = last_run()
check("U5.B' split of [0.1, 0.2]: full controls still run", rc == 0 and r.get("covers_target") and r["full_controls"]
      and (Q(1, 10), Q(3, 20), "F") in S.full, f"rc {rc}, full controls on {S.full}")

# B'': a down-chain segment splits and its halves certify -> the reach stays contiguous to eps_a
fresh()
S = Sim(fail=lambda lo, hi: "split" if (lo, hi) == (Q(1, 160), Q(1, 80)) else None)
rc = P.main(S)
r = last_run()
dh = [c for c in S.calls if c[0] >= Q(1, 160) and c[1] <= Q(1, 80)]
check("U5.B'' down-chain split then certify", rc == 0 and r.get("covers_target") and r["reach"] == ["1/640", "3"]
      and dh == [(Q(1, 160), Q(1, 80), "Fk2"), (Q(3, 320), Q(1, 80), "Fk2"), (Q(1, 160), Q(3, 320), "Fk2")],
      f"rc {rc}, reach {r.get('reach')}, calls {dh}")

# C: a segment that fails at every depth stops its chain at DMAX; the other chain still runs
fresh()
S = Sim(fail=lambda lo, hi: "split" if lo >= Q(2) and hi <= Q(21, 10) else None)
rc = P.main(S)
r = last_run()
check("U5.C stop rule (up chain)", rc == 0 and r["reach"] == ["1/640", "2"] and not r["covers_target"] and r["up_stopped"]
      and not r["down_stopped"] and not any(c[0] >= Q(21, 10) for c in S.calls), f"reach {r.get('reach')}")
fresh()
S = Sim(fail=lambda lo, hi: "split" if hi <= Q(1, 80) else None)
rc = P.main(S)
r = last_run()
check("U5.C' stop rule (down chain), the up chain still runs", rc == 0 and r["reach"] == ["1/80", "3"] and r["down_stopped"]
      and not r["up_stopped"] and any(c[1] == 3 for c in S.calls), f"reach {r.get('reach')}")

# C'': a radius-limited failure stops its chain at once, with no split
fresh()
S = Sim(fail=lambda lo, hi: "radius" if hi <= Q(1, 80) else None)
rc = P.main(S)
r = last_run()
check("U5.C'' radius-limited stops without splitting", rc == 0 and r["reach"] == ["1/80", "3"] and r["down_stopped"]
      and sum(1 for c in S.calls if c[1] <= Q(1, 80)) == 1, f"reach {r.get('reach')}")

# D: a correctness gate stops the whole run, and a rerun refuses to resume
fresh()
S = Sim(fail=lambda lo, hi: "stop" if (lo, hi) == (Q(5, 10), Q(6, 10)) else None)
rc = P.main(S)
r = last_run()
S2 = Sim()
rc2 = P.main(S2)
check("U5.D gate stops the run; no resume", rc == 2 and r.get("outcome") == "stopped" and not any(c[0] >= Q(6, 10) for c in S.calls)
      and rc2 == 2 and S2.calls == [], f"rc {rc}, rerun rc {rc2}, rerun stages {len(S2.calls)}")

# D': S1 - a state record from OTHER code is not trusted on resume: the run stops, nothing is staged
fresh()
S = Sim(code="c1", crash_after=10)
try:
    P.main(S)
except KeyboardInterrupt:
    pass
S2 = Sim(code="c2")
rc = P.main(S2)
r = last_run()
check("U5.D' foreign-code state record refused (S1)", rc == 2 and r.get("outcome") == "stopped" and "code base" in r.get("reason", "")
      and S2.calls == [], f"rc {rc}, reason {r.get('reason', '')[:60]}, stages {len(S2.calls)}")

# E: resume after a crash: certified segments and recorded splits are not staged again
fresh()
failB = lambda lo, hi: "split" if (lo, hi) == (Q(15, 10), Q(16, 10)) else None
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

# F: S1 - a segment whose batch rerun differs does not count: the reach stops below it and the run fails
fresh()
S = Sim(rerun_bad={(Q(15, 10), Q(16, 10))})
rc = P.main(S)
r = last_run()
check("U5.F batch rerun mismatch: reach from identical reruns only", rc == 2 and r.get("batch_identical") is False
      and r["reach"] == ["1/640", "3/2"] and not r["covers_target"], f"rc {rc}, reach {r.get('reach')}")

# G: S2 - if no full-controls pass happened for a mode, the run fails and does not claim the target
fresh()
S = Sim(full_never=True)
rc = P.main(S)
r = last_run()
check("U5.G no full-controls pass -> run fails (S2)", rc == 2 and r.get("full_controls") is False and not r["covers_target"],
      f"rc {rc}, full_controls {r.get('full_controls')}")

print("U5 RESULT:", "PASS" if all(RES) else "FAIL", f"({sum(RES)}/{len(RES)})")
sys.exit(0 if all(RES) else 1)
