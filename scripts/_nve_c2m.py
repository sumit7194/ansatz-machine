#!/usr/bin/env python3
"""C2-M (data/nve/route1_check/C2_M_REGISTRATION.md): CAPD's finite M_F plus more Chebyshev nodes, region-B pilots.

Modes (BOX = P2 | P3, with that pilot's R1_* environment as in air/v7_pB.sh):
  cover    the 25 closed R/5 cells of v2's kbox, each run through the C2-4 glue (driver v2, IdQR), two at a time.
           A cell is ACCEPTED only if its record shows H1-H4 (registration 5). A cell that fails is refined into its
           4 quadrants (R/10); a failing quadrant into 4 (R/20); a failing R/20 cell STOPS the pilot. -> c2m_<BOX>_cover.json
  m1       control M1: every accepted cell's enclosures of F, tr M0 and tr M1 must CONTAIN the point values inside it.
           Centre cell: the step 0' R/5 samples (P2); every other cell (and P3's centre): one new evaluation at its centre.
           SLICE=i/n splits the new evaluations between processes (resumable jsonl).
  verdict  the proof file in v5's schema (n from v5's formula, NMAX = 160 asserted; the region-B precondition and
           self-test over the box, as v5's prove), then v6's verdict with EXACTLY two source substitutions, each
           asserted to find its original text: (1) v5's Dyson coverage gate (F3) -> the C2-M cover gate (every leaf
           cell accepted with H1-H4, the cover complete, no STOP); (2) the node-precision assertion inserted after the
           interpolants (2 x the largest node radius <= 1e-3 x the ATAP error term).
           C2M_PLANT=M2 plants M_X = 0.5 x the sampled max |X| on E_rho (v6 must ALARM "proved M below a sample");
           C2M_PLANT=M4 plants a node radius 1e-2 into the precision check (it must trip).
  m3       control M3, a DRY run of the cover's control flow (no CAPD): a forced refusal of the centre R/5 cell must
           take the R/10 path, and forced refusals down to R/20 must STOP.
    BOX=P2 <env> .venv313/bin/python -I -u scripts/_nve_c2m.py cover|m1|verdict|m3
"""
import hashlib
import inspect
import json
import math
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
BOX = os.environ["BOX"]
assert BOX in ("P2", "P3"), "C2-M covers the region-B pilots only (registration: scope)"
import _nve_route1_segment_v7B as L        # noqa: E402
from flint import acb, arb, ctx             # noqa: E402

ctx.prec = 256
S6, S5, S7, V = L.S6, L.S5, L.S7, L.V
NMAX_C2M = 160                              # the Bridge's ruling (registration 4)
RHO = 4.0
assert [float(r) for r in L.S4.RHOS4] == [RHO], "C2-M runs at rho = 4 only (R1_RHOS=4)"
ROOT = os.path.dirname(HERE)
OUTD = os.path.join(ROOT, "data", "nve", "route1_check", "c2")
GLUE = os.path.join(HERE, "_nve_c2_capd.py")
PLANT = os.environ.get("C2M_PLANT", "")

# ------------------------------------------------------------------------------------------------ code hash (F2)
assert S6.MODE == "F", "C2-M runs in F mode only (read F8)"
CODE_FILES = L.CODE_FILES + ("c2_capd/c2_driver.cpp", "_nve_c2_capd.py", "_nve_c2m.py")
DRIVER_BIN = os.path.join(HERE, "c2_capd", "build", "c2_driver_v2")      # read F5: the binary the glue runs is hashed
ENVM = L.ENV7B + "; C2-M (CAPD v2 cover, NMAX 160)"
CODE = hashlib.sha256(b"".join(open(os.path.join(HERE, f), "rb").read() for f in CODE_FILES)
                      + open(DRIVER_BIN, "rb").read() + ENVM.encode()).hexdigest()[:16]
BASE = f"c2m{V.TAG}{S5.KTAG}{S6.MTAG}_{CODE}"
for mod in (S5, S6, S7, L):
    mod.CODE, mod.CODE_FILES, mod.BASE = CODE, CODE_FILES, BASE
