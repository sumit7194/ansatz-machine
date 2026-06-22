# Roadmap

*Ranked by expected value per hour. Open threads from RESULTS.md live here
now; move items to JOURNAL.md entries as they complete.*

## v8 — Bridge-driven upgrades (2026-06-20, from the bridge project's review)

*Context: after the §56–76 exact-oracle suite was built, the bridge project used
these results to close its gaps (the "spine" — Moves A/B/D). That review surfaced
exactly where ansatz's current oracles are SOFT, and these four (+1 minor) are the
upgrades that would harden them. **Captured here, not yet started** — pick up if/when
the bridge needs them. Ranked by leverage.*

### 1. A precise QNM oracle, beyond the eikonal  ◀ ✅ DONE (2026-06-20, §77)
**Built:** `scripts/qnm_precise.py` — `qnm_precise(M,a,ℓ,m,n)` wraps Leaver (the `qnm`
package, D27). Battery §77: exact Schwarzschild ℓ=2,n=0 = 0.37367−0.08896i (vs §56
eikonal ~3% off), the 221 overtone (a=0.7) = 0.52116−0.24424i, the no-hair test now
0.1%-level. Optional dep (numpy/scipy/numba), isolated from the pure-SymPy core;
§77 fail-soft skips if absent.
§56 gives the eikonal/light-ring QNM and explicitly defers the precise overtone
spectrum to "Leaver / the `qnm` package." That cap is exactly what made the bridge's
ringdown comparison (Move B) a few-to-15% test instead of a precision one. Wrap the
precise solver (the `qnm` package §56 already cites, or a 6th-order WKB) into a
first-class **`qnm_precise(M, a, ℓ, m, n)`** oracle — turning the spine's ringdown link
from "consistent at the light-ring level" into a real **0.1%-level exact↔measured
test**, and giving the **221 overtone** ansatz currently can't (the actual quantity
deepstrain's δ measures). [builds on §56 ringdown, §72 template]

### 2. A symbolic Killing-tensor verifier  ◀ ✅ DONE (2026-06-20, §78)
**Built:** `gr_engine.Geometry.is_killing_tensor` / `killing_tensor_residual` — certifies
`∇₍ₐK_bc₎ ≡ 0` SYMBOLICALLY (cancel→together→expand_trig+simplify; needs only
Christoffels, not Riemann, so it stays tractable in rational u=cosθ coords — closes in
~1s). Battery §78: the metric g passes (∇g=0), a control fails, and Kerr's Carter tensor
`Σ(lₐn_b+l_b nₐ)+r²g` gives `∇₍ₐK_bc₎ ≡ 0` exactly — the Carter constant now a PROOF, not
the numeric residual of §58/§69.

*(original note:)*
§58/§69 compute Kerr's Carter tensor and check `∇₍ₐK_bc₎=0` NUMERICALLY — so Move A's
certification was a numeric residual, not a theorem. Extend **`gr_engine.verify`** to
certify `∇₍ₐK_bc₎ ≡ 0` SYMBOLICALLY (the same cancel→factor→simplify cascade it already
uses for the field equations). That makes the discover→verify pipeline's certification
a **proof, not a measurement** — a real upgrade to the most novel capability. [§58
Killing, §69 Killing–Yano; the numeric verification is honest but not a theorem]

### 3. Full-spin (or O(a²)) rotating modified-gravity black holes  ◀ ⚠ PROBED, full PDE OPEN (2026-06-20, §82)
The rotating-EdGB being O(a) slow-rotation is what blocked the genuine "discover an
unknown invariant" frontier (Move D's pivot): at O(a) the Carter analog trivially
survives. Pushing to **O(a²)** makes the integrability question non-trivial (oblateness
enters); **full-spin** is the real prize but hard (the 2D PDE the EdGB doc flags). [see
EDGB.md / ROTATING.md; ties the Killing-tensor frontier to modified gravity]

**Honest probe (§82, NOT the full solve):** rather than solve a modified theory's O(a²)
field equations (the genuine 2D PDE — still open), we attacked item 3's *scientific core*
with the new tools: deform Kerr by an l=2 quadrupole bump and ask if integrability
survives (§78 Killing-tensor + §79 chaos lens). Result — and the stress-test is what
surfaced it: the *literal* Kerr Carter tensor stops closing (residual ≠ 0), YET geodesics
show NO detectable chaos across a broad orbit scan (λ at the regular floor; the lens DOES
see chaos when present, cf di-hole λ≈2.09). So the naive "deform ⇒ chaos" guess fails;
the deformed metric's integrability is UNDETERMINED — a *different* Killing tensor may
survive, or chaos hides below detection. **Still open:** (a) the actual modified-gravity
O(a²) metric (the 2D-PDE solve); (b) a general Killing-tensor PDE search to decide
integrability of the deformed metric; (c) orbit-resolved Poincaré sections for weak chaos.

