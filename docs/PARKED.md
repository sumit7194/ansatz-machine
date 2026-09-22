# Parked items — specified now so they are not rediscovered later

## P1 — Is A's rank-2 Killing tensor in the collaborating screen's span on the sampled domain?

**Raised by the bridge at the close of leg 6 (2026-09-22).** Every representability test either party
ran was on `chain4 + εK₁`. But that screen does not hunt for that object — it hunts for *any*
conserved quantity. So "span is not the limitation" was a claim about our **approximation**, not
about the object being searched for.

**The item as posed:** produce A's exact rank-2 Killing tensor; they fit it against `d2_rat` on
r ∈ [5.107, 9.147].

**AND THE CAVEAT THAT MAKES IT ILL-POSED AS STATED, recorded before anyone plans a run:**

> **We do not know that A has an exact rank-2 Killing tensor, and this repo cannot produce one.**
> Every result behind "A keeps Carter" is **first order in ε** — the compatible-space computation
> solves `{H₀,F⁽¹⁾} + {δH,K⁽⁰⁾} = 0`, which says the O(ε) obstruction vanishes and *nothing about
> O(ε²)*. The complete rank-4 product algebra surviving is likewise an O(ε) statement. A deformation
> can admit a first-order extension of Carter and no exact one; the whole §140–§143 arc is built
> inside that limitation (CLAUDE.md §3, ceiling 1).

So P1 splits into two, and only the second is currently answerable:

1. **Does A keep Carter exactly, at finite ε?** *Open, and out of reach of this instrument.* It would
   need the tower carried to O(ε²) at minimum, and an all-orders statement needs an argument rather
   than a computation.
2. **Is `chain4 + εK₁` — the first-order object we actually have — in their span on the sampled
   domain?** *Answerable, and partly answered:* the horizon pole does **not** exclude it there
   (residual 4.19e-05 against their existing basis), so whatever their CERTIFY is responding to
   remains unknown.

**What to hand them if P1 is ever taken up:** the O(ε) object, labelled as O(ε), with the manifest's
eight fields — including DOMAIN. Handing over "A's exact Killing tensor" would be shipping an object
whose existence we have not established, which is the night's central failure in its purest form.


---

## P1, ANSWERED (2026-09-22, by a scan already running)

**The screen's margin does not measure integrability.** A, B and C all returned exponent ~2.000,
R² 1.0000, B/A = 1.00 across two decades — three different integrability structures, indistinguishable.
It is the generic variance response to being deformed at O(ε), which needs nothing about Killing
tensors.

**But A's exponent is informative where B's is not, and the ε=0 row supplies the premise:**

    A at eps=0     margin 7.85e-18   EMITS  -> K_0 IS in the span, and the fit FINDS it
    A at eps=0.05  margin 6.02e-07          -> eleven orders higher
    A exponent     1.999 over two decades

The basis is ε-independent and A's invariant survives exactly at every ε. If `K_A(ε) = K₀ + ε·δK + …`
were in the span the fit would find it at every ε and the margin would sit at the ε=0 floor —
exponent 0. It rises as ε². Conditioning is excluded (κ^0.03). **So `δK` is outside the span on the
sampled domain.**

**Why B makes it an argument rather than an observation:** B has nothing exact to miss, so its
exponent-2 is pure generic response. Same number, opposite information content — **and the difference
is supplied by our symbolic result (A keeps Carter, B does not), not by anything they can measure.**
Cleanest instance in the whole exchange of a symbolic and a numerical result each being useless alone.

### The remaining test, which now has opposite predicted signs

    add dK to the library  ->  A's exponent must COLLAPSE from 2 toward 0
                               B's exponent must NOT move  (no exact invariant to complete)

### What we can actually supply, and its scope

`δK` is the first-order correction to **Carter**, exact in χ. `K₁` corrects the **χ²-truncated
chain4**. Different objects — K₁'s representability says nothing about δK's, which is why four
sound-looking exclusions tested the wrong thing.

**To O(χ²) it is producible from what we already have.** From chain4 = −8Q − 7P_φ² + 56χ²(H + P_t²),
with P_φ², P_t² exactly conserved and H_def conserved:

    dK = -(K1 - 56*chi^2*dH)/8        to O(chi^2),  dH = the deformation's Hamiltonian contribution

**EXACT IN χ IT IS NOT PRODUCIBLE HERE** — same ceiling as the original P1. So the test above would
run against a χ²-accurate δK, and a partial collapse of A's exponent would be ambiguous between
"δK is the missing span" and "δK is only partly right at this χ". Worth stating before the run, not
after.
