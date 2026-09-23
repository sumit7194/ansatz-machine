# Does anything carry an irreducible Killing tensor of rank ≥ 5?

## The setup

A **Killing tensor** of rank *r* on a spacetime is exactly a conserved quantity polynomial of
degree *r* in the momenta:

    F  =  K^{a₁…a_r} p_{a₁} … p_{a_r}        with        {H, F} = 0

Rank 1 is a Killing vector — an ordinary symmetry. **Rank 2 is where it gets interesting:** Kerr
carries one, the Carter constant, discovered in 1968 and not predicted by anything. It is the sole
reason geodesics around a rotating black hole separate, and almost no other spacetime has anything
like it.

**Irreducible** means the conserved quantity is not just a polynomial built from ones you already
had. Products and sums of Killing vectors always give you higher-rank tensors for free; those are
*reducible* and carry no new information.

## The problem

> **Rank 3 and rank 4 irreducible Killing tensors exist — constructed, not found.**
> *[EXP-001]* **Above rank 4 is NOT unexplored without field equations:** Galajinsky 2012
> (PRD 85, 085002) writes out irreducible Killing tensors of every rank 3 ≤ r ≤ n on an
> (n+2)-dimensional Lorentzian metric, rank 5 explicitly (needs D ≥ 7). **Ricci-flat examples exist
> only in ultrahyperbolic signature (2,q), ranks 3–4, D = 4–6** (Cariglia–Galajinsky 2015). **No
> Lorentzian Ricci-flat or Einstein spacetime with an irreducible Killing tensor of rank ≥ 3 is
> known in any dimension** — stated open by CG 2015 and Fordy–Galajinsky 2019.
>
> **Construct a metric carrying an irreducible Killing tensor of rank ≥ 5, or establish that none
> can exist in a stated class.**

Either outcome is a result. **The construction is the harder and more interesting one.**
*[EXP-001]* It has been attempted and achieved without field equations (Galajinsky 2012); the
unattempted-and-open version is **vacuum, Lorentzian, rank ≥ 3** — the frontier there is rank 3.

## What makes this checkable

The deliverable is **an object**, and an exact symbolic checker decides it in three steps with no
numerics anywhere in the verification path:

    1.  does the metric satisfy its field equations?          exact, yes/no
    2.  is the claimed F actually conserved, {H,F} = 0?       exact, yes/no
    3.  is it IRREDUCIBLE, or a product of lower-rank ones?   exact, yes/no

**You cannot argue past any of these.** A rank-5 tensor either satisfies the Killing equation or it
does not, and SymPy decides it exactly. *[EXP-001: not "in seconds" — the sibling's 4D rank-4
den¹ run took 66 min; Kruglikov–Steneker's quartic prolongation matrix was 495 880 × 371 910.
Budget hours for rank 5.]* This is the whole reason this problem was chosen: a wrong
answer is detectable, which is not true of most open problems.

