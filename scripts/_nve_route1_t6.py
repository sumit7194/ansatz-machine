#!/usr/bin/env python3
"""T-tests of the P4 build (v6, the engine gate, the production driver), Air. [ansatz-machine-personal, 2026-11-27]
Pass criteria are fixed here, before any run; each can fail.

  u1  REPRODUCTION. v6 on [1, 1.1] at spin 3/5 with v5's settings (R1_TOLMODE=abs, rows 3, 4, 5, 6.5, R1_FULLCTL=1)
      against tests52's v5.2 files on this machine and Python:
      (a) every row equal to v5.2's after dropping only v6's additions (tol_F, mode, tolmode), code and sec;
      (b) the proof JSON equal after dropping seg (the moved-segment label), code, code_files, code_env, env and sec;
      (c) all 24 node values (13 nodes, 3 held-out, 8 ellipse) equal to v5.2's node file, string for string;
      (d) the verdict CERTIFIED with the same printed bounds as v5.2/P1: |F| >= 0.265039275, |tr M0| >= 1.993158417,
          |Im tr M1| >= 2.648820879; planted zero refused; the controls as in P1.
  u3  F/k^2, KNOWN ANSWER. v6 in mode Fk2 on [1, 1.1] (rel tolerance, rho 4, full controls): CERTIFIED; the derived
      |F| lower bound is <= min_j |F(node_j)| (an upper bound of the true minimum; a wrong e_g could break this);
      the row's tol_F equals 1e-2 |F(21/20)| ((k_c - R)/k_c)^2 with R = (1/20)(4 + 1/4)/2.
  u6  F2 FOR v6 and the BATCH RERUN. v6's code hash differs from v5.2's; a foreign-code record planted in (a) v6's rows
      file stops v6 prove, (b) v6's node file stops v6 verdict, both with "F2 gate" and nothing new written; (c) the
      untampered verdict rerun is byte-identical and evaluates nothing new.
  fk2files  from an F/k^2 segment's files: the verdict's bounds are >= errF/d^2 and M_F/d^2 (S4).
  synth     a synthetic F/k^2 verdict at small k with a known F = c k^2: n = 2 must NOT certify (a /d error would),
            n = 8 must (S4).
  u7        a moved-segment known answer: v6 at k_c = 2 reproduces P3's row and certifies (S4).
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
        J = {k: v for k, v in J.items() if k not in ("seg", "code", "code_files", "code_env", "env")}
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


def fk2files():
    """S4: from the files of an F/k^2 segment, the verdict's bounds must be at least errF/d^2 and M_F/d^2, with
    d = k_c - R (R recomputed). A /d instead of /d^2, or a wrong R, breaks this at small k."""
    S = v6()
    from flint import arb
    J = json.load(open(S.S5.MJSON))
    vd = json.load(open(S.VJSON))
    ch = J["chosen"]
    rb = arb(ch["rho"])
    R = max(arb(ch["R"]).upper(), (S.HALF * (rb + 1 / rb) / 2).upper())
    d = (S.KC - R).lower()
    eg, mg = (arb(ch["errF"]) / (d * d)).upper(), (arb(ch["MF"]) / (d * d)).upper()
    ok = vd["mode"] == "Fk2" and bool(arb(vd["err"][0]) >= eg) and bool(arb(vd["M"][0]) >= mg) and bool(d > 0)
    check(f"FK2FILES {S.V.SEG}", ok, f"err[0] {vd['err'][0]} >= errF/d^2 {float(eg):.4e}; M[0] {vd['M'][0]} >= "
          f"M_F/d^2 {float(mg):.4e}; d {float(d):.4e}")


def synth():
    """S4: a SYNTHETIC F/k^2 verdict at small k with a known function, in-process (no evaluator run). F(k) = c k^2,
    tr M0 = 1.9, tr M1 = 0.5 + 2.6i, on [1/640, 1/320]; M_F = 2 |c| (k_c + R)^2 bounds |F| on the k-disc. With the
    correct e_g = e_F/d^2 (d = k_c - R = 7/10240), n = 2 gives e_g about 5.7 |c| > |g| = |c|: NOT certified; a /d
    error would give e_g about 1e-3 |c| and certify. n = 8 gives e_g about 1.4e-3 |c|: certified. Both: planted zero
    refused, held-out consistent, M >= samples, the S3 recomputation consistent."""
    import tempfile
    os.environ.update(R1_KC="3/1280", R1_HALF="1/1280", R1_MODE="Fk2", R1_TOLMODE="rel", R1_FULLCTL="1",
                      R1_FLOATS="route1_floats_synth_t6.json")
    fl = os.path.join(E, "route1_floats_synth_t6.json")
    json.dump({"3/1280": dict(F=["1e-7", "0"], T0=["1.9", "0"], T1=["0.5", "2.6"], points=[], lasso=[], geometry_ok=True)},
              open(fl, "w"))
    try:
        S = v6()
        from flint import acb, arb
        V = S.V
        tmp = tempfile.mkdtemp(prefix="t6synth_")
        S.S5.MJSON, S.NODEF, S.VJSON = (os.path.join(tmp, x) for x in ("M.json", "nodes.jsonl", "v.json"))
        S.S5.LOG5 = V.LOG = os.path.join(tmp, "log.out")
        c = acb("0.2", "0.1")
        T0, T1 = acb("1.9"), acb("0.5", "2.6")
        S.load_nodes = lambda: {}
        S.get = lambda done, key, kre, kim: (c * acb(kre.mid(), kim.mid()) ** 2, T0, T1)
        rb = arb(4)
        R = (S.HALF * (rb + 1 / rb) / 2).upper()
        MF = (2 * c.abs_upper() * (S.KC + R) ** 2).upper()
        out = {}
        for n in (2, 8):
            den = rb ** n * (rb - 1)
            row = dict(rho=4.0, n=n, R=V.ser(R), MF=V.ser(MF), MT0=V.ser(arb(3)), MT1=V.ser(arb(3)),
                       errF=V.ser((4 * MF / den).upper()), errT0=V.ser((12 / den).upper()), errT1=V.ser((12 / den).upper()),
                       precondition=dict(ok=True), code=S.CODE, mode="Fk2", tolmode="rel",
                       coverage=dict(circle=dict(steps=10, bounds=10, ksub=25, pairs=250),
                                     lasso=dict(steps=10, bounds=10, ksub=25, pairs=250)))
            json.dump(dict(code=S.CODE, chosen=row, rows=[row], selftest=True, steps=[10, 10]), open(S.S5.MJSON, "w"))
            try:
                S.verdict()
            except SystemExit as e:
                out[n] = ("exit", e.code)
                continue
            out[n] = json.load(open(S.VJSON))
        v2, v8 = out[2], out[8]
        ctl = lambda v: isinstance(v, dict) and v["planted_zero_refused"] and v["held_out_consistent"] and v["proved_M_ge_sampled"] \
            and not v["s3_inconsistent"] and not v["alarm"]
        check("SYNTH F/k^2 at small k: n = 2 NOT certified (a /d bug would certify)", ctl(v2) and v2["outcome"] == "not_certified",
              f"outcome {v2['outcome'] if isinstance(v2, dict) else v2}; err {v2['err'][0] if isinstance(v2, dict) else ''}")
        check("SYNTH F/k^2 at small k: n = 8 certified, |F/k^2| near |c| = 0.2236", ctl(v8) and v8["outcome"] == "certified"
              and 0.2 < float(v8["abs_f_ge"]) < 0.2237, f"outcome {v8['outcome'] if isinstance(v8, dict) else v8}; "
              f"|f| >= {v8.get('abs_f_ge') if isinstance(v8, dict) else ''}")
    finally:
        os.remove(fl)


def u7():
    """S4: a MOVED-segment known answer. v6 at spin 3/5 on [39/20, 41/20] (k_c = 2), rho 4, v5's absolute tolerance,
    with P3's floats: its row equals P3's (v5.1) row at k_c = 2, apart from v6's additions and code; and the verdict
    certifies."""
    S = v6()
    r3 = lines(os.path.join(E, "route1_seg_v5_kc2h1o20_2ba10dbd79a83372_rows.jsonl"))
    r6 = lines(S.S5.ROWS)
    drop = ("sec", "code", "tol_F", "mode", "tolmode")
    d = [sorted(k for k in set(a) | set(b) if k not in drop and a.get(k) != b.get(k)) for a, b in zip(r3, r6)]
    vd = json.load(open(S.VJSON))
    check("U7 moved segment k_c = 2: row equal to P3's, verdict certified", len(r3) == len(r6) == 1 and not d[0]
          and vd["outcome"] == "certified" and vd["planted_zero_refused"], f"row differences {d}; outcome {vd['outcome']}; "
          f"|F| >= {vd['abs_f_ge']}")


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
               OUTJ=os.path.join(E, f"route1_seg_engine_{S.BASE}.jsonl"), R1_CODE=S.CODE)
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
    dict(u1=u1, u3=u3, u6=u6, gate=gate, fk2files=fk2files, synth=synth, u7=u7)[sys.argv[1]]()
    print(f"{sys.argv[1]} RESULT:", "PASS" if all(RES) else "FAIL", f"({sum(RES)}/{len(RES)})")
    sys.exit(0 if all(RES) else 1)
