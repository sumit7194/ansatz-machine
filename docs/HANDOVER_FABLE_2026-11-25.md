# Handover: Fable thinking session, 2026-11-25 (c2, the analytic route near k = 0)

**[model: Fable 5.2] Session ansatz-machine-personal (Sumit's personal account). Branch
`fable/2026-11-25-c2-analytic`, worktree `../conjecture_machine-fable`. Never merged to main. Everything here is
UNVERIFIED until the office ansatz-machine checks it.**

## What was asked (the Bridge, for Sumit)
Route (ii) of the Maciejewski reply: verify the formula for the k² coefficient c2 of F = tr[M1, M0] − 2, try to
evaluate it from Kerr's explicit solutions, and show c2 ≠ 0. If that fails, plan route (i).

## What exists
| file | what |
|---|---|
| `data/nve/C2_ANALYTIC.md` | the derivation, the numbers, the finding at spin ≈ 0.908, what a certificate needs, the plan for (i), and the check list for the office session |
| `scripts/_nve_c2_analytic.py` | the small check: numpy, double precision, about 0.2 s per spin, no shared code with the monodromy engines |

## Where it stands
- **Done:** the formula is verified and reduced to c2 = sinh²(κω)·I₊·I₋/κ². Numerically c2 ≠ 0 at spins 3/10, 3/5,
  4/5, 9/10 (E = 4/5). At spin 3/5 it matches the stored 50-digit data to 12 digits.
- **Found:** c2 = 0 at spin a\* ≈ 0.9080, which explains the extra zero seen at spin 9/10.
- **Not done:**
  - no interval certificate of I± ≠ 0 and Re(κω) ≠ 0 (recipe in §6 of the note; it is small);
  - no engine samples at small k for spins 3/10, 4/5, 9/10 (only the internal two-route agreement there);
  - c3, and the behaviour exactly at a\*;
  - nothing was added to the claim, the MRS section, RESULTS or the journal. Those live on main and are the office
    session's to edit.

## Runs made (all small, `nice -n 12`, one core)
- `scripts/_nve_c2_analytic.py` at about 20 spins, about 0.2 s each.
- One first version of the script used nested 30-digit quadrature and was too slow. It was stopped after about
  5 minutes and replaced. It wrote no files.
- Read-only use of stored outputs: `gapb.jsonl`, `lower_comm.jsonl`, `spin_run_*.json`, `spin_locateA_9_10.out`.
- No running job, script, guard or output file of the office fleet was touched. The main checkout was not
  modified; its `.venv` interpreter was used to run the script.

## Paused, not to be resumed without a new ask
The Nov-18 edge-link ("window vs saddle") work.