### 4. A first-class geodesic integrator + a chaos lens (SALI/Lyapunov)  ◀ ✅ DONE (2026-06-20, §79)
**Built:** `scripts/geodesic_chaos.py` — `trajectory(g,x0,u0)` (RK4) + `lyapunov(g,x0,u0)`
(largest exponent via renormalized nearby orbits), pure Python (no numpy, stays in the
core). Battery §79: Kerr orbit conserves (E,L,μ²,C) to 1e-11 (integrator correct);
λ(Kerr)≈0.009 (REGULAR — the Carter constant §78 forbids chaos); λ(Majumdar–Papapetrou
di-hole)≈2.09 (CHAOTIC, ~222×). Integrability ⟺ a hidden symmetry (§78) ⟺ λ≈0 — the lens
measures what the Killing-tensor proof certifies, on any metric. (Largest-Lyapunov, not
SALI — a clean next refinement.)

*(original note:)*
The bridge built both as throwaway code (and ansatz built geodesic integrators inline in
§54/§58). Make them **native** — `trajectory(metric, x₀, u₀)` + a SALI/Lyapunov chaos
diagnostic — so ansatz can study the **integrability/chaos of its own discovered
metrics**, a natural lens right beside the Killing tensors (§58/§69). Would have made
Move D native instead of bridged. [reusable tool both sister projects can use as ground
truth — the "option B" geodesic tool already flagged]

### (from stress-testing 2026-06-20) tetrad-free Weyl invariants  ◀ ✅ DONE (§83)
The tetrad-free Weyl-SQUARE `C_abcd C^abcd = K − 2R_abR^ab + R²/3` (the magnitude) landed
first (§76(D)). Now the **complex invariants I, J** are also tetrad-free (§83):
`I=(A−iB)/16, J=(C₃−iD₃)/96` with A=C·C, B=C·*C (the Chern–Pontryagin/magnetic part),
C₃ the cubic, D₃ its dual — constants calibrated against the NP I,J on Schwarzschild
(real) and Kerr (complex). So the SPECIALITY (I³=27J² ⟺ algebraically special) is now
chart-free: standard vs isotropic Schwarzschild give identical I,J at the mapped point
(closes the §76 canonical-form caveat); and the off-diagonal case works via the NUMERIC
route (`numeric_curvature.weyl_invariants_numeric`) — Kerr → type D with no tetrad.
HONEST LIMIT (stress-test §83(E)): I,J give speciality + magnitude, NOT the full Petrov
type — a type-N pp-wave has I=J=0 like type O; splitting {II|D} and {III|N|O} still needs
the adapted tetrad (§80) or differential invariants. That's inherent to scalar invariants,
not a coordinate issue. `invariant_fingerprint` now uses the tetrad-free I,J for any
diagonal metric. REMAINING (smaller): differential/Cartan–Karlhede invariants for the
full type chart-free — a bigger project, deferred.

### (minor) petrov() auto-tetrad for off-diagonal/Kerr  ◀ ✅ DONE (2026-06-20, §80, numeric)
`analyzer.petrov` returned UNKNOWN for Kerr — the symbolic Weyl tensor swamps (the
§48/§57 limit; the real blocker is Weyl itself, not just the tetrad). Closed via the
NUMERIC companion (`numeric_curvature.weyl_scalars_numeric` + `petrov_type_numeric`):
battery §80 gives Kerr → type D (only Ψ2≠0 in the Kinnersley tetrad), Ψ2 matches the
exact −M/(r−ia cosθ)³, and the speciality I³=27J² holds. `analyzer.petrov` stays
symbolic + perf-guarded; the fully-automatic principal-null-direction finder for
arbitrary metrics is the general extension.

## v5 — ✅ COMPLETE (2026-06-12)

All three steps below landed: R0′ all-green (039a9f7; κ_c = 1.0 now a
probe-level prediction — deviations from the registration disclosed in
ROTATING.md), R2 banked with a repaired two-holdout protocol (4-number
formula, fresh sealed p=0.75: 0.1730% — see RESULTS.md), and the
expedition step turned out moot (no wide expedition was ever running —
the launch had failed on the pkill self-match bug, see VM.md; a
high-ladder hunt over 8+1..12+1 now runs on the VM instead, tmux
`ladder`). The handoff text below is kept for the record.

