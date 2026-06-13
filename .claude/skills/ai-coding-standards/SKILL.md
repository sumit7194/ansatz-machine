---
name: ai-coding-standards
description: General engineering standards and anti-slop guardrails for AI-assisted coding in ANY language or framework. Use this skill whenever you write, review, refactor, or plan code in this project — features, bug fixes, dependency changes, tests, refactors — even for "quick fixes" and one-line changes. It encodes the working loop (search-before-write, smallest diff, verify-before-done), dependency restraint rules, and countermeasures for documented AI-generated-code failure modes (duplication, hallucinated packages, stale APIs, weakened tests, premature "done" claims). Grounded in 2024–2026 research (GitClear, DORA, METR, USENIX, Veracode).
---

# AI Coding Standards (framework-agnostic)

> Portable skill. To install: copy this folder to `<project>/.claude/skills/ai-coding-standards/` (project-level) or `~/.claude/skills/ai-coding-standards/` (all projects). Then fill in the "Project adaptation" section at the bottom for the specific stack.

## Why this exists — the evidence

Research on AI-generated code shows its failures are **additive**:

- Duplicated code blocks rose **~8× in 2024**; copy/paste exceeded refactoring for the first time on record (GitClear 2025, 211M changed lines).
- Each +25% AI adoption correlated with **−7.2% delivery stability**, driven by larger change batches; gains only materialize with small batches + strong tests (DORA 2024/2025).
- Experienced devs were **19% slower** with AI on real tasks — while believing they were ~20% faster (METR RCT 2025). Perceived speed is not real speed.
- **19.7%** of LLM-recommended packages don't exist; attackers pre-register hallucinated names with malware — "slopsquatting" (USENIX Security 2025).
- **45%** of AI-generated code introduced OWASP-class vulnerabilities; newer models were NOT more secure (Veracode 2025).
- Top developer frustration: "AI solutions that are *almost right, but not quite*" (66%, Stack Overflow 2025).

**The pattern:** AI failure is additive — more code, more duplication, more defensive bloat, bigger diffs, premature "done". Quality engineering is **subtractive and verificatory** — reuse, delete, scope down, prove. When in doubt, make the subtractive move.

## The loop — every task, no exceptions

