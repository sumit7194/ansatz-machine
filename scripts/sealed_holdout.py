#!/usr/bin/env python3
"""Sealed-holdout guard — makes "peeking at the answer key" impossible
to write by accident.

Why this exists (measured failures, 2026-06-12): two protocol
violations in two days survived until a human audit caught them — a
post-hoc threshold (Gemini incident, R1) and winner-selection by
holdout error (R2, repaired). Audits are the last line of defense;
this module is the first.

The rules it enforces:
  1. `seal(path, builder)` — truth data is built ONCE and written to
     disk. If the file exists it is loaded, never rebuilt.
  2. `score_once(path, candidate_id, scorer)` — every scoring access
     is appended to a ledger file next to the truth file. The FIRST
     candidate scored is locked in; scoring a DIFFERENT candidate
     against the same seal raises SealViolation. Re-scoring the same
     frozen candidate (regression re-runs) is always fine.
  3. Overrides are possible but never silent: pass a written reason
     and it is recorded in the ledger forever.

Stdlib only. The ledger is advisory-but-honest: it cannot stop a
hostile actor, only an absent-minded one — which is the actual threat.
"""

import hashlib
import json
import os
import time


class SealViolation(RuntimeError):
    pass


def _ledger_path(path):
    return path + ".ledger.json"


def _load_ledger(path):
    lp = _ledger_path(path)
    if os.path.exists(lp):
        with open(lp) as fh:
            return json.load(fh)
    return {"sealed_at": None, "accesses": []}


def _save_ledger(path, ledger):
    with open(_ledger_path(path), "w") as fh:
        json.dump(ledger, fh, indent=2)


def candidate_fingerprint(obj):
    """Stable id for 'the thing being scored' — e.g. the coefficient
    list of a frozen formula. Same numbers -> same fingerprint."""
    blob = json.dumps(obj, sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()[:16]


def seal(path, builder):
    """Load truth data from `path`, or build + write it exactly once.
    `builder()` must return a JSON-serializable object."""
    if os.path.exists(path):
        with open(path) as fh:
            return json.load(fh)
    data = builder()
    with open(path, "w") as fh:
        json.dump(data, fh)
    ledger = _load_ledger(path)
    ledger["sealed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")
    _save_ledger(path, ledger)
    return data


def score_once(path, candidate_id, scorer, override_reason=None):
    """Score one candidate against the sealed truth at `path`.

    `candidate_id`: fingerprint of the candidate (use
    candidate_fingerprint()). `scorer` is called with the loaded truth
    data and must return the score. The first candidate ever scored is
    locked in; a different candidate_id raises SealViolation unless an
    override_reason is given (and recorded).
    """
    if not os.path.exists(path):
        raise SealViolation(f"no sealed truth at {path} — seal() first")
    ledger = _load_ledger(path)
    prior = {a["candidate"] for a in ledger["accesses"]
             if not a.get("override")}
    if prior and candidate_id not in prior and not override_reason:
        raise SealViolation(
            f"seal {os.path.basename(path)} already consumed by candidate "
            f"{sorted(prior)} — scoring a different candidate is exactly "
            f"the bug this guard exists for. If this is deliberate, pass "
            f"override_reason (it will be recorded).")
    with open(path) as fh:
        truth = json.load(fh)
    score = scorer(truth)
    # Re-scoring an already-recorded candidate is a no-op for the ledger
    # (keeps the file stable across regression-gate runs).
    already = any(a["candidate"] == candidate_id and not a.get("override")
                  for a in ledger["accesses"])
    if not already or override_reason:
        ledger["accesses"].append({
            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "candidate": candidate_id,
            "score": repr(score),
            "override": override_reason,
        })
        _save_ledger(path, ledger)
    return score


if __name__ == "__main__":
    # self-test in a temp dir
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        p = os.path.join(td, "truth.json")
        data = seal(p, lambda: {"answer": 42})
        assert data["answer"] == 42
        assert seal(p, lambda: {"answer": 99})["answer"] == 42  # no rebuild
        s = score_once(p, "cand-A", lambda t: t["answer"] / 2)
        assert s == 21
        score_once(p, "cand-A", lambda t: t["answer"])  # same cand: fine
        try:
            score_once(p, "cand-B", lambda t: t["answer"])
            raise AssertionError("SealViolation not raised")
        except SealViolation:
            pass
        score_once(p, "cand-B", lambda t: t["answer"],
                   override_reason="self-test of the override path")
        ledger = _load_ledger(p)
        assert len(ledger["accesses"]) == 2  # repeat of cand-A deduped
        assert ledger["accesses"][-1]["override"]
    print("sealed_holdout self-test PASSED ✅")
