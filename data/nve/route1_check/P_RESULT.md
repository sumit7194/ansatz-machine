# v7 stage P (three pilots at spin 3/5): NONE certified. By the registration: STOP and bring a fresh plan

**Office ansatz-machine (Claude Opus), 2026-11-28 (day 0).** The registration is `V7_REGISTRATION.md`, stage P, with
addenda 5–10. Each pilot got ONE attempt, per the Bridge's ruling. Pilot 1 is graded a post-failure amendment (one
fix, one rerun).

**Disclosures, part of the verdict:**
- **Pilot 1:** its first attempt failed on the precondition (a one-ball root bound over a k-box straddling k = 4). It
  was fixed by addendum 6 (25 sub-boxes) and rerun once. The empty-hash runner bug of the first attempt affected only
  its engine-gate paths. Details are in `P1_RESULT.md`.
- **Pilots 2 and 3:** the precondition guard was reworked (addenda 8–9) after a pre-pilot diagnostic showed refusal at
  the pilot boxes. No pilot certification was attempted before the rework. That rework then had its own non-author
  read (addendum 10) and must-fail control (S).

## Outcomes (all ρ = 4 rows rejected; no verdict, no engine gate, no node file)

| pilot | segment | run | rejection |
|---|---|---|---|
| 1 | circle, k_c 79/20, half 1/20 | rerun 16:28:33, PID 42556 | "holomorphy box fails at 1.3213 + 0.2754i" |
| 2 | region B, k_c 83/20, half 1/20 | 16:34:59, PID 54525 | "holomorphy box fails at 1.5032" (beside the base point bB = 1.5008) |
| 3 | region B dyadic, k_c 30/7 − 1.5e−3, half 1/2000 | 16:34:59, PID 54527 | "holomorphy box fails at 1.5032" |

In pilots 2 and 3 the self-test passed and the region-B second-derivative bound refused nothing (6 calls, 0 refusals).
Each prove took about 30 s.

## Diagnosis (read-only, after the verdicts; nothing rerun, nothing fixed)
**One common mechanism.** v4 requires v2's CRUDE dq bound (`dq_sup`) to succeed on every step box before it tries the
centred bound. On one step box per pilot, G1 or G2 (the ρ-equation's singular functions) could not be certified
nonzero over the box × the whole k-box at ρ = 4. Yet no true zero is near:
- **Pilot 1:** G2 is uncertified on 12 of 25 k-sub-boxes at box radius 0.01, but certified on all 25 at 0.003. The
  nearest true G-zero over the k-square is 0.45 away.
- **Pilots 2 and 3:** the nearest true zero of G1 or G2 (r+, p±) to the refused box over the k-square is 0.27 (P2) and
  0.30 (P3) away.

So it is an **enclosure-width artifact**. The crude bound encloses c0 over Z × K as c0(k_c) + dk·D0 + dk²E0/2 (with
the field's box remainder on Z). With |dk| up to about 0.15 at ρ = 4 and half-width 1/20, the k-direction inflation
makes G's ball contain 0 even though G itself does not vanish. It is **not specific to k ≈ 4**: it hits region B at
4.15 and next to 30/7 too.

## Re-gate note (for the value gate and Sumit; the Bridge's points a–c)
- **(a) Production near k = 4, and in general.**
  - P1's failure alone would touch only the circle segment(s) straddling k = 4: at 3/5, [3.9, 4.0] up to the A/B
    switch.
  - But P2 and P3 show the same crude-bound artifact in region B, so it is a property of the current dq machinery at
    ρ = 4 and production width, not of k ≈ 4. **Every top segment (about 46 at 3/5) is at risk.**
  - The registered response to a rejected row is the **split rule** (halve the segment, to depth 2). It shrinks the
    k-box and quarters the dk² term. Whether it recovers these rows is **UNTESTED**.
- **(b) Measured cost per certified segment:** none was certified, so no v7 top-segment cost exists.
  - The only certified v7 segment is T1' (k ≈ 1, region A): about 21 min including full controls and the engine
    gate, of which prove took 3.6 min.
  - The pilot attempts cost about 0.5–1 min each, because the rejection comes early.
- **(c) Any fix would be a NEW registered stage, not a retry of P.** Candidates, none applied:
  1. A cheap discriminator, like the stop-(c) one: P2's prove at half-width 1/40 and 1/80 (the split rule's depths),
     to see whether the split recovers the row. About 2 core-min.
  2. Tighter k-direction enclosure in the crude bound: more k-sub-boxes (KSUB 5 → 10 or more), or the field's
     K-uniform c0 via addendum 5's segment representation (E-style, with the first k-derivative over K), in place of
     the second-order k-Taylor.
  3. A smaller ellipse (ρ = 3). That conflicts with §5A's "ρ = 4 only", so it needs an amendment.
  Each needs its own registration, read and controls.

**Stage P verdict: NONE CERTIFIED. Stop** (registration: "none by day 17 → stop"). A fresh plan goes to the Bridge and
Sumit. V1, V2 (3/5) and P-B stand as passed; the c0 evaluator, the field, the region-B port and the second-derivative
bound are sound as read. What blocks is the inherited crude dq enclosure.
