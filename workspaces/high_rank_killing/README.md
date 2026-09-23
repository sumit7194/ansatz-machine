# high_rank_killing

**Construct a metric carrying an irreducible Killing tensor of rank ≥ 5 — or establish that none
can exist in a stated class.**

> ## OUTCOME (2026-09-05) — the target moved, and the moved target was hit
>
> **EXP-001 refuted the premise.** Rank ≥ 5 is *not* unexplored: Galajinsky 2012 writes out
> irreducible Killing tensors of every rank 3 ≤ r ≤ n on an (n+2)-D Lorentzian metric **without
> field equations**. And every *Ricci-flat* example in the literature is **ultrahyperbolic (2,q)**.
> **The real open frontier is rank 3, in Lorentzian vacuum** — stated open by Cariglia–Galajinsky
> 2015 and by Fordy–Galajinsky 2019, who call it *"an empirical barrier of rank-2 that seems rather
> puzzling."*
>
> **EXP-002/003 constructed it.** A **4D Lorentzian vacuum pp-wave** with a polynomially irreducible
> **rank-3** Killing tensor, plus a **5D (1,4)** companion. Verified three ways: exact Ricci-flatness
> with the coupling symbolic, `{H,F} = 0` exactly plus an independent geodesic route, and a closed
> dimension squeeze (**2/6/11** in 4D, **3/9/20** in 5D — lower bound meets upper bound).
>
> **Honest scope, which travels with it:** `F = −4{Q1,Q2}` is **functionally dependent**. The defence
> is computed rather than asserted — **CG's own published (2,2) cubic is also a bracket**, so the
> objection applies equally to the examples the literature already accepts, and the only new content
> is the signature.
>
> **Start at [WRITEUP.md](WRITEUP.md).** Imported for independent verification by
> `../conjecture_machine` under `external/high_rank_killing/`.
>
> **Rank ≥ 5 is parked**: EXP-001 found no route, and searching without one was judged not worth the
> cost.

Rank 2 is the Carter constant, the hidden symmetry that makes Kerr geodesics separable. Rank 3 and
rank 4 examples are believed to exist, constructed rather than found. **Above rank 4 the landscape
appears unexplored.**

## Read in this order

| file | what it is |
|---|---|
| **[TASK.md](TASK.md)** | the problem, the M1 gate, the frozen verification protocol, six reportable outcomes |
| **[CLAUDE.md](CLAUDE.md)** | the operating contract — loads every session, short on purpose |
| **[SISTERS.md](SISTERS.md)** | the read-only sibling repos; `../conjecture_machine` holds the instrument |
| **[TODO.md](TODO.md)** | open questions and unverified claims |
| **[report.md](report.md)** | one entry per experiment, fields enforced |

## Why this problem

**The deliverable is an object, not an argument** — and an exact symbolic checker decides it:

```
1. does the metric satisfy its field equations?        exact, yes/no
2. is the claimed F conserved, {H,F} = 0?              exact, yes/no
3. is it irreducible, or built from lower-rank ones?   exact, yes/no
```

No numerics anywhere in the verification path. A wrong answer is detectable, which is not true of
most open problems.

## The instrument already exists

`../conjecture_machine` has a prover validated in **both** directions — it recovers the Carter
constant on Kerr and returns zero on a deformed vacuum across ranks 1–6. Read-only. `SISTERS.md`
says which file does what.

## Ground rules

- **Prior art first.** Every claim in `TASK.md` is written from recollection and unverified. The
  last workspace built this way had two of its claims overturned by the sweep.
- **A null over a search space never shown to contain the answer is not a result.**
- **"I could not construct one" is not "none exists."** Say which you have.
- **The siblings are read-only.** Cite them by repo and file in the same sentence as the number.
