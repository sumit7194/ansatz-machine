#!/usr/bin/env python3
"""Double-expansion Killing solver: order by order in BOTH coupling zeta and spin chi.

WHY BOTH. The sGB solution is a truncated double series and solves no field equation exactly, so
asking `_kt_exact` for an exact Killing tensor returns zero automatically -- an artifact of
truncation. The one-parameter solver (_kt_perturb) fixed that for zeta but still needs an exact
background, and "Kerr truncated at chi^2" is not one: its exact Killing space is just the
reducibles, Carter is not in it, and the question "does Carter survive" cannot even be posed.

THE ORDER IS NOT A CHOICE. Ayzenberg & Yunes note the lower-spin solutions remain Petrov type D,
which admits a Carter-like tensor; type I first appears at O(chi^2). So at O(chi) Carter survives
and a search there is vacuous. O(chi^2) is where the obstruction lives.

THE STRUCTURE, and why it is cheap. Expanding {H,F} = 0 at order (i,j) = (1,n):

    {H^(0,0), F^(1,n)} = -[ sum_{j>=1} {H^(0,j), F^(1,n-j)} + sum_j {H^(1,j), F^(0,n-j)} ]

The unknown always sits under the SCHWARZSCHILD bracket. Everything on the right is known from
lower orders. So the tower is triangular, and the homogeneous operator is THE SAME MATRIX at every
level -- built once per rank and reused six times. Schwarzschild's bracket is also cheaper than
Kerr's (smaller denominators, smaller box).

THE FREE CONTROL. The (0,n) levels -- sGB switched off -- solve the same recursion from
Schwarzschild's Killing space and must reproduce KERR's at every rank: 5 at rank 2, 8 at rank 3,
14 at rank 4, all three already measured independently in §128. L^2 has to deform into Carter along
the way. That is a known-answer check on the whole triangular machinery before sGB enters at all,
and it costs nothing extra.

Repro:  .venv/bin/python scripts/_kt_double.py --rank 2 --control
"""
import os, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np
import sympy as sp
import _kt_search as K
import _kt_metrics as MM
import _kt_exact as EX
import _kt_perturb as PB
from _kt_modp32 import nullspace_modp32, matrix_from_dicts32, matrix_from32

# INT32 STORAGE, INT64 ARITHMETIC. At rank 4 the operator matrix is ~20125 columns and the int64
# elimination needs ~7.8 GB -- past what this laptop can give it. int32 storage halves that to
# ~3.9 GB; the arithmetic still promotes to int64 in chunks, so nothing overflows. The routine was
# validated vector-for-vector against nullspace_modp (scripts/_kt_modp32.py --selftest) before
# being wired in here.
#
# AND A GUARD ON THE REAL DATA, because a self-test on random matrices is not the same as being
# right on this one. Every returned vector is checked to satisfy M v = 0 (mod p) on the ACTUAL
# matrix, in row chunks so the check itself cannot blow the memory it is protecting. This catches
# a wrong answer; it does not prove completeness, which rests on the validated algorithm.
INT32_MIN_COLS = 8000


def nullspace(M, p, verify=True):
    """Nullspace over GF(p), int32 storage above INT32_MIN_COLS columns, with a residual check."""
    A = np.asarray(M)
    ncols = A.shape[1] if A.size else 0
    vecs = nullspace_modp32(A, p) if ncols >= INT32_MIN_COLS else PB.nullspace_modp(A, p)
    if verify and vecs:
        # SPLIT THE MULTIPLY, because the obvious check overflows. With M and V entries both up to
        # p ~ 2^31, a single product is ~2^62 and summing thousands of them wraps int64 silently --
        # the first version of this guard did exactly that and reported EVERY residual nonzero on a
        # correct nullspace. Splitting V into 16-bit halves keeps each term under 2^47, so k up to
        # ~65000 columns accumulates safely. Third time this specific overflow has been the bug
        # rather than the thing under test.
        V = np.array(vecs, dtype=np.int64).T % p          # (ncols, nvec)
        Vhi, Vlo = V >> 16, V & 0xFFFF
        bad = 0
        for s0 in range(0, A.shape[0], 2000):
            blk = np.asarray(A[s0:s0+2000], dtype=np.int64) % p
            res = (((blk @ Vhi) % p) * 65536 + (blk @ Vlo)) % p
            bad += int(np.count_nonzero(res))
        if bad:
            raise AssertionError(
                f"NULLSPACE GUARD FAILED: {bad} nonzero residuals in M v mod p over "
                f"{len(vecs)} vectors. The returned vectors are not in the nullspace -- the "
                f"elimination is wrong, and every dimension downstream of it is meaningless.")
    return vecs

