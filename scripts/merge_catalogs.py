#!/usr/bin/env python3
"""Strict-union merge of cached fingerprints from another catalog file.

Two machines (Mac + VM) cache profiles into their own copies of
catalog_discoveries.json. This folds a SOURCE copy's profiles into the
local one WITHOUT ever overwriting or dropping an existing local profile
— a pure add-only union keyed by family name. Safe to run repeatedly;
nothing a machine has already computed can be lost.

Usage:  .venv/bin/python scripts/merge_catalogs.py <source_catalog.json>
"""

import json
import os
import sys

_here = os.path.dirname(os.path.abspath(__file__))
LOCAL = os.path.join(_here, "..", "catalog_discoveries.json")


def _atomic_write_json(path, data):
    tmp = path + ".tmp"
    with open(tmp, "w") as fh:
        json.dump(data, fh, indent=2)
        fh.flush()
        os.fsync(fh.fileno())
    os.replace(tmp, path)


def main():
    if len(sys.argv) != 2:
        print("usage: merge_catalogs.py <source_catalog.json>")
        return 2
    src_path = sys.argv[1]
    local = json.load(open(LOCAL))
    src = json.load(open(src_path))
    src_prof = {e["name"]: e["profile"] for e in src if "profile" in e}

    added = 0
    for e in local:
        if "profile" not in e and e["name"] in src_prof:
            e["profile"] = src_prof[e["name"]]   # add-only; never overwrite
            added += 1

    have = sum(1 for e in local if "profile" in e)
    if added:
        _atomic_write_json(LOCAL, local)
    print(f"merged: +{added} profiles from {os.path.basename(src_path)} "
          f"→ local now {have}/{len(local)} cached")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
