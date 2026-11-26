#!/bin/sh
# §3(b): the 50-digit engine at every node of both certified segments (25 at spin 3/5, 19 at spin 9/10).
cd /Users/sumit/Github/conjecture_machine-check || exit 1
PY=/Users/sumit/Github/conjecture_machine/.venv/bin/python
NVE_SPIN=3/5 R1_R0=1.35 NODES=data/nve/eps/route1_seg_nodes_arb.jsonl FLOATS=data/nve/eps/route1_floats.json \
    nice -n 15 "$PY" -u scripts/_nve_route1_engine_nodes.py || exit 1
NVE_SPIN=9/10 R1_R0=1.2639 NODES=data/nve/eps/route1_seg_nodes_arb_9_10_v4cert.jsonl FLOATS=data/nve/eps/route1_floats_9_10.json \
    nice -n 15 "$PY" -u scripts/_nve_route1_engine_nodes.py || exit 1
echo ENGINE_DONE