t, x, y, ph = sp.symbols("t x y phi", real=True)
chi, zeta = sp.symbols("chi zeta")
PRIMES = (2147483647, 2147483629)
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def kerr_chi_pieces(M=sp.Integer(1), a_over_m=sp.Integer(1)):
    """g^ab for Kerr expanded in chi, as [chi^0, chi^1, chi^2] pieces in (t,x=r,y=cos th,phi).

    a = M*chi*a_over_m. The chi^0 piece is Schwarzschild, which is the background whose bracket
    becomes the reusable operator."""
    a = M*chi*a_over_m
    Sig = x**2 + a**2*y**2
    Dl = x**2 - 2*M*x + a**2
    g = sp.zeros(4, 4)
    g[0,0] = -(1 - 2*M*x/Sig)
    g[0,3] = g[3,0] = -2*M*a*x*(1-y**2)/Sig
    g[1,1] = Sig/Dl
    g[2,2] = Sig/(1-y**2)           # y = cos(theta): dtheta^2 -> dy^2/(1-y^2)
    g[3,3] = (x**2 + a**2 + 2*M*a**2*x*(1-y**2)/Sig)*(1-y**2)
    g = sp.Matrix(4,4, lambda i,j: sp.expand(sp.series(g[i,j], chi, 0, 3).removeO()))
    gi_exact = sp.Matrix(4,4, lambda i,j: sp.cancel(sp.together(g.inv()[i,j])))
    gi = sp.Matrix(4,4, lambda i,j: sp.expand(sp.series(gi_exact[i,j], chi, 0, 3).removeO()))
    out = []
    for n in range(3):
        out.append(sp.Matrix(4,4, lambda i,j: sp.cancel(sp.together(
            sp.diff(gi[i,j], chi, n).subs(chi, 0)/sp.factorial(n)))))
    return out