A validated instrument for exactly these three steps already exists in `../conjecture_machine` —
**read-only**, see `SISTERS.md`. It has been shown to work in **both** directions: it recovers the
Carter constant on Kerr (returns *something* where something is known to exist) and returns zero on
a deformed vacuum across ranks 1–6 *[EXP-001: at denominator power 1; den² only at ZV rank 4; its
rank-3/4 positive controls are CG's ultrahyperbolic metrics]*. **A checker that has only ever said "no" has not been shown able
to say "yes"**, and that repo's §127 is the model for how to establish it.

---

## Before anything: M1, and it is a real gate

**Everything on this page was written from an assistant's recollection and is UNVERIFIED.** The
same was true of the last workspace built this way, and the prior-art sweep found **two** claims in
it wrong — one of which invalidated a whole line of evidence. Expect the same here.

**Verify, before deriving anything:**

- **Whether rank 3 and rank 4 irreducible Killing tensors actually exist**, in what dimension, on
  what class of metrics, and by whom. *[EXP-001 — settled.]* Lorentzian, no field equations: rank 3
  and 4 in 4D (GHKW 2011, PLB 700, 68; Gibbons–Rugina 2011, JMP 52, 122901), ranks 3..n in
  (n+2)D (Galajinsky 2012). Ricci-flat: CG 2015 (PLB 744, 320), rank 3 in D = 4, 5, 6 and rank 4
  in D = 5, 6, **all signature (2,q)** — the sibling's control is their eq. 26, 5D, (2,3). *The
  4D question is open at rank 3 — for Lorentzian vacuum, in every dimension.*
- **Whether rank ≥ 5 is genuinely unexplored**, or whether a non-existence theorem already covers
  it. *[EXP-001 — settled.]* Explored and achieved without field equations (Galajinsky 2012).
  No general non-existence theorem. Specific metrics only: ZV ≤ 11, Tomimatsu–Sato ≤ 7, C-metric
  ≤ 9 (Vollmer, J. Geom. Phys. 115 (2017) 28 — three metrics, not one); ZV δ=2 < 7
  (Kruglikov–Matveev 2012); slow-rotation dCS ≤ 6 (Owen–Yunes–Witek 2021); Wils ≤ 6
  (Kruglikov–Steneker 2022). Generic metrics have no polynomial integral of any degree
  (Kruglikov–Matveev 2016).
- **Whether "Ricci-flat" is the right class to ask in.** *[EXP-001]* Yes — it is the only class
  where the question is open, and it is open from **rank 3** up in Lorentzian signature. Every
  Lorentzian construction lives off-shell; every Ricci-flat one lives in (2,q).
- **What the obstruction is.** *[EXP-001]* **No rank bound exists in 4D.** The Killing equation is
  of finite type at every rank (dimension ≤ (1/n)·C(n+r−1,r)·C(n+r,r+1): 10, 50, 175, 490, 1176,
  2520 in 4D for r = 1..6, attained on constant curvature where everything is reducible), but
  4D Lorentzian metrics with irreducible Killing tensors of *every* rank exist once field
  equations are dropped (lift of Kiyohara 2001 / Valent 2017). The only obstruction on the table
  is CG's: the Eisenhart lift is vacuum iff the base potential is harmonic, and no harmonic
  potential with a cubic-or-higher integral is in Hietarinta's list.

**Report the sweep before building. If it kills the target, say so and stop.**

---

## Verification protocol — frozen before any result

    TIER 1  EXACT    The three checks above, symbolically, over a stated field. Both primes
                     if working mod p. Nothing here is numerical and nothing should be.

    TIER 2  CONTROL  Before trusting a null from any search: show the search space COULD have
                     contained the answer. Run the known rank-3/rank-4 example through your own
                     machinery and confirm it is found. A null from an unvalidated search is
                     worth nothing.

    TIER 3  INDEPENDENCE  If you construct something, verify it by a route that shares no code
                     with the route that produced it. A tensor found and checked by the same
                     script has been checked by its own author.

**Grade every claim `verified` / `partially verified` / `unverified`.**

---

## Outcomes, ranked, all reportable

    A  A metric with an irreducible Killing tensor of rank >= 5, verified by all three checks.
    B  A rank-5 construction in a broader class than vacuum 4D -- higher dimension, or with
       matter -- with the class stated.
    C  A proof that no irreducible Killing tensor of rank >= 5 exists in a stated class, with
       the obstruction named.
    D  A structural reason the rank tower terminates, even short of a proof -- e.g. an argument
       that the space of candidates collapses above some rank.
    E  A sharpened map of what IS known: the actual dimensions, classes and ranks of every
       existing example, correcting this page where it is wrong.
    F  It is already done. Report the citation and stop. THIS IS A RESULT.

**E is not a consolation prize.** If the honest state of the field is that rank 3 exists only in
5D and 4D is open at rank 3, then establishing that is worth more than a failed rank-5 attempt.

---

## What would make the work worthless

- A tensor proposed without running it through an exact check.
- A null from a search space never shown to contain the answer. *"No solution" from a space that
  could not have held one is a fact about your parametrisation, not about the problem.*
- A claim about what is known, written from memory rather than checked against a source.
- Reporting "I could not construct one" as "none exists."
- Modifying anything in a sibling repository. They are read-only, without exception.

---

## Corrections log

**[EXP-001, 2026-09-04]** Seven claims above were checked against sources and five were amended
in place (marked `[EXP-001]`): "above rank 4 unexplored" (false without field equations); the CG
dimension/signature (4–6D, all ultrahyperbolic); "SymPy in seconds"; the instrument's den¹ scope;
Vollmer's scope (three metrics). Two survived unchanged: rank 3/4 exist by construction; the
outcome ladder. The sharpened target is in `TODO.md` (RESUME POINT) and `report.md` EXP-001.
