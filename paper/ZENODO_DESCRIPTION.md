# Zenodo record draft (NOT published; for the Bridge's read and Sumit's yes)

- **Resource type:** Publication / Preprint
- **Title:** Twisted Kerr-mass vacuum fields: non-integrability of the axial geodesic flow. Numerical results, with
  computer-assisted certificates near Kerr and over part of the twist range (AI-assisted)
- **Creator:** Pal, Sumit (Independent researcher; ORCID 0009-0000-9541-2793)
- **Publication date:** at publication
- **Version:** draft 1
- **Language:** English
- **License (proposal; Sumit to confirm):** Creative Commons Attribution 4.0 International (CC BY 4.0)
- **Files:**
  - `main.pdf` (the preprint, previewed on the page);
  - `SUMMARY.pdf` (one-page plain summary);
  - `REFEREE_GUIDE.md`, `README.md`, `SHA256SUMS.txt`;
  - the LaTeX source `main.tex`, `SUMMARY.tex`, the figure data `fig_bounds_*.dat` and `make_figure_data.py`.
  - The record has few files, with no ZIP, so the preview works. The code lives in the software record below.

## Description (sections as they will appear)

**Result.** For a one-parameter family of stationary axisymmetric vacuum fields that keep Kerr's mass profile on the
symmetry axis and deform only the twist (k = 0 is Kerr; physical range 0 ≤ k ≤ 30/7), we find the following. The
first-order normal variational equation along the L_z = 0 timelike geodesic on the lower symmetry axis has a
Zariski-dense monodromy group in SL(2, C) for every real k in (0, 30/7], at energy E = 0.8 and spins
a ∈ {0.3, 0.6, 0.8, 0.9} (M = 1). By Morales–Ramis–Simó theory, the geodesic flow then has no complete set of first
integrals meromorphic near the complexified orbit; so, at this numerical grade, Carter's constant does not
survive the twist.

**Grades.**
- **Numerical over the whole range:** 50-digit argument-principle counts.
- **Proved next to Kerr,** relative to a stated chain of applicability results, for 0 < |k| ≤ ε_a, with
  ε_a = 2.79e−3, 1.92e−3, 8.39e−4, 1.06e−4.
- **Certified in interval arithmetic** at the end sliver near k = 30/7.
- **Certified by computer-assisted interval arithmetic** for every real k in [1/640, 3] at a = 0.6 (with the above,
  all of 0 < k ≤ 3) and in [1/320, 3] at a = 0.3.
- Runs at a = 0.8 and 0.9 are in progress.

**Method.**
- Monodromy of the axis variational equation around two loops, with
  F = tr[M1, M0] − 2, tr M0, tr M1 and the finite-group traces as tests.
- Argument-principle counts over complex twist rectangles.
- Near Kerr: a closed-form k² coefficient and a certified remainder bound.
- Over segments: Chebyshev interpolation of Arb node values, with a proved bound on a Bernstein ellipse.

**Verification.**
- Every node value of every certified segment was recomputed by an independent 50-digit implementation.
- Must-fail controls (a planted zero, a held-out node, a shrunken bound, a planted precondition) behaved as required.
- Certified verdicts reran byte-identically, and one certificate was reproduced on a second machine.
- Predictions were fixed before each run and committed, with hits and misses reported.
- Independent checks were made by separate AI sessions, as described below.

**Limits.**
- Four spins and one energy.
- Only integrals meromorphic near the complexified orbit are excluded.
- Nothing off the axis is checked, and these are not black holes.
- Part of the applicability chain is our own unrefereed proof.
- The twist range [3, 30/7 − δ0] is numerical only.
- No external expert has reviewed this work.

**AI assistance.**
- This work was carried out with AI assistance: Claude (Anthropic) for code, analysis and drafting, and Gemini
  (Google) for hostile referee reads.
- The independent checks were done by separate AI sessions, not by human peer review.
- The author chose the questions, directed and reviewed the work, and takes full responsibility for the content.

## Keywords
Kerr metric; Carter constant; integrability; Morales–Ramis theory; differential Galois theory; monodromy;
stationary axisymmetric vacuum; Ernst equation; computer-assisted proof; interval arithmetic; geodesics;
AI-assisted research

## Related identifiers
| relation | identifier | what |
|---|---|---|
| isSupplementedBy | 10.5281/zenodo.24593416 (DOI) | Ansatz Machine v1.2.0: software, data and logs |
| isSupplementedBy | https://github.com/sumit7194/ansatz-machine (URL) | repository; the segment-certificate logs are on branch `personal/2026-11-26-route1-check` |
| cites | 10.1103/PhysRev.174.1559 | Carter 1968 |
| cites | 10.1103/PhysRevLett.11.237 | Kerr 1963 |
| cites | 10.1103/PhysRev.167.1175 | Ernst 1968 |
| cites | 10.1007/978-3-0348-8718-2 | Morales-Ruiz 1999 (book) |
| cites | 10.4310/MAA.2001.v8.n1.a3 | Morales-Ruiz and Ramis 2001 |
| cites | 10.1016/j.ansens.2007.09.002 | Morales-Ruiz, Ramis and Simó 2007 |
| cites | 10.1016/S0747-7171(86)80010-4 | Kovacic 1986 |
| cites | 10.1103/PhysRevD.88.064003 | Maciejewski, Przybylska and Stachowiak 2013 |
| cites | 10.1007/s10714-023-03170-z | Destounis and Kokkotas 2023 |
| cites | arXiv:2607.27129 | Ramond 2026 |
| cites | 10.1093/mnras/stu715 | Markakis 2014 |
| cites | 10.1103/PhysRevD.77.024035 | Gair, Li and Mandel 2008 |
| cites | 10.1103/PhysRevD.81.124005 | Lukes-Gerakopoulos, Apostolatos and Contopoulos 2010 |
| cites | 10.1088/0264-9381/9/11/013 | Manko and Novikov 1992 |
| cites | arXiv:0806.0016 | Chruściel and Costa 2008 |
| cites | 10.1137/130932132 | Trefethen and Weideman 2014 |
| cites | 10.1137/1.9781611975949 | Trefethen, ATAP (2019) |
| cites | 10.1109/TC.2017.2690633 | Johansson, Arb (2017) |

Every DOI above was resolved at Crossref, and the arXiv identifiers at the arXiv API, on 2026-11-28. Titles, venues
and years match the reference list.