def sgb_ginv_pieces(GI):
    """g^ab pieces of the sGB correction at chi^0, chi^1, chi^2, in (t, x=r, y=cos th, phi).

    All three come from THIS project's own derivations: the static pair verified against the EdGB
    field equations (_kt_sgb_verify), the O(chi) frame-dragging term derived in commit 64ef0c2, and
    the five Zerilli functions derived and verified at fresh points in §129.

    The inverse is built perturbatively from Schwarzschild and truncated -- NOT by inverting the
    truncated metric, which would silently mix in orders the solution does not control."""
    f = 1 - 2/x
    Y2 = 3*y**2 - 1
    DG_TT = -(1)/(3*x**3)*(1 + 26/x + sp.Rational(66,5)/x**2 + sp.Rational(96,5)/x**3 - 80/x**4)
    DG_RR = -(1)/(f**2*x**2)*(1 + 1/x + sp.Rational(52,3)/x**2 + 2/x**3
                              + sp.Rational(16,5)/x**4 - sp.Rational(368,3)/x**5)
    W_ROT = (9*x**4 + 140*x**3 + 90*x**2 + 144*x - 400)/(15*x**7)
    H02f = -(-8820000 + 8173200*x + 15803900*x**2 - 4198950*x**3 - 4061710*x**4
             - 2275145*x**5 + 164874*x**6 + 187446*x**7 + 187446*x**8)/(110250*x**10*(x-2))
    H22f = -(149940000 - 201978000*x + 101014900*x**2 - 18766650*x**3 + 11833890*x**4
             - 7545095*x**5 - 55626*x**6 + 150696*x**7 + 187446*x**8)/(110250*x**10*(x-2))
    K2f  = -(8820000 - 6213200*x - 3416700*x**2 - 1855650*x**3 + 887110*x**4
             + 800733*x**5 + 435540*x**6 + 187446*x**7)/(110250*x**10)
    H00f =  (800 - 11264*x + 2172*x**2 + 1020*x**3 + 1214*x**4 + 156*x**5
             + 210*x**6 + 15*x**7)/(90*x**9*(x-2))
    H20f =  (8000 + 25312*x - 22664*x**2 - 724*x**3 + 640*x**4 + 1090*x**5
             - 180*x**6 + 150*x**7 - 15*x**8 + 15*x**9)/(30*x**9*(x-2)**2)
    h = sp.zeros(4,4)
    h[0,0] = DG_TT + chi**2*f*(H00f + H02f*Y2)
    h[1,1] = DG_RR + chi**2*(H20f + H22f*Y2)/f
    h[0,3] = h[3,0] = chi*W_ROT*(1-y**2)
    h[2,2] = chi**2*x**2*(K2f*Y2)/(1-y**2)      # g_thth -> g_yy: divide by (1-y^2)
    h[3,3] = chi**2*x**2*(1-y**2)*(K2f*Y2)
    # THE O(zeta) INVERSE PERTURBATION IS EXACTLY -g^-1 h g^-1 ON THE KERR BACKGROUND.
    # Since h enters at O(zeta^1) and we keep only that order, no Neumann series is needed at all:
    # (g + zeta h)^-1 = g^-1 - zeta g^-1 h g^-1 + O(zeta^2), and g^-1 for Kerr is already in hand
    # from kerr_chi_pieces. The first version built a five-term Neumann series from Schwarzschild
    # and separately inverted a symbolic 4x4 to recover the lower Kerr metric -- both unnecessary,
    # and together they ran past ten minutes.
    giK = sp.zeros(4,4)
    for n in range(3):
        giK += chi**n*GI[n]
    def trc(e):
        e = sp.expand(e)
        return sp.Add(*[u for u in sp.Add.make_args(e) if sp.degree(u, chi) <= 2])
    tmp = sp.Matrix(4,4, lambda i,j: trc(sp.expand(
        sum(giK[i,k]*h[k,l]*giK[l,j] for k in range(4) for l in range(4)))))
    gi = sp.Matrix(4,4, lambda i,j: -trc(sp.expand(tmp[i,j])))
    out = []
    for n in range(3):
        out.append(sp.Matrix(4,4, lambda i,j: sp.cancel(sp.together(
            sp.diff(gi[i,j], chi, n).subs(chi,0)/sp.factorial(n)))))
    return out


def hamiltonian(ginv):
    return sp.Rational(1,2)*sum(ginv[i,j]*K.MOM[i]*K.MOM[j]
                                for i in range(K.DIM) for j in range(K.DIM))


