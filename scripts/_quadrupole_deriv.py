"""EXPLORATORY (underscore = not a battery). Item-3 step 1 attempt: derive the consistent
static l=2 (quadrupole) vacuum deformation of Schwarzschild, then test its integrability
with §85. Idea was sound; the EXECUTION hit the wall.

⚠️ DEAD END (2026-06-24): this SWAMPED. The symbolic Ricci of the general (r,θ) 4-function
l=2 ansatz took 2.5 HOURS to build and was still grinding the remaining components at
3h52m (RSS 1.2 GB) — the same SymPy (r,θ)-metric blow-up that killed the rotating-EdGB
work. CONFIRMED: item-3's wall is real and symbolic — even the LINEARIZED STATIC case is
intractable here. Killed it. The tractable path is NUMERICAL (Weyl-formalism metric built
as g(x) floats + numeric vacuum check + §85), which is dedicated multi-session
infrastructure, OR reliable literature transcription (the ZV closed form is not reliably
memorizable — a γ=1 sanity check of my recalled form FAILED, so transcription would be
guessing; not done). Kept as the record of where the wall is. The SCIENCE is already
answered at achievable rigor by §85 (a quadrupole deviation breaks the Carter constant ⇒
modified-gravity rotating BHs, whose quadrupole ≠ Kerr's, are generically non-integrable).
"""

import sys
import time

import sympy as sp

sys.path.insert(0, "/Users/sumit/Github/conjecture_machine/scripts")
from gr_engine import Geometry

r, th = sp.symbols("r theta", positive=True)
M, q = sp.symbols("M q", positive=True)
f = 1 - 2 * M / r
P2 = (3 * sp.cos(th)**2 - 1) / 2

# general static, axisymmetric, l=2 even diagonal ansatz (4 unknown radial functions)
A, B, C, D = [sp.Function(n)(r) for n in ("A", "B", "C", "D")]
g = sp.diag(
    -f * (1 + q * A * P2),
    (1 + q * B * P2) / f,
    r**2 * (1 + q * C * P2),
    r**2 * sp.sin(th)**2 * (1 + q * D * P2),
)

if __name__ == "__main__":
    t0 = time.time()
    geo = Geometry(g, [sp.Symbol("t"), r, th, sp.Symbol("phi")])
    Ric = geo.ricci
    print(f"[Ricci built in {time.time()-t0:.0f}s]  linearized vacuum eqns R_ab = O(q^2):\n", flush=True)
    # extract the O(q) part of each independent Ricci component
    for (i, j) in [(0, 0), (1, 1), (2, 2), (3, 3), (1, 2)]:
        lin = sp.series(sp.cancel(sp.together(Ric[i, j])), q, 0, 2).removeO()
        lin = sp.simplify(lin / q) if lin != 0 else sp.S.Zero          # coefficient of q
        if lin != 0:
            # strip the common angular factor to expose the radial ODE
            print(f"  R_{i}{j} / q =", sp.simplify(lin), flush=True)
    print(f"\n[total {time.time()-t0:.0f}s]", flush=True)
