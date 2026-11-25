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

## Part B: a prototype and a plan, not a certificate
| file | what |
|---|---|
| `data/nve/EPS_EFFECTIVE.md`, Part B | the evaluator, the k-ball measurement, the one-segment demonstration, the plan, every remaining limit |
| `scripts/_nve_route1_proto.py` | validated evaluator of M0, M1 at a point or ball of k (python-flint/Arb); `segment` mode for the interpolation demonstration |
| `scripts/_nve_route1_floats.py` | reference values and loop vertices from the 50-digit engine (main venv) |
| `data/nve/eps/route1_*.out/.json/.jsonl` | outputs; `route1_segment.jsonl` is the per-evaluation checkpoint |

- **Interpreter for the prototype (record for reproducibility):**
  `/Users/sumit/Github/quantum/sims/.venv/bin/python -I`, Python 3.13.12, python-flint 0.9.0, mpmath 1.3.0. It is
  Quantum's pinned environment, used read-only on the Bridge's instruction; nothing was installed anywhere.
- **Built and measured:** the point evaluator (enclosures contain the engine's values at k = 1, 1.05, 1.1; 30 s each;
  radius 1e−9 on F); k-balls fail (radius of F = 2e7 × radius of k); the interpolation layer on k ∈ [1, 1.1].
- **Where it stopped:**
  - the bound M on a complex k-neighbourhood (B4 steps 1–2) is designed, not built, so nothing is certified over
    any k-interval;
  - the step-size fix (Q on boundary balls plus a winding check) is not built: the walk takes about 10× more steps
    than it needs;
  - spin 3/5 only; |k| ≲ 3 only; region B not designed.

## Runs made (one process at a time, nice 12, with the Bridge's OK while the fleet held all ten cores)
- `_nve_eps_certify.py`: about 10 development runs at spin 3/5 (20–90 s each), then the ten runs of
  `data/nve/eps/run_all.py`.
- `_nve_eps_engine_check.py`: five runs (31–118 s each, peak 127 MB) via `data/nve/eps/run_engine.py`.
- `_nve_route1_floats.py` (main venv): one run, three k, 25–27 s each, peak under 130 MB.
- `_nve_route1_proto.py` (Quantum's interpreter, read-only): about 12 point or ball evaluations at 26–30 s each, and
  the 16 evaluations of the segment run (446 s in all, checkpointed per evaluation), peak 29 MB.
- Nothing of the fleet's was touched. The main checkout was not modified; its `.venv` interpreter ran the scripts.

## What the office session should check (Part B)
1. The evaluator's tail bounds: the Laurent tail (`laurent`, `c0_at`) and the majorant in `step`.
2. That a refused disc really is the only way a zero of G1 or G2 could matter (the disc box covers the Taylor disc).
3. The interpolation theorem at source (ATAP Thm 8.2; quoted from memory), and the extreme-point convention.
4. Whether to pin python-flint in this repo's own environment.
5. Whether the plan's shift from an argument principle to enclosures on the real interval is acceptable.

## What the office session should check (Part A)
1. The derivation in `EPS_EFFECTIVE.md` §2–§3, in particular: F = tr N² − tr(M1NM1⁻¹N); the closed form
   P = P_K(1 + γs) and Δq = (3/8)Lλ + (3/16)λ²; the moduli bounds in `box_bounds`; the entry-weighted conjugation bound
   in `assemble`.
2. The majorant tables (`hmaj`, `phibar`, the Riemann sums and tails) and the binomial bound.
3. The branch tracking of √(ND) and the interval Euler for U on the lasso.
4. That keeping the k = 0 lasso fixed is acceptable wording for the claim.
5. Rerun the four spins and the controls; they are deterministic.