S5.ENVSTR = ENVM
S5.MJSON = os.path.join(V.OUTD, f"route1_seg_M_{BASE}{'_' + PLANT if PLANT else ''}.json")   # read F3: plants apart
S5.LOG5 = V.LOG = os.path.join(V.OUTD, f"route1_seg_{BASE}.out")
S6.NODEF = os.path.join(V.OUTD, f"route1_seg_nodes_{BASE}.jsonl")
S6.VJSON = os.path.join(V.OUTD, f"route1_seg_verdict_{BASE}{'_' + PLANT if PLANT else ''}.json")
say = S5.say

KC, HALF = S6.KC, S6.HALF
R = (HALF * (arb(RHO) + 1 / arb(RHO)) / 2).upper()
KBOX, SUBS = V.kbox(acb(KC), R)
LABEL = os.environ.get("C2M_LABEL", BOX)          # production probes (C2_M_PROBES_REGISTRATION.md) run under their own
assert LABEL.replace("_", "").isalnum()             # label, so their files never collide with the P2/P3 pilots' records
COVER = os.path.join(OUTD, f"c2m_{LABEL}_cover.json")


def me(x):
    m, e = x.man_exp()
    return f"{int(m)} {int(e)}"


def cell_of(ball):
    """(exact centre acb, half-side point arb) of a square containing the acb ball"""
    c = acb(ball.real.mid(), ball.imag.mid())
    h = max(ball.real.rad(), ball.imag.rad())
    return c, arb(h).upper()


def quadrants(c, h):
    """4 cells covering the closed square c +- h(1 + i): centres c +- h/2 +- i h/2 (rounded to exact mids, the rounding
    added to the half-side), each of half-side >= h/2"""
    out = []
    for sx in (-1, 1):
        for sy in (-1, 1):
            q = c + acb(sx * h / 2, sy * h / 2)
            qc = acb(q.real.mid(), q.imag.mid())
            err = max((q.real - qc.real).abs_upper(), (q.imag - qc.imag).abs_upper())
            qh = (h / 2 + err).upper()
            quarter = c + acb(sx * h / 2 + arb(0, h / 2), sy * h / 2 + arb(0, h / 2))   # the closed quarter
            assert (qc + qh * V.UNIT).contains(quarter), "a quadrant does not contain its quarter"
            out.append((qc, qh))
    return out


def base_env():
    e = dict(os.environ, C2_STAGE="c2m", C2_VARIANT="_v2", C2_TOL="1e-15", C2_ORDER="20", C2_KDIV="5")
    e.pop("C2_PLANT", None)
    e.pop("C2_SMOKE", None)
    e.pop("C2_HSDIV", None)
    return e


def cell_id(cid):
    return cid if LABEL == BOX else f"{LABEL}-{cid}"


def drive_json(cid):
    return os.path.join(OUTD, f"c2m_{BOX}_k5_o20_v2_tol1e-15_cell{cell_id(cid)}_drive.json")


NONCE = {}


def accept(rec, cid=None):
    """the H1-H4 record of a cell (registration 5); the record must be THIS run's (read F2) and the IdQR driver's (F5)"""
    if rec is None:
        return dict(ok=False, why="no record (the glue crashed)")
    if cid is not None and cid in NONCE and (rec.get("run_id"), rec.get("cell")) != NONCE[cid]:
        return dict(ok=False, why="the record is not this run's (nonce or cell mismatch)")
    hdr = rec.get("driver_header") or ""
    if rec.get("rc") == 0 and hdr != "dry" and "policy IdQR (B = I)" not in hdr:
        return dict(ok=False, why="the driver header does not show the IdQR policy")
    if rec.get("rc") != 0:
        return dict(ok=False, why=" | ".join(rec.get("refused") or ["rc != 0"]), H1=not any(
            "start" in r for r in (rec.get("refused") or [])))
    mg = rec.get("margins") or {}
    loops_ok = all(str(lp) in mg for lp in (0, 1))
    pos = loops_ok and all(mg[str(lp)][kk] > 0 for lp in (0, 1) for kk in ("a1", "D2", "G1_2", "G2_2"))
    try:
        fin = all(acb(arb(rec[q][0]), arb(rec[q][1])).is_finite() for q in ("F", "T0", "T1"))
    except (ValueError, TypeError):
        fin = False
    ok = bool(pos and fin)
    return dict(ok=ok, H1=True, H2=bool(loops_ok and all(mg[str(lp)]["a1"] > 0 for lp in (0, 1))),
                H3=bool(loops_ok and all(mg[str(lp)][kk] > 0 for lp in (0, 1) for kk in ("D2", "G1_2", "G2_2"))),
                H4=bool(fin and rec.get("driver_header") is not None), margins=mg,
                why=None if ok else "a margin or finiteness missing")