**Before writing code:**
1. Read the 2–3 nearest existing files. Match their style, naming, and patterns exactly — consistency beats personal preference.
2. Search the codebase for existing helpers/components/modules that already do the job. A near-duplicate of existing code is a defect, not a style issue.
3. If the repo already solves a class of problem (error handling, HTTP client, DI, validation, date formatting), extend that solution. Introducing a parallel mechanism for a solved problem requires explicit human approval first.
4. Verify every API against the **installed** version (lockfile + that package's docs/changelog), not memory — training data is stale.
5. Plan briefly. For multi-file work, state the plan before editing.

**While writing:**
- Smallest diff that completes the task. No drive-by reformatting, renames, or refactors mixed in — propose those separately.
- Comments explain *why* only — never narrate what the next line does. No emoji, no "Step 1/2/3" comments, no banner comments.
- No speculative abstraction: no interface/abstract class with one implementation, no manager/wrapper/config layers "for later". Rule of three before extracting.
- Trust the type system: no redundant null/undefined checks on values the types already guarantee; every try/catch, retry, or timeout must name the failure scenario it handles.

**Before claiming done — the gate:**
1. Run the project's full local gate: formatter + linter/static analysis (zero findings) + test suite. If the project has a verify script, use it.
2. Show the real output. Never state that tests/analysis pass without fresh output from this session. "It should work" is not a status.
3. Self-review the diff hunk by hunk against the checklist below: dead code deleted, old paths removed, unused imports gone, docs updated if behavior or commands changed.
4. If a gate fails: fix it or report the failure honestly. Never weaken, skip, or delete a test to get green — if a test looks wrong, stop and say so.

**When stuck:** after 2 failed fix attempts, stop adding code. Re-read the code, reproduce the failure deliberately, write a one-line root-cause hypothesis, then edit. Layering workarounds (band-aid retries, swallowing errors, widening types, casting away) is forbidden.

## Dependency restraint (a top documented complaint)

Order of preference, strictly: **standard library → framework built-in → an existing dependency in the project → a new dependency**. A new dependency is a last resort with a stated justification, not a convenience.

Before adding ANY package:
1. Does the stdlib/framework or an existing dep already cover this? If yes, stop.
2. Confirm it **exists** on the official registry (npm/PyPI/pub.dev/crates.io/Maven) — query the registry, don't trust memory. ~20% of LLM package suggestions are hallucinated, and those names get weaponized.
3. Vet it: maintained (release within ~12 months), known/verified publisher, healthy adoption (downloads/stars), active issue tracker, compatible license, sane transitive dependency count.
4. Add with a standard version constraint; **commit the lockfile** (for applications). Version pinning lives in the lockfile, not the manifest.
5. One major-version upgrade per PR, with the changelog read and the full test suite run.
6. Dependency overrides/resolutions are temporary: each carries a TODO with an upstream issue link.

Never add a dependency to avoid writing 20 lines of code. Never add two packages that solve the same problem class.

## Failure-mode catalog → rules

1. **"Almost right, but not quite"** → Never trust plausibility. Prove every change with executed checks plus a deliberate trace of edge cases: empty, null/missing, error path, concurrent/duplicate call.
2. **Duplication instead of reuse** → Search before writing (by concept, not just exact name). Extending the existing helper is the default; near-duplicates block review.
3. **Ignoring conventions / second pattern for a solved problem** → Copy the style of neighboring files; one pattern per problem class (one error model, one HTTP client, one DI style, one state approach).
4. **False "done" claims** → No completion claim without fresh verification output shown in the same message.
5. **Weak or gamed tests** → Tests are a contract: never delete/skip/weaken an assertion to pass; never special-case test inputs in production code; assert behavior (outputs, state transitions), not internals.
6. **Swallowed exceptions / silent fallbacks** → No empty catch; no catch-log-return-null; no broad catch without a typed clause outside top-level handlers. Handle with a real recovery strategy or rethrow. Errors must surface.
7. **Doom loops — fixing by adding** → The 2-strikes rule above. Root cause before the third edit.
8. **Over-engineering** → Solve today's problem in the fewest concepts. No config layers, plugin systems, or generic frameworks for one caller.
9. **Hallucinated packages/APIs** → Registry check before adding; signature check against installed version before calling.
10. **Stale-training-data APIs** → Treat memorized API knowledge as suspect; check current docs for anything deprecated-prone; keep the linter/compiler strict so it catches what review misses.
11. **Huge unfocused diffs** → Touch only task-required files; keep changes reviewable (aim under ~300 changed lines per PR). DORA links big batches directly to instability.
12. **Narration comments** → Comments state constraints and *why*. Delete any comment restating the line below it.
13. **Dead code and leftovers** → Replacing logic means deleting the old path, its imports, and helpers in the same change. Commented-out code is never committed. Deleting code is progress.
14. **Defensive bloat** → See "trust the type system" above. Cargo-cult retries/timeouts without a named failure scenario get removed.
15. **Stale docs** → Any change altering behavior, commands, or setup updates the corresponding doc (README/CHANGELOG/comments) in the same diff — or states explicitly that none exists.

## Self-review checklist (run before every "done")

- [ ] Full gate run (format + lint/analyze + tests); real output shown; green
- [ ] No near-duplicate of an existing helper introduced
- [ ] Old code paths, unused imports, orphaned helpers deleted; no commented-out code
- [ ] Diff contains only task-related changes
- [ ] Every catch handles specifically or rethrows; nothing silently swallowed
- [ ] New dependencies registry-verified and vetted; APIs checked against installed versions
- [ ] Comments are why-only; zero narration
- [ ] Tests assert behavior; none weakened, skipped, or deleted
- [ ] Edge cases traced: empty, null, error path, concurrent/duplicate
- [ ] Docs/CHANGELOG updated if behavior, commands, or setup changed

## Project bookkeeping (generic)

- **Small scoped tasks**: well-defined tasks with clear acceptance criteria produce dramatically less slop than "build the whole thing" prompts. Decompose before generating.
- **Lockfiles committed** for applications; dependency audit (outdated check) monthly; routine upgrades in their own PR.
- **CHANGELOG.md** (Keep-a-Changelog): user-visible changes add a line under `[Unreleased]` in the same PR.
- **ADRs** (`docs/adr/NNNN-title.md`, Status/Context/Decision/Consequences): significant decisions are written down; accepted ADRs are superseded, never silently contradicted. Check `docs/adr/` before proposing architectural changes.
- **CI as the backstop**: the same gate (format check, lint with zero findings, tests, coverage floor that ratchets up) runs on every PR. A bug fix without a regression test isn't done.
- **README honesty**: setup commands in the README must actually work; they're part of the same-diff doc rule.

## Project adaptation — the Ansatz Machine (conjecture_machine)

**What this project is.** A propose→verify→evolve loop hunting exact/closed-form
solutions of gravity field equations. The verifier is mathematics (SymPy), so the
usual "tests" here are *mathematical gates*, and "done" means a green gate plus an
honest disclosure trail. The standards above apply, but the highest-leverage ones
are: smallest-diff, search-before-write, no new dependencies, no false "done", and
the honesty rules (below) that are stricter than generic testing.

**Stack + versions.**
- Python ≥ 3.12 (dev box runs 3.14). The venv is `.venv/`.
- Exactly **one** runtime dependency: **SymPy** (`requirements.txt`). This is a hard
  rule (see DECISIONS.md **D1**). Stdlib-only otherwise — no NumPy/SciPy/pandas.
  Adding any dependency requires a written DECISIONS.md entry justifying it FIRST.
- No formatter/linter is configured; match the existing style by hand (4-space
  indent, ~79-col comments, snake_case, module-level docstrings that state the
  step number and what failure each design choice bought).

**The verify command (the only gate that matters).**
```
./verify.sh        # runs every battery; prints "VERIFY: ALL GREEN ✅" or failures
```
Never claim done without a fresh green `./verify.sh` in the same session. Individual
batteries (e.g. `.venv/bin/python scripts/01_verifier.py --kerr`) for fast iteration,
but the full gate is the bar before any commit/push.

**One-pattern-per-problem table (extend these, do not fork a parallel mechanism):**
| Problem | The one pattern here |
|---|---|
| Curvature math (Christoffel→Riemann→Ricci→Einstein) | `scripts/gr_engine.py` only — no second GR engine |
| Verdicts | three-valued: VERIFIED / REJECTED / UNPROVEN (D3) — never a boolean "pass" |
| Zero-testing | prefer rational coordinates so it's decidable (D4); numeric spot-check before symbolic |
| Novelty / "is this known?" | `scripts/02_fingerprints.py` invariant-curve matcher; declare blind spots, never bluff |
| Catalog growth (memory) | `scripts/05_generalize.py` `grow()` → `catalog_discoveries.json` |
| Cross-script import | `importlib.util.spec_from_file_location(...)` with a `scripts/` path; add `sys.path.insert(0,'scripts')` for `gr_engine` |
| Sealed-holdout fits | `scripts/sealed_holdout.py` — seal once, score one candidate, ledger every access (D21) |
| Design decisions | `docs/DECISIONS.md` IS the ADR log (D-numbered). Check it before changing rules; supersede explicitly, never silently contradict |
| Activity log | `docs/JOURNAL.md` (dated, newest first); measured numbers in `RESULTS.md` |

**Honesty rules (project-specific, override generic testing guidance when stricter):**
- Pre-register gates BEFORE running a hunt/fit. Never tune a threshold to fit a
  result; if you do, disclose it in the docs (see the rejected post-hoc threshold
  in ROTATING.md).
- Sealed holdouts are built BEFORE any fitting and scored ONCE on the frozen
  candidate, through the `sealed_holdout` ledger. Selecting a model by holdout
  error is the cardinal sin (it happened once in R2 — caught, repaired, disclosed).
- Null results are results: an exhausted search gets a RESULTS.md section, not silence.
- Regression batteries VERIFY the banked artifact; they don't re-derive it (D20).
  Re-derivation lives behind an explicit `--refit`-style flag.

**Where things live.**
- `scripts/NN_name.py` — numbered pipeline steps; the number is the rough order.
  `scripts/gr_engine.py`, `scripts/ansatz_status.py`, `scripts/sealed_holdout.py` are
  the un-numbered shared modules. (VM-local helper runners use 9x numbers, untracked.)
- `docs/` — JOURNAL, DECISIONS (=ADRs), ROADMAP, RESULTS-adjacent notes (EDGB,
  ROTATING, VM, GLOSSARY, SEARCH_STRATEGIES, STORY).
- `RESULTS.md` — the measured lab notebook (top-level).
- `catalog_discoveries.json` — the machine's persistent memory (proved families).

**Deprecation / footgun traps specific to this repo (AI-stale-knowledge spots):**
- SymPy `simplify()` blanket-applied to large tensors does not terminate in
  practical time (Kerr: >12 CPU-min). Use the targeted Ricci-form check (D2) and
  rational coordinates (D4). `together`/`cancel`/`trigsimp` beat blanket `simplify`.
- `simplify(x) != 0` never proves `x ≠ 0` (Richardson undecidability) — that's why
  verdicts are three-valued. Don't "fix" an UNPROVEN by forcing a boolean.
- Assumptions are load-bearing: `positive=True` on `M`, `r` is required or SymPy
  refuses `sqrt(r**2)→r`. Don't strip assumptions to make an expression collapse.
- `setsid` is Linux-only — on the Mac dev box use `nohup ... & disown` to detach
  long runs (a silent failure cost ~75 min once; see JOURNAL 2026-06-12 night).
- **Concurrent catalog writes are unguarded** (KNOWN ISSUE): `catalog_discoveries.json`
  has no file lock. Two writers (e.g. an oracle proving rungs + a parallel hunt
  growing families) can clobber each other. RULE until a lock exists: never run two
  catalog-writing jobs at once; on the VM, hunts log finds and we re-prove + grow
  locally. (Map of the generic "concurrent/duplicate call" edge case to this repo.)

**VM split (see docs/VM.md).** Mac = dev/edit/authority (all writes, git push from
here). VM = long unattended runs only, results travel back as log lines and are
re-proved locally before entering the catalog. Launch VM jobs in named tmux
sessions; never `pkill -f <name>` inside an ssh command that also contains `<name>`
(it kills its own shell — the "flaky ssh 255" bug).
