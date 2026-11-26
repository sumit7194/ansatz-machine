#!/usr/bin/env python3
"""T-tests of the P4 build (v6, the engine gate, the production driver), Air. [ansatz-machine-personal, 2026-11-27]
Pass criteria are fixed here, before any run; each can fail.

  u1  REPRODUCTION. v6 on [1, 1.1] at spin 3/5 with v5's settings (R1_TOLMODE=abs, rows 3, 4, 5, 6.5, R1_FULLCTL=1)
      against tests52's v5.2 files on this machine and Python:
      (a) every row equal to v5.2's after dropping only v6's additions (tol_F, mode, tolmode), code and sec;
      (b) the proof JSON equal after dropping seg (the moved-segment label), code, code_files, env and sec;
      (c) all 24 node values (13 nodes, 3 held-out, 8 ellipse) equal to v5.2's node file, string for string;
      (d) the verdict CERTIFIED with the same printed bounds as v5.2/P1: |F| >= 0.265039275, |tr M0| >= 1.993158417,
          |Im tr M1| >= 2.648820879; planted zero refused; the controls as in P1.
  u3  F/k^2, KNOWN ANSWER. v6 in mode Fk2 on [1, 1.1] (rel tolerance, rho 4, full controls): CERTIFIED; the derived
      |F| lower bound is <= min_j |F(node_j)| (an upper bound of the true minimum; a wrong e_g could break this);
      the row's tol_F equals 1e-2 |F(21/20)| ((k_c - R)/k_c)^2 with R = (1/20)(4 + 1/4)/2.
  u6  F2 FOR v6 and the BATCH RERUN. v6's code hash differs from v5.2's; a foreign-code record planted in (a) v6's rows
      file stops v6 prove, (b) v6's node file stops v6 verdict, both with "F2 gate" and nothing new written; (c) the
      untampered verdict rerun is byte-identical and evaluates nothing new.
  gate ENGINE GATE, both directions. On u1's node file the gate passes 13/13. On a copy with one node's F shifted by
      1e-6 (enclosure moved off the true value) it exits 2 at that node.
    <.venv313 python> -I -u scripts/_nve_route1_t6.py u1|u3|u6|gate"""
import hashlib
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
E = os.path.join(ROOT, "data", "nve", "eps")
V52 = "c3ef97b3d4943b24"                          # tests52's v5.2 code hash, printed in its log header
PY313, PY314 = os.environ.get("PY313", sys.executable), os.environ.get("PY314", ".venv/bin/python")
V6 = os.path.join(HERE, "_nve_route1_segment_v6.py")
RES = []


def check(name, ok, note=""):
    RES.append(ok)
    print(f"{name}: {'PASS' if ok else 'FAIL'}  ({note})", flush=True)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest() if os.path.exists(p) else None