def run_cells(cells, dry_refuse=None):
    """cells: list of (cid, centre, h). Runs them two at a time (or, dry, decides by dry_refuse). -> {cid: record}"""
    out = {}
    if dry_refuse is not None:
        good = lambda: dict(rc=0, F=["1", "0"], T0=["1", "0"], T1=["1", "0"],
                            margins={"0": dict(a1=1, D2=1, G1_2=1, G2_2=1), "1": dict(a1=1, D2=1, G1_2=1, G2_2=1)},
                            driver_header="dry", t_capd=0.0)
        for cid, c, h in cells:
            mode = dry_refuse.get(cid) if isinstance(dry_refuse, dict) else ("none" if cid in dry_refuse else None)
            rec = good()
            if mode == "none":
                rec = None                                   # the glue crashed
            elif mode == "rc":
                rec = dict(rc=2, refused=["REFUSED (dry)"])  # the driver refused
            elif mode == "margin":
                del rec["margins"]["1"]                       # a loop's margins missing
            elif mode == "nonfinite":
                rec["F"] = ["nan", "0"]                       # a non-finite enclosure
            elif mode == "zero":
                rec["margins"]["0"]["G2_2"] = 0               # a margin not positive
            out[cid] = rec
        return out
    pending = list(cells)
    running = []
    while pending or running:
        while pending and len(running) < 2:
            cid, c, h = pending.pop(0)
            env = base_env()
            env["C2_CELL"] = f"{me(c.real)} {me(c.imag)} {me(h)}"
            env["C2_CELL_ID"] = cell_id(cid)
            env["C2_RUN_ID"] = f"{CODE}|{cid}|{time.time_ns()}"          # read F2: the record must carry this nonce
            NONCE[cid] = (env["C2_RUN_ID"], env["C2_CELL"])
            if os.path.exists(drive_json(cid)):
                os.remove(drive_json(cid))                               # read F2: never reuse an earlier record
            logf = open(os.path.join(OUTD, f"c2m_{LABEL}_cell{cid}.out"), "w")
            p = subprocess.Popen([sys.executable, "-I", "-u", GLUE, "drive"], env=env, stdout=logf, stderr=subprocess.STDOUT,
                                 cwd=ROOT)
            running.append((cid, p, logf, time.time()))
        time.sleep(2)
        for item in list(running):
            cid, p, logf, t0 = item
            if p.poll() is not None:
                logf.close()
                running.remove(item)
                path = drive_json(cid)
                rec = json.load(open(path)) if os.path.exists(path) else None
                out[cid] = rec
                say(f"  cell {cid}: rc {None if rec is None else rec.get('rc')} [{time.time() - t0:.0f} s]")
    return out


