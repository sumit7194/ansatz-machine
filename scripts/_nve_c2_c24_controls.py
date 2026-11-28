#!/usr/bin/env python3
"""C2-4 must-fire controls (addendum C2-4), run after the focused read and before step 0''. Each control runs the glue's
drive with one plant, and must be REFUSED BY ITS OWN GUARD (matched on the refusal reason, so a control cannot pass on
an incidental guard):
  K1  wrong start sign (-s0 given to the (a3) start match)   -> "(a3)"                           [P2 and P1]
  K2  a segment from the base point across B's cut (B = -20)  -> "(a1) ... on this edge"           [P2]
  K3  the circle disc radius planted at 0.01                  -> "(a2)"                           [P1]
  K4  a non-point time injected once                          -> "(b) the set's time is not a point"  [P2]
  K2s, K3s  as K2, K3 with the a priori edge guard skipped (read F2): the per-step guard (or, for a cut crossing,
            CAPD's interval sqrt, which throws on a negative argument) must refuse
    .venv313/bin/python -I -u scripts/_nve_c2_c24_controls.py
"""
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTD = os.path.join(ROOT, "data", "nve", "route1_check", "c2")
BASE = dict(NVE_SPIN="3/5", R1_R0="1.35", R1_RHOS="4", R1_MODE="F", R1_TOLMODE="rel", C2_STAGE="step0pp",
            C2_VARIANT="_v2", C2_TOL="1e-15", C2_ORDER="20", C2_KDIV="5")
BOXENV = dict(P2=dict(BOX="P2", R1_KC="83/20", R1_HALF="1/20", R1_FLOATS="route1_floats_v7B_3_5.json"),
              P1=dict(BOX="P1", R1_KC="79/20", R1_HALF="1/20", R1_FLOATS="route1_floats_v7p_3_5.json"))
CASES = [("K1", "P2", ["(a3)"]), ("K1", "P1", ["(a3)"]),
         ("K2", "P2", ["(a1) root argument not certified off the cut on this edge"]),
         ("K2s", "P2", ["(a1) root argument not certified off the cut on the whole-step enclosure",
                        "capd exception below the minimal step"]),   # read F2: with the edge guard skipped; CAPD's
         ("K3", "P1", ["(a2) circle inner argument not certified inside its disc on this edge"]),   # interval sqrt
         ("K3s", "P1", ["(a2) circle inner argument not inside its disc on the whole-step enclosure"]),  # throws on a cut
         ("K4", "P2", ["(b) the set's time is not a point"])]
res = []
for plant, box, want in CASES:
    env = dict(os.environ, **BASE, **BOXENV[box], C2_PLANT=plant)
    pr = subprocess.run([sys.executable, "-I", "-u", os.path.join(ROOT, "scripts", "_nve_c2_capd.py"), "drive"],
                        env=env, capture_output=True, text=True, cwd=ROOT)
    tag = f"{box}_k5_o20_v2_tol1e-15_{plant}"
    rec = json.load(open(os.path.join(OUTD, f"step0pp_{tag}_drive.json")))
    why = " | ".join(rec.get("refused") or [])
    fired = rec.get("rc") != 0 and any(w in why for w in want)
    res.append(dict(plant=plant, box=box, fired=fired, refused=why[:300], want=want))
    print(f"{plant} {box}: {'FIRED' if fired else 'DID NOT FIRE'}  ({why[:200]})", flush=True)
ok = all(r["fired"] for r in res)
json.dump(dict(controls=res, all_fired=ok), open(os.path.join(OUTD, "c24_controls.json"), "w"), indent=1)
print(f"C2-4 controls: {'ALL FIRED' if ok else 'NOT ALL FIRED'}", flush=True)
sys.exit(0 if ok else 1)