## v6 (NEXT — the fork, decide deliberately)

- **(a) The write-up.** v1→v5 is a coherent story: verifier →
  rediscovery → catalog growth → static EdGB universal (0.2751%
  sealed) → rotating EdGB universal (0.1730% fresh-sealed, 4 numbers —
  a COMPACT fit, NOT an open gap: closed-form rotating EdGB exists
  (Ayzenberg–Yunes, Maselli, arXiv:2510.05208); sell compactness only,
  prior-art corrected 2026-06-23). Genre precedent: KKZ, PRD 96, 064004.
- **(b) More physics.** Second order in spin / full 2D rotating EdGB
  (the PDE wall), or a new theory through the same pipeline —
  dynamical Chern–Simons is mostly a REDUCE swap. Harvest the VM
  high-ladder finds either way (re-prove locally before committing
  catalog growth).

## v5 (historical) — self-contained handoff

*Written 2026-06-12 so work continues without the originating chat.
Assumes v5 R1 is banked (commit 4a99c54: κ_c = 1.0, frame-dragging
calibrated). Read [ROTATING.md](ROTATING.md) + [RESULTS.md](../RESULTS.md)
first. Non-negotiables: pre-register gates BEFORE running; never tune a
threshold to fit a result (disclose if you do); `./verify.sh` green
before any push; verifier = truth; launch VM jobs via `tmux new-session
-d` (ssh drops ~50%, see memory `vm-ssh-flaky-use-tmux`).*

### Step 1 — R0′: derive G₂/G₃ ourselves (centerpiece, frontier)

**Why:** R1's κ_c = 1.0 currently CALIBRATES a transcribed Pani–Cardoso
equation. Deriving the frame-dragging ODE ourselves turns κ_c = 1.0 into
a confirmed PREDICTION and restores the airtight chain. Brute force
(`19b_rot_reduce_fast.py`) is parked — GB-scale intermediates for a
two-line answer.