def cover(dry_refuse=None):
    t0 = time.time()
    level0 = []
    for i, d in enumerate(SUBS):
        c, h = cell_of(acb(KC) + d)
        level0.append((f"L0_{i}", c, h))
    # coverage assertions: kbox asserts its 25 cells cover the square; each cell's square contains its kbox ball
    for (cid, c, h), d in zip(level0, SUBS):
        b = acb(KC) + d
        assert (c + h * V.UNIT).contains(b), f"cell {cid} does not contain its kbox ball"
    leaves, cells, stop = [], {}, None
    todo, level = level0, 0
    while todo:
        recs = run_cells(todo, dry_refuse)
        nxt = []
        for cid, c, h in todo:
            acc = accept(recs.get(cid), None if dry_refuse is not None else cid)
            cells[cid] = dict(level=level, centre=[c.real.str(30), c.imag.str(30)], h=float(h),
                              exact=dict(re=me(c.real), im=me(c.imag), h=me(h)),
                              cell_env=f"{me(c.real)} {me(c.imag)} {me(h)}", accept=acc,
                              rec={k: recs[cid].get(k) for k in ("F", "T0", "T1", "t_capd", "steps", "refused",
                                                                 "run_id", "cell")}
                              if recs.get(cid) else None)
            if acc["ok"]:
                leaves.append((cid, c, h, recs[cid]))
            elif level < 2:
                for j, (qc, qh) in enumerate(quadrants(c, h)):
                    nxt.append((f"{cid}.{j}", qc, qh))
            else:
                stop = f"cell {cid} (R/20) not accepted: {acc.get('why')}"
        if stop:
            break
        todo, level = nxt, level + 1
    MX = None
    if not stop:
        sups = [[acb(arb(r[q][0]), arb(r[q][1])).abs_upper() for q in ("F", "T0", "T1")] for _cid, _c, _h, r in leaves]
        MX = [V.amax([s[m] for s in sups]) for m in range(3)]
    t_capd = sum((cells[c]["rec"] or {}).get("t_capd") or 0 for c in cells)
    res = dict(box=BOX, code=CODE, k_c=str(KC), half=str(HALF), R=float(R), rho=RHO, n_cells=len(cells),
               n_leaves=len(leaves), stop=stop, M=None if MX is None else [V.ser(x) for x in MX],
               t_capd_total=round(t_capd, 1), wall=round(time.time() - t0, 1), dry=dry_refuse is not None, cells=cells,
               leaves=[cid for cid, *_ in leaves])
    if dry_refuse is None:
        json.dump(res, open(COVER, "w"), indent=1)
    say(f"C2-M cover {LABEL}: {len(leaves)} leaves of {len(cells)} cells; stop {stop}; "
        f"M {res['M'] and [V.hi_sci(arb(x)) for x in res['M']]}; CAPD {t_capd:.0f} s total, wall {res['wall']} s")
    return res


def m3():
    """control M3 (dry; it runs the real cover(), quadrants() and accept()): (a) centre-cell records that fail in each
    of accept()'s ways (a crash, a driver refusal, a missing loop's margins, a non-finite enclosure, a zero margin), one
    per run, must each take the R/10 path; (b) the centre cell, its quadrant .0 and that quadrant's R/20 child .0.0
    refused must STOP (any refused R/20 cell stops the pilot)"""
    a_ok, a_runs = True, {}
    for mode in ("none", "rc", "margin", "nonfinite", "zero"):
        ra = cover(dry_refuse={"L0_12": mode})
        ok = (ra["stop"] is None and "L0_12" not in ra["leaves"]
              and all(f"L0_12.{j}" in ra["leaves"] for j in range(4)) and ra["n_leaves"] == 28)
        a_runs[mode] = ok
        a_ok &= ok
    rb = cover(dry_refuse={"L0_12": "none", "L0_12.0": "none", "L0_12.0.0": "none"})
    b_ok = rb["stop"] is not None and "L0_12.0.0" in rb["stop"]
    out = dict(M3a_refinement_path=a_ok, M3a_by_mode=a_runs, M3b_stop=b_ok, b=dict(stop=rb["stop"]))
    json.dump(out, open(os.path.join(OUTD, f"c2m_{LABEL}_M3.json"), "w"), indent=1)
    print(f"C2-M control M3 {LABEL}: refinement path {'FIRED' if a_ok else 'DID NOT FIRE'}; R/20 STOP "
          f"{'FIRED' if b_ok else 'DID NOT FIRE'}", flush=True)
    sys.exit(0 if (a_ok and b_ok) else 1)


