# Handover: Fable thinking session, 2026-11-25/26 (an explicit ε for Statement A; route (i) first step)

**[model: Fable 5.2] Session ansatz-machine-personal (Sumit's personal account). Branch `fable/2026-11-25-eps`,
worktree `../conjecture_machine-fable`, cut from main at d9fd9e0. Never merged to main. Everything here is UNVERIFIED
until the office ansatz-machine checks it.** Brief: `docs/BRIEF_FABLE_EPS_2026-11-25.md` v2.1.

## Part A: done
| file | what |
|---|---|
| `data/nve/EPS_EFFECTIVE.md` | the derivation, what r certifies, results, controls, what limits r |
| `scripts/_nve_eps_certify.py` | the certifier (`mpmath.iv`; about 90 s per spin under load; peak 32 MB) |
| `scripts/_nve_eps_engine_check.py` | the engine-consistency control (50-digit engine at k = r and k = ir) |
| `data/nve/eps/` | every output (`eps_<spin>.out/.json`, `_wide`, the two controls, `engine_check.out`) and the two drivers |

- **Result:** ε_a = 2.80e−3, 1.93e−3, 8.40e−4, 1.06e−4 at spins 3/10, 3/5, 4/5, 9/10 (registered loops).
- **Controls:** spin 227/250 gives r = 5.4e−8; the must-refuse run prints "NO r" with its reason; the engine is
  consistent at all five spins.
- **Not certified:** the hand derivation; that the lasso polygon is a simple closed curve around exactly r₊, p₊
  (winding numbers and the U-increment are checked); everything upstream.

## Part B
See the end of `data/nve/EPS_EFFECTIVE.md`, and the "where it stopped" lines below (updated at each commit).

## Runs made (one process at a time, nice 12, with the Bridge's OK while the fleet held all ten cores)
- `_nve_eps_certify.py`: about 10 development runs at spin 3/5 (20–90 s each), then the ten runs of
  `data/nve/eps/run_all.py`.
- `_nve_eps_engine_check.py`: five runs (31–118 s each, peak 127 MB) via `data/nve/eps/run_engine.py`.
- Nothing of the fleet's was touched. The main checkout was not modified; its `.venv` interpreter ran the scripts.

## What the office session should check (Part A)
1. The derivation in `EPS_EFFECTIVE.md` §2–§3, in particular: F = tr N² − tr(M1NM1⁻¹N); the closed form
   P = P_K(1 + γs) and Δq = (3/8)Lλ + (3/16)λ²; the moduli bounds in `box_bounds`; the entry-weighted conjugation bound
   in `assemble`.
2. The majorant tables (`hmaj`, `phibar`, the Riemann sums and tails) and the binomial bound.
3. The branch tracking of √(ND) and the interval Euler for U on the lasso.
4. That keeping the k = 0 lasso fixed is acceptable wording for the claim.
5. Rerun the four spins and the controls; they are deterministic.