if __name__ == "__main__":
    def arg(fl, d=None, c=str):
        return c(sys.argv[sys.argv.index(fl)+1]) if fl in sys.argv else d
    rank = arg("--rank", 2, int)
    denpow = arg("--denpow", 2, int)
    margin = arg("--margin", 4, int)
    p = PRIMES[arg("--prime", 0, int)]
    K.set_dim((t, x, y, ph), sp.symbols("P_t P_x P_y P_phi", real=True), dep=(1,2))
    t0 = time.time()

    GI = kerr_chi_pieces()
    gi0 = GI[0]
    L, _, _ = MM.denominator(gi0)
    den = L**denpow
    gnames, prods, pnames = EX.generators(gi0, rank, den)
    bx, by = EX.reducible_box(prods, den)
    dx, dy = bx + margin, by + margin
    print(f"Schwarzschild background: L = {sp.factor(L)}", flush=True)
    print(f"  generators {gnames}; {len(prods)} reducible products at rank {rank}", flush=True)
    print(f"  box x<={dx} y<={dy}; den = L^{denpow}", flush=True)

    mons = K.monomials(rank)
    cols, F_cos = PB.coefficient_basis(mons, dx, dy, den)
    n_w = len(cols)
    print(f"  {n_w} coefficient unknowns per level", flush=True)

    H = [hamiltonian(GI[n]) for n in range(3)]

    # ---- the reusable operator: {H^(0,0), w_j} for every basis function ----
    raws0, dens0 = PB.build_columns([(H[0], F) for F in F_cos], mons, True, "op ")
    D = sp.Integer(1)
    for d_ in dens0:
        D = sp.lcm(D, d_)
    M0, dicts0 = matrix_from32(raws0, D, p, n_w, PB.clear)
    print(f"  operator matrix {M0.shape} [{time.time()-t0:.0f}s]", flush=True)
    bg = nullspace(M0, p)
    # FREE IT. M0 is never read again, but the name keeps ~3.9 GB (rank 4, int32) alive right up
    # to the point where Mfull allocates another 3.9 GB beside it -- 7.8 GB against ~7.3 GB free,
    # i.e. swap or death. The whole int32 conversion is wasted if both matrices are resident.
    _m0_gb = M0.nbytes / 2**30
    del M0
    import gc; gc.collect()
    print(f"  operator matrix released ({_m0_gb:.1f} GB); only one large matrix resident from here",
          flush=True)
    print(f"  chi^0 level: Schwarzschild Killing space = {len(bg)}", flush=True)

    if "--control" in sys.argv:
        # THE FREE CONTROL: run the (0,n) tower with sGB OFF. It must land on KERR's Killing space.
        # Expected from §128, measured independently: 5 at rank 2, 8 at rank 3, 14 at rank 4.
        EXPECT = {2: 5, 3: 8, 4: 14}
        def to_co(v):
            F = [sp.Integer(0)]*len(mons)
            for j,(mi,a_,b_) in enumerate(cols):
                if v[j]:
                    F[mi] += int(v[j])*x**a_*y**b_
            return [sp.cancel(f/den) for f in F]
        # CHAINS, not just leading terms. The source at level n is
        #     sum_{j>=1} {H^(0,j), F^(0,n-j)}
        # so level 2 needs F^(0,1), the level-1 SOLUTION. The first version of this loop used
        # F^(0,0) in every term -- it never fed level 1 into level 2 -- and still returned 5 of 5,
        # which happens to be Kerr's answer. A control that passes on broken code is worse than one
        # that fails, so each surviving direction now carries its whole chain.
        #
        # Coefficients stay mod p throughout. Brackets are computed symbolically over Q on mod-p
        # REPRESENTATIVES, which is consistent because the bracket is Q-linear and reduction mod p
        # is a ring homomorphism -- but the moment a result is fed to sp.Rational or sp.solve as if
        # it were exact, it is garbage. That error has now appeared three times in this file alone.
        def vec_to_co(v):
            F = [sp.Integer(0)]*len(mons)
            for j,(mi,a_,b_) in enumerate(cols):
                c_ = int(v[j]) % p
                if c_:
                    F[mi] += c_*x**a_*y**b_
            return [sp.cancel(f/den) for f in F]

        # RESUME. The chi-tower is independent of the sGB question and cost 2597s at rank 2; the
        # zeta side is where iteration happens, so recomputing it per attempt is pure waste. Three
        # expensive computations were lost to missing checkpoints earlier in this session, and the
        # first version of this file wrote the checkpoint without ever reading it back.
        import pathlib, pickle
        ckf = pathlib.Path(f"data/kt_double_chains_r{rank}_d{denpow}_b{dx}x{dy}.pkl")
        chains = None
        if ckf.exists():
            try:
                chains = [[[sp.sympify(e) for e in lvl] for lvl in ch]
                          for ch in pickle.loads(ckf.read_bytes())]
                print(f"  RESUMED chi-tower from {ckf.name}: {len(chains)} chains", flush=True)
            except Exception as exc:
                print(f"  checkpoint unreadable ({exc}); recomputing", flush=True)
                chains = None
        if chains is None:
            chains = [[to_co(v)] for v in bg]  # chains[k][n] = F^(0,n) of direction k
        dim = len(chains)
        _resumed = len(chains[0]) > 1 if chains else False
        for n in ([] if _resumed else (1, 2)):
            srcs = []
            for ch in chains:
                acc = sp.Integer(0)
                for j in range(1, n+1):
                    if n-j < len(ch):
                        tog, _ = PB.bracket_raw_coeffs(ch[n-j], H[j], mons)
                        acc += tog
                srcs.append(acc)
            D2 = D
            for e in srcs:
                D2 = sp.lcm(D2, sp.denom(sp.together(e)))
            if sp.simplify(D2 - D) == 0:
                dS = [PB.clear(e, D, p) for e in srcs]
                Mfull = matrix_from_dicts32(dicts0 + dS, n_w + dim, p)
            else:
                Mfull, _ = matrix_from32(raws0 + srcs, D2, p, n_w + dim, PB.clear)
            ns = nullspace(Mfull, p)
            # Keep only vectors with a nonzero c-block; their F-blocks ARE the level-n solutions
            # for the chain combination their c-block names. Vectors with c = 0 are homogeneous
            # additions and carry no information about survival.
            keep = []
            cb_rows = []
            for v in ns:
                cb = [int(z) % p for z in v[n_w:]]
                if any(cb):
                    keep.append(v); cb_rows.append(cb)
            surv = EX.rank_modp(cb_rows, dim, p) if cb_rows else 0
            print(f"  chi^{n} level: {surv} of {dim} extend  [{time.time()-t0:.0f}s]", flush=True)
            # rebuild chains: each kept vector defines a new chain = its c-combination of the old
            # chains, extended by its own F-block.
            newch = []
            for v, cb in zip(keep, cb_rows):
                comb = []
                for lvl in range(len(chains[0])):
                    acc = [sp.Integer(0)]*len(mons)
                    for k2, ck in enumerate(cb):
                        if ck:
                            for mi in range(len(mons)):
                                acc[mi] += ck*chains[k2][lvl][mi]
                    comb.append([sp.cancel(a_) for a_ in acc])
                comb.append(vec_to_co(v))
                newch.append(comb)
            chains = newch
            dim = surv
            if dim == 0:
                break

        import pathlib, pickle
        ckf = pathlib.Path(f"data/kt_double_chains_r{rank}_d{denpow}_b{dx}x{dy}.pkl")
        ckf.write_bytes(pickle.dumps([[[sp.srepr(e) for e in lvl] for lvl in ch]
                                      for ch in chains]))
        print(f"  chi-tower chains CHECKPOINTED to {ckf.name} "
              f"({len(chains)} chains) [{time.time()-t0:.0f}s]", flush=True)

        want = EXPECT.get(rank)
        print(f"\n  Kerr Killing space at rank {rank}: got {dim}, expect {want}", flush=True)
        if want is not None and dim != want:
            sys.exit("  CONTROL FAILED: the chi-tower does not reproduce Kerr's Killing space, so "
                     "the triangular machinery is wrong and no sGB result from it would mean "
                     "anything.")
        print("  count check passed, but a COUNT IS NOT ENOUGH HERE.", flush=True)
        print("  Schwarzschild and Kerr have the SAME dimension at every rank (5, 8, 14) because",
              flush=True)
        print("  Lsq maps one-to-one onto Carter -- so 'the count is preserved' would also pass if",
              flush=True)
        print("  the tower did nothing. Identifying the direction is the real test.\n", flush=True)

        # IDENTIFY, DO NOT COUNT. Carter reduces to Lsq at chi^0 and its spin dependence enters
        # only through a^2 = m^2 chi^2, so for the Lsq direction the tower must give
        #     F^(0,1) = 0                         (no O(chi) piece at all)
        #     F^(0,2) = y^2 m^2 (mu^2 - p_t^2)    modulo Schwarzschild Killing tensors
        # A tower that did nothing returns zero for both, and fails this.
        Lsq_expr = (1-y**2)*K.MOM[2]**2 + K.MOM[3]**2/(1-y**2)
        mu2 = -2*hamiltonian(gi0)
        predicted = y**2*(mu2 - K.MOM[0]**2)          # m = 1 in these coordinates
        print(f"  Carter's O(chi^2) piece should be  y^2 (mu^2 - p_t^2)", flush=True)
        print(f"    = {sp.simplify(predicted)}", flush=True)
        chk = sp.cancel(sp.together(sp.expand(PB.poisson_ok if False else 0)))
        # Verify the PREDICTION is itself right: Lsq + chi^2 * predicted must Poisson-commute with
        # the Kerr Hamiltonian to O(chi^2). If this fails the prediction is wrong, not the tower.
        import _kt_reducible as R
        Hk = sum((chi**n)*sum(GI[n][i,j]*R.MO[i]*R.MO[j] for i in range(4) for j in range(4))
                 for n in range(3))
        Fk = Lsq_expr + chi**2*predicted
        br = sp.expand(R.poisson(Hk, Fk))
        br2 = sp.cancel(sp.together(sp.expand(sp.diff(br, chi, 2).subs(chi, 0)/2)))
        br1 = sp.cancel(sp.together(sp.expand(sp.diff(br, chi).subs(chi, 0))))
        br0 = sp.cancel(sp.together(sp.expand(br.subs(chi, 0))))
        print(f"  prediction self-check: {{H,F}} at chi^0 = {br0 == 0}, chi^1 = {br1 == 0}, "
              f"chi^2 = {br2 == 0}", flush=True)
        if not (br0 == 0 and br1 == 0 and br2 == 0):
            sys.exit("  THE PREDICTION IS WRONG, not the tower -- Lsq + chi^2 y^2(mu^2-p_t^2) does "
                     "not commute with the Kerr Hamiltonian to O(chi^2). Fix the prediction first.")
        # IDENTIFY THE DIRECTION. Find the tower vector whose c-block picks out Lsq, read off its
        # F^(0,2), and compare against the verified prediction MODULO the Schwarzschild Killing
        # space -- each level is determined only up to adding a background Killing tensor, so
        # equality on the nose is the wrong test and would fail a correct answer.
        # IS THE COUNT VACUOUS? Settle it by asking whether Lsq survives UNCHANGED, rather than
        # by extracting the tower's F^(0,2) and comparing -- three attempts at that extraction
        # failed on mod-p/rational mixing, and this argument is both cheaper and stronger.
        Hk = sum((chi**n)*sum(GI[n][i,j]*R.MO[i]*R.MO[j]
                              for i in range(4) for j in range(4)) for n in range(3))
        brL = sp.expand(R.poisson(Hk, Lsq_expr))
        L2 = sp.cancel(sp.together(sp.expand(sp.diff(brL, chi, 2).subs(chi, 0)/2)))
        print(f"\n  {{H_Kerr, Lsq}} at chi^2 is {'ZERO' if L2 == 0 else 'NONZERO'}", flush=True)
        if L2 == 0:
            print("  THE COUNT IS VACUOUS: Lsq survives unchanged, so 5-of-5 would also hold for "
                  "a tower that did nothing. This control proves nothing.", flush=True)
        else:
            nfloor = sum(1 for a_ in range(rank+1) for b_ in range(rank+1)
                         for c_ in range(rank//2+1) if a_+b_+2*c_ == rank)
            print(f"  THE COUNT IS DECISIVE: Lsq alone does NOT extend to O(chi^2), so a tower "
                  f"doing nothing would have reported {nfloor} of {dim} -- only the directions "
                  f"built from p_t, p_phi and H, which survive trivially. Reporting {dim} means "
                  f"it found a nonzero F^(0,2), and the verified prediction above identifies that "
                  f"deformation as Carter's.", flush=True)
            print("\n  CONTROL PASSED, non-vacuously: the chi-tower deforms Lsq into Carter.",
                  flush=True)

    if "--sgb" in sys.argv:
        # THE zeta TOWER. With the chi-chains in hand (each a Kerr Killing tensor, F^(0,0..2)),
        # ask which of them survive the sGB correction:
        #   {H^(0,0), F^(1,n)} = -[ sum_{j>=1} {H^(0,j), F^(1,n-j)}
        #                           + sum_{j>=0} {H^(1,j), F^(0,n-j)} ]
        # Same reusable operator, same chain bookkeeping, same mod-p discipline.
        SG = sgb_ginv_pieces(GI)
        badrep = []
        for n_ in range(3):
            b = PB.check_perturbation_representable(SG[n_], dx, dy, den)
            if b:
                badrep.append((n_, b))
        if badrep:
            sys.exit(f"\n  sGB PERTURBATION NOT REPRESENTABLE at {badrep}. H^(1,j) lies outside "
                     f"the ansatz, so directions will appear to die for reasons that have nothing "
                     f"to do with the geometry. Measured requirement: denpow 6 with numerator "
                     f"degrees to (16,16). Raise --denpow / --box and rerun.")
        HS = [hamiltonian(M) for M in SG]
        print(f"\n  sGB Hamiltonian pieces built and REPRESENTABLE [{time.time()-t0:.0f}s]",
              flush=True)
        # THE FLOOR IS COMBINATORIAL, and needs no metric at all. It is the number of products of
        # p_t, p_phi and H of total degree = rank -- manifestly independent, since they carry
        # distinct momentum structures. Two earlier attempts to compute it from a metric both
        # failed: gi0 (Schwarzschild) wrongly counted Lsq, which sGB does not conserve; and Kerr's
        # generators do not divide Schwarzschild's L^6 ansatz denominator. Counting is exact and
        # matches every floor measured in §128 (rank 2 -> 4, rank 3 -> 6, rank 4 -> 9).
        nred = sum(1 for a_ in range(rank+1) for b_ in range(rank+1)
                   for c_ in range(rank//2+1) if a_ + b_ + 2*c_ == rank)
        print(f"  reducible floor (products of p_t, p_phi, H at rank {rank}): {nred}", flush=True)

        zchains = [[] for _ in chains]          # zchains[k][n] = F^(1,n) of direction k
        zdim = len(chains)
        alive = list(range(len(chains)))
        for n in (0, 1, 2):
            srcs = []
            for k, ch in enumerate(chains):
                acc = sp.Integer(0)
                for j in range(1, n+1):                       # {H^(0,j), F^(1,n-j)}
                    if n-j < len(zchains[k]):
                        tg, _ = PB.bracket_raw_coeffs(zchains[k][n-j], H[j], mons)
                        acc += tg
                for j in range(0, n+1):                       # {H^(1,j), F^(0,n-j)}
                    if n-j < len(ch):
                        tg, _ = PB.bracket_raw_coeffs(ch[n-j], HS[j], mons)
                        acc += tg
                srcs.append(acc)
            D2 = D
            for e in srcs:
                D2 = sp.lcm(D2, sp.denom(sp.together(e)))
            if sp.simplify(D2 - D) == 0:
                dS = [PB.clear(e, D, p) for e in srcs]
                Mfull = matrix_from_dicts32(dicts0 + dS, n_w + zdim, p)
            else:
                Mfull, _ = matrix_from32(raws0 + srcs, D2, p, n_w + zdim, PB.clear)
            ns = nullspace(Mfull, p)
            keep, cbs = [], []
            for v in ns:
                cb = [int(z) % p for z in v[n_w:]]
                if any(cb):
                    keep.append(v); cbs.append(cb)
            surv = EX.rank_modp(cbs, zdim, p) if cbs else 0
            print(f"  zeta chi^{n} level: {surv} of {zdim} survive  [{time.time()-t0:.0f}s]",
                  flush=True)
            newch, newz = [], []
            for v, cb in zip(keep, cbs):
                comb = []
                for lvl in range(len(chains[0])):
                    acc = [sp.Integer(0)]*len(mons)
                    for k2, ck in enumerate(cb):
                        if ck:
                            for mi in range(len(mons)):
                                acc[mi] += ck*chains[k2][lvl][mi]
                    comb.append([sp.cancel(a_) for a_ in acc])
                newch.append(comb)
                zc = []
                for lvl in range(len(zchains[0]) if zchains and zchains[0] else 0):
                    acc = [sp.Integer(0)]*len(mons)
                    for k2, ck in enumerate(cb):
                        if ck and lvl < len(zchains[k2]):
                            for mi in range(len(mons)):
                                acc[mi] += ck*zchains[k2][lvl][mi]
                    zc.append([sp.cancel(a_) for a_ in acc])
                zc.append(vec_to_co(v))
                newz.append(zc)
            chains, zchains = newch, newz
            zdim = surv
            zck = pathlib.Path(f"data/kt_double_z_r{rank}_d{denpow}_n{n}.pkl")
            zck.write_bytes(pickle.dumps({
                "chains": [[[sp.srepr(e) for e in lvl] for lvl in ch] for ch in chains],
                "zchains": [[[sp.srepr(e) for e in lvl] for lvl in ch] for ch in zchains],
                "zdim": zdim}))
            print(f"    level {n} checkpointed ({zck.name})", flush=True)
            if zdim == 0:
                break

        print(f"\n  SURVIVING at O(zeta chi^2), rank {rank}: {zdim}", flush=True)
        print(f"  reducible floor: {nred}", flush=True)
        if zdim == nred:
            if rank == 2:
                print("  => only the reducible floor survives. Carter does NOT extend, which is "
                      "what three independent published arguments require (Petrov type I in "
                      "Ayzenberg-Yunes; Owen-Yunes-Witek's Killing search; Deich et al.'s chaotic "
                      "Poincare sections).", flush=True)
            else:
                print(f"  => only the reducible floor survives: no irreducible rank-{rank} Killing "
                      f"tensor at O(zeta chi^2) that is analytic in zeta with a Kerr root.",
                      flush=True)
                print("     NO PUBLISHED ARGUMENT REACHES THIS RANK -- there is nothing here to "
                      "agree with. Petrov type I forbids a rank-2 tensor and says nothing above it; "
                      "Owen-Yunes-Witek searched rank 2. Do not report this as corroborated.",
                      flush=True)
                print(f"     EXPECTED, NOT INDEPENDENT: the rank-{rank} Kerr Killing space above "
                      f"the floor is spanned by Carter times momenta, so Carter's death at rank 2 "
                      f"made this the strongly favoured outcome. It is not a corollary -- for "
                      f"F0 = Q p_t the O(zeta) source is {{H1,Q}} p_t and its solution G1 need not "
                      f"factor as F1 p_t, so the obstruction sits in a larger space than rank 2's "
                      f"and the extra factor could have killed it. It did not.", flush=True)
        elif zdim > nred:
            if rank == 2:
                print(f"  => {zdim - nred} direction(s) ABOVE the reducible floor survive. At rank "
                      f"2 this CONTRADICTS three published arguments, so the instrument is the "
                      f"first suspect, not the physics (D41).", flush=True)
            else:
                print(f"  => {zdim - nred} direction(s) ABOVE the reducible floor survive. No "
                      f"published argument reaches rank {rank}, so nothing is contradicted -- but "
                      f"nothing corroborates it either, and a positive result is never "
                      f"self-certifying (a sampled count is an UPPER bound). Identify the "
                      f"direction and verify {{H,F}}=0 on it before this is called anything.",
                      flush=True)
        else:
            print(f"  => FEWER than the reducible floor survive, which is impossible: products of "
                  f"p_t, p_phi and H are conserved exactly. This condemns the run.", flush=True)
