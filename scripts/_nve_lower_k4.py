"""§159 follow-up (review of a relayed all-spin extension): k = 4 is the second root of disc_w B = 240k(k-4), where
B = 6(w+1)^2 is a perfect square, so c0'' is rational (as at k = 0, the Kerr point). Is the lower-axis monodromy VA there?
Same registered pipeline (run_case: S at two steps, all gates), plus neighbour k = 39/10. E = 4/5, spin 3/5."""
import json, os, sys
sys.path.insert(0, os.path.dirname(__file__))
import sympy as sp
from _nve_lower import run_case, A, z, OUT
from _ts_edge2 import fleet_guard

if __name__ == "__main__":
    g = fleet_guard()
    if g:
        raise SystemExit(f"NOT STARTED: {g}")
    fK = 1 - 1 / (z - sp.I * A) - 1 / (z + sp.I * A)
    ck = os.path.join(OUT, "lower_k4.jsonl")
    for k in (sp.Integer(4), sp.Rational(39, 10)):
        r = run_case("K4", fK, k, sp.Rational(4, 5))
        open(ck, "a").write(json.dumps(r, default=str) + "\n")
        print(f"k={k}: rho_c {r['rho_c']:.3f} zeros {r['zeros_P']} poles {r['poles_P']} count_ok {r['count_ok']} "
              f"S {r['runs']['0.35']['S']:.4e}/{r['runs']['0.2']['S']:.4e} red {r['runs']['0.2']['reducible']} "
              f"fin {r['runs']['0.2']['finite']} gates {r['runs']['0.2']['gates']} -> {r['cls']} (gates_ok {r['gates_ok']})", flush=True)
