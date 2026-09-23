#!/usr/bin/env python3
"""Score a _kt_pole_reduced.py output against a prediction SEALED BEFORE the run.  (weekend rank 8)

WHY THIS EXISTS.  A long run read by the person who predicted its answer is read hopefully: a near
miss becomes "basically as expected".  So every weekend job has its expectation written down and
committed first (data/anat/weekend/PREDICTIONS.json), and this script — not a reader — decides
whether the output matched, field by field.

Two modes per job:
  "expect": {...}      named fields, each compared exactly (see FIELDS below)
  "same_as": "<path>"  a reproduction: every parsed field must equal the reference run's, except
                       timings and the prime.  Directions are printed after rational reconstruction,
                       so they are prime-independent and are compared as text.

A field the output does not contain is a MISMATCH, never a skip — an output that crashed before
printing its survivors must not score as "nothing contradicted the prediction".

Usage: _kt_weekend_check.py <job-name>            (reads PREDICTIONS.json and the job's .out)
       _kt_weekend_check.py --file OUT --job NAME  (score an arbitrary file against a job's entry)
Exit 0 = every field matched; 10 = at least one mismatch; 2 = could not score.
MISMATCH is 10, not 1, because a Python that crashes on startup exits 1: a crash must never be
readable as a failed prediction (it once was).
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
PRED = os.path.join(ROOT, "data", "anat", "weekend", "PREDICTIONS.json")


def parse(text):
    """Everything a pole-order run reports, as plain comparable values."""
    out = {}
    m = re.search(r"dim V = (\d+)", text)
    if m:
        out["dim_V"] = int(m.group(1))
    m = re.search(r"nullity (\d+)", text)
    if m:
        out["nullity"] = int(m.group(1))
    m = re.search(r"keeping ALL (\d+): dim (\d+) of (\d+)", text)
    if m:
        out["products"], out["keeping_all"], out["slots"] = int(m.group(1)), int(m.group(2)), int(m.group(3))
    le = {int(k): int(v) for k, v in re.findall(r"\(pole order <= (\d+)\): dim (\d+)", text)}
    if le:
        out["pole_le"] = le
    fa = {int(k): int(v) for k, v in re.findall(r"first appearing with Q\^\d+ \(pole order (\d+)\): (\d+)", text)}
    if fa:
        out["first_appearing"] = fa
    # directions and their survivors, grouped by the pole order of the header they sit under
    dirs, cur = {}, None
    lines = text.splitlines()
    for i, ln in enumerate(lines):
        h = re.search(r"first appearing with Q\^\d+ \(pole order (\d+)\)", ln)
        if h:
            cur = int(h.group(1))
            dirs.setdefault(cur, [])
            continue
        if ln.strip().startswith("named directions"):
            cur = None
        s = re.match(r"\s+survivors (\(.*\))\s*$", ln)
        if s and cur is not None and i > 0:
            dirs[cur].append([lines[i - 1].strip(), s.group(1)])
    if dirs:
        out["directions"] = {k: v for k, v in dirs.items()}
    out["controls"] = dict(re.findall(r"control (\S+): (\(.*\))", text))
    out["random"] = re.findall(r"random #\d+: (\(.*\))", text)
    if not out["controls"]:
        del out["controls"]
    if not out["random"]:
        del out["random"]
    return out


def norm(v):
    """JSON round-trip turns int keys into strings; compare in one canonical form."""
    return json.loads(json.dumps(v, sort_keys=True))


def score(got, want):
    rows, ok = [], True
    for field, w in want.items():
        if field.startswith("_"):
            continue
        if field == "controls_all_keep":
            g = got.get("controls")
            good = bool(g) and all(v.startswith(f"({w},") for v in g.values())
            shown = f"{len(g or {})} controls, keeping {sorted({v.split(',')[0][1:] for v in (g or {}).values()})}"
        elif field == "random_all_keep":
            g = got.get("random")
            good = bool(g) and all(v.startswith(f"({w},") for v in g)
            shown = f"{len(g or [])} random, keeping {sorted({v.split(',')[0][1:] for v in (g or [])})}"
        else:
            g = got.get(field, "<MISSING>")
            good = norm(g) == norm(w)
            shown = json.dumps(norm(g) if g != "<MISSING>" else g, sort_keys=True)
        ok &= good
        rows.append((field, good, shown, json.dumps(norm(w), sort_keys=True)))
    return ok, rows


def main():
    if "--file" in sys.argv:
        path = sys.argv[sys.argv.index("--file") + 1]
        name = sys.argv[sys.argv.index("--job") + 1]
    else:
        if len(sys.argv) < 2:
            sys.exit(__doc__)
        name, path = sys.argv[1], None
    try:
        jobs = {j["name"]: j for j in json.load(open(PRED))["jobs"]}
    except (OSError, ValueError, KeyError) as exc:
        print(f"cannot read predictions: {exc}")
        return 2
    if name not in jobs:
        print(f"no job named {name!r}; known: {sorted(jobs)}")
        return 2
    job = jobs[name]
    path = path or os.path.join(ROOT, job["out"])
    try:
        got = parse(open(path).read())
    except OSError as exc:
        print(f"cannot read output: {exc}")
        return 2
    if "same_as" in job:
        ref = parse(open(os.path.join(ROOT, job["same_as"])).read())
        want = {k: v for k, v in ref.items()}
        label = f"reproduction of {job['same_as']}"
    else:
        want, label = job["expect"], "sealed prediction"
    ok, rows = score(got, want)
    print(f"{name}: {path}\n  scored against the {label}\n")
    for field, good, g, w in rows:
        print(f"  {'ok  ' if good else 'MISS'}  {field}")
        if not good:
            print(f"          got      {g}")
            print(f"          expected {w}")
    print(f"\n  VERDICT: {'MATCH -- every field as predicted' if ok else 'MISMATCH -- the prediction failed somewhere above'}")
    return 0 if ok else 10


if __name__ == "__main__":
    sys.exit(main())