def m1():
    """control M1: containment of point values in every accepted cell's enclosures"""
    C = json.load(open(COVER))
    assert C["stop"] is None and C["code"] == CODE
    path = os.path.join(OUTD, f"c2m_{LABEL}_M1.jsonl")
    done = {}
    if os.path.exists(path):
        for ln in open(path):
            d = json.loads(ln)
            done[d["key"]] = d
    sl = os.environ.get("SLICE", "0/1")
    i0, nsl = (int(v) for v in sl.split("/"))
    jobs = []
    # the step 0' samples belong to the P2/P3 pilots' own boxes; a labelled probe's box differs, so every cell of a
    # probe gets one new centre evaluation instead (and the all-81 assert does not apply)
    samp_file = os.path.join(OUTD, f"step0p_{BOX}_k5_samples.jsonl") if LABEL == BOX else os.path.join(OUTD, "__none__")
    for idx, cid in enumerate(C["leaves"]):
        cell = C["cells"][cid]
        ex = cell["exact"]
        f_ = lambda t: arb(int(t.split()[0])) * arb(2) ** int(t.split()[1])
        c = acb(f_(ex["re"]), f_(ex["im"]))
        h = f_(ex["h"])
        box = c + h * V.UNIT
        enc = [acb(arb(cell["rec"][q][0]), arb(cell["rec"][q][1])) for q in ("F", "T0", "T1")]
        if cid == "L0_12" and os.path.exists(samp_file):
            for ln in open(samp_file):
                d = json.loads(ln)
                k = acb(arb(d["k"][0]), arb(d["k"][1]))
                if not box.contains(k):
                    continue
                vals = [acb(arb(d[q][0]), arb(d[q][1])) for q in ("F", "T0", "T1")]
                key = f"{C['code']}|{cid}|{cell['cell_env']}|sample{d['i']},{d['j']}"
                if key not in done:
                    done[key] = dict(key=key, cell=cid, reused=True,
                                     contained=[bool(e.contains(v)) for e, v in zip(enc, vals)])
                    with open(path, "a") as fh:
                        fh.write(json.dumps(done[key]) + "\n")
        else:
            jobs.append((idx, cid, acb(c.real.mid(), c.imag.mid()), enc))
    for idx, cid, k, enc in jobs:
        key = f"{C['code']}|{cid}|{C['cells'][cid]['cell_env']}|centre"
        if idx % nsl != i0 or key in done:
            continue
        r = V.evaluate(k.real, k.imag, S6.REF)
        vals = [acb(arb(r[q][0]), arb(r[q][1])) for q in ("F", "T0", "T1")]
        done[key] = dict(key=key, cell=cid, reused=False, sec=r["sec"],
                         contained=[bool(e.contains(v)) for e, v in zip(enc, vals)])
        with open(path, "a") as fh:
            fh.write(json.dumps(done[key]) + "\n")
            fh.flush()
            os.fsync(fh.fileno())
        print(f"M1 {cid}: contained {done[key]['contained']} [{r['sec']} s]", flush=True)
    need = {f"{C['code']}|{cid}|{C['cells'][cid]['cell_env']}|centre" for _i, cid, _k, _e in jobs}
    cur = {k: v for k, v in done.items() if k.startswith(C["code"] + "|")}     # read F4: only this cover's records
    nsamp = sum(1 for k in cur if "|sample" in k)
    if os.path.exists(samp_file) and "L0_12" in C["leaves"]:
        assert nsamp == 81, f"M1: {nsamp} of the 81 centre-cell samples were used"
    done = cur
    if need <= set(done):
        allc = all(all(d["contained"]) for d in done.values())
        out = dict(n_checked=len(done), n_new=len(need), all_contained=allc,
                   failures=[d["key"] for d in done.values() if not all(d["contained"])])
        json.dump(out, open(os.path.join(OUTD, f"c2m_{LABEL}_M1.json"), "w"), indent=1)
        print(f"C2-M control M1 {LABEL}: {'PASS' if allc else 'FAIL'} ({len(done)} values)", flush=True)


