#!/usr/bin/env python3
"""T1 of the route-(i) registration (§3(d)): v5's proof stage reproduces v4's rows exactly.
[ansatz-machine-personal, 2026-11-26]
    python3 scripts/_nve_route1_t1_compare.py <v4 rows.jsonl> <v5 rows.jsonl> [<committed v4 rows.jsonl>]
    T1_MJSON="<v4 proof JSON>:<v5 proof JSON>" adds the whole-proof-JSON comparison (added after T1 on 7f96efc failed:
    the rows alone could not see a field missing from the proof JSON). There, v5 may add only version, code, code_env,
    code_files; env (interpreter) and every row's sec are dropped on both sides; everything else must be equal.
PASS iff, row by row (same rho order), the v5 record minus v5's own additions (coverage, code, f1) and the wall time
(sec) equals the v4 record minus sec: every key and every value, the gauge floats and Arb strings included. v5 adds
checks only, so any other difference is a bug. Both runs must be on the same machine and the same Python (§3(d)).
With a third file, also reports v4-on-this-run against the committed v4 rows (minus sec), as information: that one
is a cross-environment comparison, not part of T1."""
import json
import os
import sys

V5_ONLY = ("coverage", "code", "f1")


def load(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def strip(r, drop):
    return {k: v for k, v in r.items() if k not in drop}


def diff(a, b):
    keys = sorted(set(a) | set(b))
    return [k for k in keys if a.get(k, "<absent>") != b.get(k, "<absent>")]


r4, r5 = load(sys.argv[1]), load(sys.argv[2])
ok = len(r4) == len(r5) and len(r4) > 0
print(f"T1: {len(r4)} v4 rows, {len(r5)} v5 rows")
for a, b in zip(r4, r5):
    missing = [k for k in V5_ONLY if k not in b]
    d = diff(strip(a, ("sec",)), strip(b, ("sec",) + V5_ONLY))
    same = not d and not missing
    ok &= same
    print(f"  rho = {a.get('rho')} / {b.get('rho')}: {'IDENTICAL' if same else 'DIFFERS'}"
          + (f"; differing keys {d}" if d else "") + (f"; v5 additions missing {missing}" if missing else "")
          + (f"; v5 coverage {b.get('coverage')}, F1 checks {b.get('f1')}" if same else ""))
MJ = os.environ.get("T1_MJSON")
if MJ:
    a, b = (json.load(open(x)) for x in MJ.split(":"))
    def norm(J, extra):
        J = {k: v for k, v in J.items() if k not in ("env", "version") + extra}
        for key in ("rows",):
            J[key] = [strip(r, ("sec",) + (V5_ONLY if extra else ())) for r in J.get(key, [])]
        if J.get("chosen"):
            J["chosen"] = strip(J["chosen"], ("sec",) + (V5_ONLY if extra else ()))
        return J
    na, nb = norm(a, ()), norm(b, ("code", "code_env", "code_files"))
    d = diff(na, nb)
    ok &= not d
    print(f"  proof JSON: {'IDENTICAL' if not d else 'DIFFERS'}" + (f"; differing keys {d}" if d else "")
          + f" (v5 additions present: {[k for k in ('code', 'code_env', 'code_files') if k in b]})")
print("T1 RESULT:", "PASS" if ok else "FAIL")
if len(sys.argv) > 3:
    rc = load(sys.argv[3])
    same = len(rc) == len(r4) and all(not diff(strip(a, ("sec",)), strip(c, ("sec",))) for a, c in zip(r4, rc))
    print(f"(information) v4 on this run vs committed v4 rows, minus sec: {'IDENTICAL' if same else 'DIFFERS'}"
          + ("" if same else f"; per row {[diff(strip(a, ('sec',)), strip(c, ('sec',))) for a, c in zip(r4, rc)]}"))
sys.exit(0 if ok else 1)
