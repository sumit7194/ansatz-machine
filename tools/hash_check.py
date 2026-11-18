#!/usr/bin/env python3
"""Block a cross-session message that cites a commit hash which resolves in NONE of the fleet repos (read-only).
Usage: hash_check.py <file|->   exit 0 = ok, 1 = unresolved hash(es) found.
Candidates: 7-40 lowercase hex chars containing at least one digit and one letter, not part of a longer hex run,
not adjacent to '-' (uuids) or to '…' / '...' (truncated sha256 seals). 64-hex sha256 seals are skipped."""
import os
import re
import subprocess
import sys

REPOS = ["conjecture_machine", "TheBridge", "quantum", "quantum-mnthm", "SpaceTime", "BlackHole", "corner_function"]
BASE = "/Users/sumit/Github"
TOK = re.compile(r"(?<![0-9a-fA-F\-…./])([0-9a-f]{7,40})(?![0-9a-fA-F\-…])(?!\.\.\.)")


def candidates(text):
    out = []
    for m in TOK.finditer(text):
        t = m.group(1)
        if re.search(r"[0-9]", t) and re.search(r"[a-f]", t):
            out.append(t)
    return sorted(set(out))


def resolves(h):
    for r in REPOS:
        p = os.path.join(BASE, r)
        if not os.path.exists(p):
            continue
        if subprocess.run(["git", "-C", p, "cat-file", "-e", f"{h}^{{commit}}"], capture_output=True,
                          timeout=10).returncode == 0:
            return r
    return None


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else "-"
    text = sys.stdin.read() if src == "-" else open(src).read()
    bad = [h for h in candidates(text) if resolves(h) is None]
    if bad:
        print("UNRESOLVED commit hash(es), found in no fleet repo: " + ", ".join(bad))
        sys.exit(1)
    print("OK")


if __name__ == "__main__":
    main()