def lines(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def v6():
    sys.path.insert(0, HERE)
    import _nve_route1_segment_v6 as S
    return S


def u1():
    S = v6()
    r5 = lines(os.path.join(E, f"route1_seg_v5_{V52}_rows.jsonl"))
    r6 = lines(S.S5.ROWS)
    drop6 = ("sec", "code", "tol_F", "mode", "tolmode")
    d = [(a.get("rho"), sorted(k for k in set(a) | set(b) if k not in drop6 and a.get(k) != b.get(k)))
         for a, b in zip(r5, r6)]
    check("U1a rows equal to v5.2's", len(r5) == len(r6) == 4 and all(not x for _, x in d)
          and all(b.get("tolmode") == "abs" and b.get("tol_F") == 1e-3 for b in r6), f"differences {d}")
    m5 = json.load(open(os.path.join(E, f"route1_seg_M_v5_{V52}_nseg1.json")))
    m6 = json.load(open(S.S5.MJSON))

    def norm(J):
        J = {k: v for k, v in J.items() if k not in ("seg", "code", "code_files", "env")}
        J["rows"] = [{k: v for k, v in r.items() if k not in drop6} for r in J["rows"]]
        J["chosen"] = {k: v for k, v in J["chosen"].items() if k not in drop6}
        return J
    a, b = norm(m5), norm(m6)
    dd = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
    check("U1b proof JSON equal to v5.2's", not dd, f"differing keys {dd}")
    n5 = {r["key"]: r for r in lines(os.path.join(E, f"route1_seg_nodes_arb_v5cert_{V52}.jsonl"))}
    n6 = {r["key"]: r for r in lines(S.NODEF)}

    def role(k):                               # node j / held t=s / ellipse j: the last field of either key
        return k.split("|")[-1]
    by5 = {role(k): r for k, r in n5.items()}
    by6 = {role(k): r for k, r in n6.items()}
    same = [nm for nm in by6 if nm in by5 and all(by5[nm][x] == by6[nm][x] for x in ("F", "T0", "T1", "k"))]
    check("U1c node values equal to v5.2's", len(by6) == 24 and len(same) == 24, f"{len(same)}/{len(by6)} equal")
    v5 = json.load(open(os.path.join(E, f"route1_seg_verdict_v2_arb_v5cert_{V52}_nseg1.json")))["segs"][0]
    vd = json.load(open(S.VJSON))
    got = (vd["abs_f_ge"], vd["abs_trM0_ge"], vd["abs_Im_trM1_ge"])
    want = (v5["abs_F_ge"], v5["abs_trM0_ge"], v5["abs_Im_trM1_ge"])
    check("U1d verdict as v5.2/P1", vd["outcome"] == "certified" and got == want and got[0] == "0.265039275"
          and vd["planted_zero_refused"] and vd["held_out_consistent"] and vd["proved_M_ge_sampled"]
          and vd["planted_precondition_fires"] and vd["shrunk_M_below_sampled"],
          f"outcome {vd['outcome']}, bounds {got} vs {want}, shrunk below {vd.get('shrunk_M_below_sampled')}")


def u3():
    S = v6()
    vd = json.load(open(S.VJSON))
    nodes = [r for r in lines(S.NODEF) if "|node" in r["key"]]
    from flint import acb, arb
    mx = min(float(acb(arb(r["F"][0]), arb(r["F"][1])).abs_upper()) for r in nodes)
    row = lines(S.S5.ROWS)[0]
    R = 0.05 * (4 + 0.25) / 2
    want = 1e-2 * abs(S.FC) * ((1.05 - R) / 1.05) ** 2
    check("U3 F/k^2 known answer", vd["outcome"] == "certified" and float(vd["abs_F_ge"]) <= mx and vd["planted_zero_refused"]
          and vd["held_out_consistent"] and vd["proved_M_ge_sampled"] and abs(row["tol_F"] / want - 1) < 1e-12,
          f"outcome {vd['outcome']}; derived |F| >= {vd.get('abs_F_ge')} <= min node |F| {mx:.9f}; |F/k^2| >= {vd['abs_f_ge']}; "
          f"n {vd['n']}; tol_F {row['tol_F']:.6e} vs {want:.6e}")


def run(stage, env=None):
    p = subprocess.run([PY313, "-I", "-u", V6, stage], capture_output=True, text=True, env=env or os.environ, cwd=ROOT)
    return p.returncode, p.stdout + p.stderr


def u6():
    S = v6()
    check("U6 v6 hash differs from v5.2's", S.CODE != V52 and len(S.CODE) == 16, f"v6 code hash differs: {S.CODE != V52}")
    for nm, path, stage in (("U6a foreign record in v6's rows file", S.S5.ROWS, "prove"),
                            ("U6b foreign record in v6's node file", S.NODEF, "verdict")):
        bak = path + ".t6bak"
        shutil.copy2(path, bak)
        watch = [p for p in (S.S5.ROWS, S.NODEF, S.S5.MJSON, S.VJSON, S4ck(S)) if p != path]
        before = {p: sha(p) for p in watch}
        try:
            rec = lines(path)[0]
            rec["code"] = "0" * 16
            if "key" in rec and "|code=" in rec["key"]:
                rec["key"] = rec["key"].rsplit("|code=", 1)[0] + "|code=" + "0" * 16
            if "key" in rec:
                rec["key"] += "|planted"
            with open(path, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
            rc, out = run(stage)
            check(nm, rc != 0 and "F2 gate" in out and all(sha(p) == h for p, h in before.items()), f"rc {rc}")
        finally:
            shutil.move(bak, path)
    h0, n0 = sha(S.VJSON), sha(S.NODEF)
    rc, out = run("verdict")
    check("U6c verdict rerun byte-identical, nothing evaluated", rc == 0 and sha(S.VJSON) == h0 and sha(S.NODEF) == n0
          and "new evaluations 0" in out, f"rc {rc}")


def S4ck(S):
    return S.S4.CKFILE


def gate():
    S = v6()
    env = dict(os.environ, NODES=S.NODEF, FLOATS=os.path.join(E, os.environ["R1_FLOATS"]),
               OUTJ=os.path.join(E, f"route1_seg_engine_{S.BASE}.jsonl"))
    p = subprocess.run([PY314, "-I", "-u", os.path.join(HERE, "_nve_route1_engine_gate.py")], env=env, cwd=ROOT,
                       capture_output=True, text=True)
    out = p.stdout + p.stderr
    check("GATE passes on u1's nodes", p.returncode == 0 and "ENGINE GATE: 13/13" in out, out.strip().splitlines()[-1])
    tam = S.NODEF + ".tampered"
    recs = lines(S.NODEF)
    for r in recs:
        if r["key"].endswith("|node3"):
            from flint import arb
            x = arb(r["F"][0]) + arb("1e-6")
            r["F"][0] = x.str(30)
    with open(tam, "w") as fh:
        fh.write("".join(json.dumps(r) + "\n" for r in recs))
    out2 = os.path.join(E, f"route1_seg_engine_{S.BASE}.tampered.jsonl")
    if os.path.exists(out2):
        os.remove(out2)
    p = subprocess.run([PY314, "-I", "-u", os.path.join(HERE, "_nve_route1_engine_gate.py")],
                       env=dict(env, NODES=tam, OUTJ=out2), cwd=ROOT, capture_output=True, text=True)
    o = p.stdout + p.stderr
    check("GATE misses a shifted enclosure (other direction)", p.returncode == 2 and "FIRST MISS" in o and "node3" in o,
          f"rc {p.returncode}")


if __name__ == "__main__":
    dict(u1=u1, u3=u3, u6=u6, gate=gate)[sys.argv[1]]()
    print(f"{sys.argv[1]} RESULT:", "PASS" if all(RES) else "FAIL", f"({sum(RES)}/{len(RES)})")
    sys.exit(0 if all(RES) else 1)