**Idea (credit: Sumit's "terms-as-vector-dimensions" intuition):** never
materialize the giant expression — evaluate it on random EXACT-RATIONAL
points and recover the small answer by a linear solve (Schwartz–Zippel /
sparse interpolation; proof-grade, not a fit).

**Algorithm** (new `scripts/21_rot_fingerprint.py`):
1. Field eq is linear: `E_tφ = G₃·w″ + G₂·w′` (no w⁰ at l=1), so
   `G₃ = ∂E_tφ/∂w″`, `G₂ = ∂E_tφ/∂w′` — background functions only.
2. Posit `G₂, G₃` as unknown rational-coeff sums over a graded monomial
   basis in `{1, r, 1/r, e^Λ, e^Γ, e^φ, Γ′, Λ′, φ′, φ″, α′}`
   (~deg 3, 50–150 terms; print basis size).
3. Per probe: random rational r₀ + random rational background JET at r₀
   (Γ₀,Γ′₀,Γ″₀,Λ…,φ…,α′). Build the metric locally as Taylor polys in
   (r−r₀) with those rationals + w-symbols; compute `E_tφ` via
   `gr_engine` — every intermediate is a NUMBER ⇒ no swell. Extract
   `G₃(r₀),G₂(r₀)` by ∂/∂w″, ∂/∂w′.
4. Each probe → one exact linear eq on the coeffs. Collect N≫K, solve the
   exact rational system, read off `G₂, G₃`.

**Gates (pre-register):**
- **G0 (overdetermination = proof):** solve with K eqs, verify on N−K
  HELD-OUT probes — all exact. This is what makes it a theorem.
- **G1 (GR limit):** α′=0 ⇒ `G₂/G₃ → 4/r − (Γ′+Λ′)/2` symbolically.
- **G2 (matches R1):** recovered `G₂/G₃` equals the PC-transcribed form in
  `20_rot_shoot.py` — ⚠️ **modulo the static EOM** (PC may quote an
  on-shell form; reduce BOTH sides by the static EdGB field equations
  before comparing, or a true match looks false). Pre-registered wrinkle.

On success: ROTATING.md R0 `[x]`, κ_c=1.0 → prediction, add R0′ battery to
verify.sh, gate, push. **Fallback** (partial win if full derivation is
too hard): just VERIFY the transcribed G₂/G₃ exactly at random probes —
restores honesty without deriving from scratch.

### Step 2 — harvest the running expedition (safe, low-effort)

A wide `07_expedition.py` is running on the VM (tmux `exp`, logs to
`~/ansatz-machine/expedition.log`, on the dashboard). Every find is
verifier-checked ⇒ safe. For each `CANDIDATE_NEW`: confirm it isn't a
gauge costume of a known family (invariants K, |∇K|² via 02-fingerprint
logic), confirm physical/positive-mass, then grow into the catalog
(`05_generalize.py`) and journal it. Re-dressed known solution ⇒ correct
null, note it.

### Step 3 — R2: universal rotating fit (the prize)

Same protocol as the static KKZ-class result (0.2751% sealed). Shoot w(r)
on backgrounds at training `p ∈ [0.1,0.6]`; build the **SEALED p=0.7
holdout BEFORE any fitting** (v5's real honesty test — do not peek).
Fit closed-form `w(r;p)` via GN + continuation (15–18 machinery); target
a few tenths of a percent sealed; must be horizon-regular and → 2J/r³ as
p→0. **Prior-art corrected (2026-06-23):** closed-form rotating EdGB DOES
exist (Ayzenberg–Yunes quadratic-in-spin arXiv:1405.2133; Maselli
5th-order arXiv:1507.00680; arXiv:2510.05208 spectral fit incl. sGB).
Frame the target as a COMPACT 4-number fit (KKZ-spirit, compactness
only) — NOT an open gap.

### Operational quick-reference

```bash
./verify.sh                                    # local gate (green before push)
gcloud compute ssh alphaludo-l4 --zone=us-east1-d \
  --command="tmux ls; tail -5 ~/ansatz-machine/expedition.log"   # VM status
# launch long VM job (tmux survives ssh drops):
gcloud compute ssh alphaludo-l4 --zone=us-east1-d \
  --command="tmux new-session -d -s JOB 'cd ~/ansatz-machine && nice -n 19 .venv/bin/python -u scripts/NN_x.py >> JOB.log 2>&1'"
# dashboard: http://34.139.175.159:8080  (firewalled to your IP)
```

---

## v3 (done — historical)

1. **Expedition mode** (`07_expedition.py`) — wire auto-growth into the hunt
   itself: walk uncharted (dimension, Λ) rungs, grow the catalog mid-run,
   prove memory by re-hunting a grown rung. Status: ✅ this session.
2. **Stationary hall** — off-diagonal g_tφ ansatz in RATIONAL coordinates
   (per D4). ✅ 2+1 leg done (rotating BTZ family found gen 12 after the
   D14/D15 saga — first frame-dragging discovery). The 3+1 version is the
   Kerr-shaped mansion: needs multi-coordinate fingerprints and f(r,u)
   genomes — still gated.
3. **Modified-gravity REDUCE** — extend the engine beyond `G_ab + Λg_ab` to
   Einstein-dilaton-Gauss-Bonnet. The EdGB black hole has been known only
   numerically since 1996; the publishable genre is closed-form fits
   (Konoplya–Zhidenko, PRD 96, 064004). Our angle must beat/extend theirs:
   simpler form, better accuracy, or uncovered theories. Requires a
   fit-quality verifier track alongside the exact one.

## Backlog (unordered, each waits for its trigger)

- **Python Cartan–Karlhede** — standalone contribution; trigger: a genuine
  fingerprint ambiguity, or a deliberate decision to build the missing tool.
- **Multi-coordinate fingerprints** — K varying in (r, θ) (Kerr-class
  candidates). Trigger: the stationary hall in 3+1.
- **Island-model GP** — trigger: any hall stagnating across ALL seeds
  (per D12, not before).
- **LLM proposer** (local model) — trigger: GP measurably plateauing on a
  hall we care about. So far GP wins on cost and has not plateaued.
- **Negative-mass-first investigation** — why catalogued rungs yield naked
  singularities first but uncharted rungs gave black holes. Testable: move
  SAMPLE_R relative to horizon zeros. Small, fun, journal-entry-sized.

## Standing constraints

- Mac-first: everything must keep running on a laptop CPU until a hall
  genuinely needs more (then a VM — see SpaceTime project context).
- One dependency (SymPy) unless a new track (e.g. numeric EdGB integration)
  justifies SciPy — justify in DECISIONS.md first.
- Null results are results: an exhausted hall gets a RESULTS.md section and a
  JOURNAL entry, not silence.