# ------------------------------------------------------------------------------------------------ verdict
def cover_gate(cov):
    """substitution (1): the C2-M cover gate, replacing v5's Dyson coverage (F3) gate (read F6: M recomputed from
    the leaves' records, the cells' geometry re-checked, and the proof file's M_F at least the cover's unless planted)"""
    C = json.load(open(COVER))
    assert C["code"] == CODE, "F2 gate: the cover was made by another code"
    assert C["stop"] is None, f"C2-M cover STOPPED: {C['stop']}"
    assert cov["leaves"] == C["n_leaves"] and cov["cells"] == C["n_cells"], "the proof file's coverage is not the cover's"
    f_ = lambda t: arb(int(t.split()[0])) * arb(2) ** int(t.split()[1])
    sups = [arb(0), arb(0), arb(0)]
    for cid in C["leaves"]:
        cell = C["cells"][cid]
        a = cell["accept"]
        assert a["ok"] and a["H1"] and a["H2"] and a["H3"] and a["H4"], f"cell {cid} lacks H1-H4"
        r = cell["rec"]
        for m, q in enumerate(("F", "T0", "T1")):
            sups[m] = V.amax((sups[m], acb(arb(r[q][0]), arb(r[q][1])).abs_upper()))
        ex = cell["exact"]
        # re-read F6: the geometry the RUN used (its record's own cell string and nonce), not two copies of one variable
        assert r.get("cell") == f"{ex['re']} {ex['im']} {ex['h']}", f"cell {cid}: its run used another geometry"
        assert (r.get("run_id") or "").startswith(CODE + f"|{cid}|"), f"cell {cid}: its record is not this code's run"
    for m, nm in enumerate(("MF", "MT0", "MT1")):
        # re-read F6: a printed-and-parsed ball's LOWER end sits below the exact value; compare its upper end
        assert bool(V.par_up(C["M"][m]) >= sups[m].upper()), f"the cover's {nm} is below its leaves' sup"
        if not PLANT.startswith("M2"):
            assert bool(V.par_up(cov[nm]) >= sups[m].upper()), f"the proof file's {nm} is below the cover's leaves' sup"

    def covered(cid):
        if cid in C["leaves"]:
            return True
        kids = [f"{cid}.{j}" for j in range(4)]
        return all(k in C["cells"] and covered(k) for k in kids)
    assert all(covered(f"L0_{i}") for i in range(25)), "the cover is incomplete"


def node_precision(vals, eF, e0, e1):
    """substitution (2), as amended by erratum C2-M-2 (read F1): 2 x the largest F-node radius <= 1e-3 x F's ATAP term.
    n is sized for F (v5's formula uses M_F), so only F's term is a meaningful scale; the trace terms come out far
    below the trace nodes' radii BY CONSTRUCTION. That is harmless to soundness: every node radius enters the
    interpolant's ball coefficients and is judged by conditions(). So the traces are not asserted here."""
    rads = [max(v[0].real.rad(), v[0].imag.rad()) for v in vals]
    if PLANT == "M4":
        rads[0] = rads[0] + arb("1e-2")
    rmax = V.amax([arb(x) for x in rads])
    assert bool(2 * rmax <= eF / 1000), f"node precision: 2 x max F-node radius {float(rmax):.2e} > 1e-3 x F's ATAP " \
                                        f"term {float(eF):.2e}"


_F3_OLD = '''    cov = ch["coverage"]                          # F3, as v5's verdict
    assert [cov["circle"]["steps"], cov["lasso"]["steps"]] == J["steps"] and min(J["steps"]) > 0
    for loop in ("circle", "lasso"):
        c = cov[loop]
        assert c["bounds"] == c["steps"] and c["ksub"] == S5.KSUB2 and c["pairs"] == c["steps"] * S5.KSUB2, \\
            f"F3 gate: {loop} {c}"
'''
_F3_NEW = '''    C2M_COVER_GATE(ch["coverage"])                # C2-M substitution (1): the cover gate replaces v5's F3
'''
_INTERP_OLD = '''    (pF, qF), (p0, q0), (p1, q1) = (V.interp([v[m] for v in vals], n) for m in range(3))
'''
_INTERP_NEW = '''    (pF, qF), (p0, q0), (p1, q1) = (V.interp([v[m] for v in vals], n) for m in range(3))
    C2M_NODE_PRECISION(vals, eG, e0, e1)          # C2-M substitution (2): the node-precision assertion
'''


def verdict_c2m():
    src = inspect.getsource(S6.verdict)
    assert src.count(_F3_OLD) == 1 and src.count(_INTERP_OLD) == 1, "v6 verdict source changed: substitutions refused"
    src = src.replace(_F3_OLD, _F3_NEW).replace(_INTERP_OLD, _INTERP_NEW).replace("def verdict():", "def _verdict_c2m():")
    g = S6.__dict__
    g["C2M_COVER_GATE"], g["C2M_NODE_PRECISION"] = cover_gate, node_precision
    exec(compile(src, "<v6 verdict, C2-M substituted>", "exec"), g)
    return g["_verdict_c2m"]


