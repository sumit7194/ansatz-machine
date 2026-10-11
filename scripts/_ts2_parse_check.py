#!/usr/bin/env python3
"""Parser-integrity check (tabula/Bridge, 2026-10-11: Python 3.12's tokenizer crashes or corrupts the heap on the ~26 KB
srepr lines of the TS component files). Parses every TS2 component file with EXACTLY load_package's parser (sympify with
SREPR_NAMES) and prints a sha256 of srepr(all components). Run in many fresh processes under PYTHONMALLOC=debug:
    for i in $(seq 20); do PYTHONMALLOC=debug .venv/bin/python -X faulthandler scripts/_ts2_parse_check.py; done | sort | uniq -c
"""
import sys, glob, hashlib
sys.path.insert(0, "scripts")
import sympy as sp, _kt_exact_op as O
h = hashlib.sha256()
files = sorted(glob.glob("data/sealed/TS2_for_quantum/ts2_*metric_components_t*.txt"))
for f in files:
    comps = {}
    for line in open(f):
        if line.startswith("#") or " = " not in line:
            continue
        k, v = line.split(" = ", 1)
        comps[k.strip()] = sp.sympify(v.strip(), locals=O.SREPR_NAMES)     # exactly load_package's parser
    for k in sorted(comps):
        h.update(f.encode()); h.update(k.encode()); h.update(sp.srepr(comps[k]).encode())
print(sys.version.split()[0], len(files), h.hexdigest())
