#!/usr/bin/env python3
"""Pre-send blinding guard. Usage: blind_check.py <recipient> <file-with-message-text>  (or '-' for stdin).
Exit 1 and print every match if the text hits an active embargo for that recipient ('*' embargoes apply to all).
Rule (bridge, 2026-10-18, after two C0 slips): every cross-session message is drafted to a file and must pass this
check before SendMessage. Embargoes live in tools/EMBARGOES.json; remove one only when its seal arrives."""
import sys, re, json, os
rec, path = sys.argv[1], sys.argv[2]
text = sys.stdin.read() if path == '-' else open(path).read()
E = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'EMBARGOES.json')))['embargoes']
hits = []
for e in E:
    r = e['recipient']
    if r != '*' and not rec.strip().lower().startswith(r.lower()): continue   # also matches 'name [ref]' and uds addresses with the name
    for p in e['patterns']:
        for m in re.finditer(p, text, re.I):
            hits.append((e['id'], m.group(0)[:120]))
if hits:
    print('BLOCKED: message hits active embargo(es):')
    for i, h in hits: print(f'  [{i}] ...{h}...')
    sys.exit(1)
print('OK: no embargo hits for', rec)