def make_proof(planted=None):
    C = json.load(open(COVER))
    assert C["code"] == CODE and C["stop"] is None
    MF, MT0, MT1 = (arb(x) for x in C["M"])
    if planted is not None:
        MF, MT0, MT1 = planted
    kc = KC
    lau_c, laud_c = V.laurent(acb(kc)), V.laurent(acb(kc), True)
    st_ok = V.selftest(kc, lau_c, laud_c)
    pre = V.precondition(KBOX)
    rb = arb(RHO)
    V.TOL_F = S6.tol_for(RHO)
    nr = (4 * MF / ((rb - 1) * arb(V.TOL_F))).log() / rb.log()
    assert nr.is_finite() and nr < NMAX_C2M + 1, f"n > NMAX = {NMAX_C2M}"
    n = max(2, math.ceil(math.log(4 * float(MF) / ((RHO - 1) * V.TOL_F)) / math.log(RHO)))
    n += n % 2
    assert n <= NMAX_C2M, f"n = {n} > NMAX = {NMAX_C2M}"
    den = rb ** n * (rb - 1)
    eF, e0, e1 = (4 * MF / den).upper(), (4 * MT0 / den).upper(), (4 * MT1 / den).upper()
    cov = dict(leaves=C["n_leaves"], cells=C["n_cells"], MF=V.ser(MF), MT0=V.ser(MT0), MT1=V.ser(MT1))
    ch = dict(rho=RHO, n=n, R=V.ser(R), MF=V.ser(MF), MT0=V.ser(MT0), MT1=V.ser(MT1), errF=V.ser(eF), errT0=V.ser(e0),
              errT1=V.ser(e1), precondition=pre, coverage=cov, code=CODE, mode=S6.MODE, tolmode=S6.TOLMODE,
              tol_F=V.TOL_F, planted=PLANT or None)
    out = dict(seg=V.SEG, version="c2m", code=CODE, code_env=ENVM, code_files=list(CODE_FILES), rows=[ch], chosen=ch,
               selftest=st_ok, steps=None, nmax=NMAX_C2M)
    json.dump(out, open(S5.MJSON, "w"), indent=1)
    say(f"C2-M proof file: n = {n}, M = {V.hi_sci(MF)}, {V.hi_sci(MT0)}, {V.hi_sci(MT1)}; precondition {pre['ok']}; "
        f"self-test {st_ok}{'; PLANT ' + PLANT if PLANT else ''}")
    return out


def verdict():
    """the C2-M verdict; C2M_PLANT=M2F|M2T0|M2T1 plants ONE quantity's M at 0.5 x the largest |X| among the REAL
    verdict's v6 ellipse samples (all on the closure of E_rho, so the plant is strictly below the truth; erratum
    C2-M-2 drops the M1 values, which may lie outside E_rho); v6 must then ALARM "proved M below a sample". M4 plants
    an F-node radius into the precision check, which must trip."""
    planted = None
    if PLANT.startswith("M2"):
        which = {"M2F": 0, "M2T0": 1, "M2T1": 2}[PLANT]
        real_vjson = S6.VJSON.replace(f"_{PLANT}.json", ".json")
        real = json.load(open(real_vjson))
        assert real.get("outcome") in ("certified", "not_certified"), "M2 needs a completed real verdict"
        done = S6.load_nodes()
        samp = [arb(0), arb(0), arb(0)]
        nkeys = 0
        for key, r in done.items():
            if "|ellipse" in key and f"n={real['n']}|" in key:
                nkeys += 1
                for m, nm in enumerate(("F", "T0", "T1")):
                    samp[m] = V.amax((samp[m], acb(arb(r[nm][0]), arb(r[nm][1])).abs_upper()))
        assert nkeys >= 8 and all(bool(x > 0) for x in samp), "M2 needs the real verdict's 8 ellipse samples"
        C = json.load(open(COVER))
        Ms = [arb(x) for x in C["M"]]
        Ms[which] = (samp[which] / 2).upper()
        planted = tuple(Ms)
        say(f"C2-M control {PLANT}: planting M[{which}] = 0.5 x sampled max = {V.hi_sci(Ms[which])}")
    make_proof(planted)
    verdict_c2m()()


if __name__ == "__main__":
    {"cover": cover, "m1": m1, "verdict": verdict, "m3": m3}[sys.argv[1]]()
