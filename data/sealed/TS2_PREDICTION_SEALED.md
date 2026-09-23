# SEALED — ansatz-machine's expectation for Tomimatsu–Sato δ=2 (NOT for the receiving tool)

*Committed 2026-09-24 BEFORE the metric is handed over and before any Morales–Ramis / Kovacic result
exists. Per the sealed-construct / blind-score protocol (D57): the receiving tool gets the metric and its
scope manifest only (`data/sealed/TS2_for_quantum/`), never this file. Open it only after the tool's
verdict is committed.*

**Prediction:** Tomimatsu–Sato δ=2 with q ≠ 0 admits **no additional meromorphic first integral** of the
geodesic flow (non-integrable), for generic q in (0, 1). At q = 0 it reduces to Zipoy–Voorhees δ=2, which is
proven non-integrable (Maciejewski–Przybylska–Stachowiak 2013), so the q → 0 limit must agree.

**Confidence:** moderate-to-high for "non-integrable"; LOW for any claim about *where* the obstruction first
shows (which particular solution, which order of variational equation). No prediction is made about the
equatorial reduction being solvable or not.

**What this expectation rests on, and what it does NOT rest on:**
- TS δ=2 is Petrov type I, so there is no Carter-type rank-2 Killing tensor (literature; not re-derived here).
- ZV δ=2 (its q = 0 member) is proven non-integrable in the meromorphic sense.
- Numerical encodings (Brink, PRD 78 102002) point the same way.
- **No E-rung (exact rank-bounded) Killing-tensor computation on TS δ=2 has been run in this repo.** None
  exists to withhold. When one is run (deferred: heavy, disk-held), its result will also be sealed until the
  tool reports.

**What would surprise us:** a solvable (Liouvillian) normal variational equation along every admissible
particular solution for generic q — that would be a genuine hint of hidden structure and worth an E-rung run
immediately.
