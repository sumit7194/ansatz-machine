# Roadmap

*Ranked by expected value per hour. Open threads from RESULTS.md live here
now; move items to JOURNAL.md entries as they complete.*

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
  sealed) → rotating EdGB universal (0.1730% fresh-sealed, 4 numbers,
  unclaimed territory). Genre precedent: KKZ, PRD 96, 064004.
  Unclaimed territory rewards speed.
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
p→0. Gap confirmed: no KKZ-style closed form exists for slow-rotating
EdGB — unclaimed territory.

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
