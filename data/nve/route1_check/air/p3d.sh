#!/bin/zsh
# P3, the last stage, alone (the Bridge's go, 2026-11-26, after P3_RESULT 610eca5). p3c.sh stopped at spin 9/10 k_c 3
# (rc 1, OverflowError in the n formula), so its last stage, spin 9/10 k_c 39/10, never ran. This runs exactly that
# stage: a verbatim subset of p3c.sh, same environment and command line, nothing else changed.
# Graded against the seal addendum's prediction (the same Laurent RuntimeError as 3/5, P = 95%).
# Refuses unless the 9/10 floats file is byte-identical to what p3.sh wrote, and if any 9/10 k_c 39/10 output exists.
cd ~/GitHub/ansatz-air || exit 1
E=data/nve/eps
echo "ab682ceac167175cbc11f662431cbb719f775788e55e435ffc169c32e744663d  $E/route1_floats_p3_9_10.json" | shasum -a 256 -c || exit 1
for f in $E/*9_10*_kc39o10*(N); do echo "REFUSE: $f exists"; exit 1; done
s=9/10; r=1.2639; t=9_10
for kc in 39/10; do
  echo "=== P3 prove spin $s k_c $kc $(date '+%F %T') $(.venv313/bin/python -V)"
  NVE_SPIN=$s R1_R0=$r R1_RHOS=4 R1_KC=$kc R1_HALF=1/20 R1_FLOATS=route1_floats_p3_$t.json \
    .venv313/bin/python -I -u scripts/_nve_route1_segment_v5.py prove || exit 1
done
echo "=== P3D_DONE $(date '+%F %T')"
