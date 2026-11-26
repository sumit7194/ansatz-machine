#!/bin/zsh
# P3 continuation (seal: P3_SEAL.md at 4a7bb55; runner p3.sh at 76f2715 stopped at spin 3/5 k_c 39/10, rc 1,
# RuntimeError "Laurent tail bound: non-finite on |omega| = 0.9/a" in V.laurent(k_c, deriv=True)).
# Per the Bridge's ruling: skips ONLY that stage, changes nothing else. Already done and not rerun: both floats inputs,
# spin 3/5 at k_c 1/2, 2, 3. This runs exactly p3.sh's remaining stages: spin 9/10 at k_c 1/2, 2, 3, 39/10, with
# p3.sh's environment and command line unchanged.
# Refuses unless the 9/10 floats file is byte-identical to what p3.sh wrote (sha256 below), and if any 9/10 P3 output exists.
cd ~/GitHub/ansatz-air || exit 1
E=data/nve/eps
echo "ab682ceac167175cbc11f662431cbb719f775788e55e435ffc169c32e744663d  $E/route1_floats_p3_9_10.json" | shasum -a 256 -c || exit 1
for f in $E/*9_10*_kc*(N); do echo "REFUSE: $f exists"; exit 1; done
s=9/10; r=1.2639; t=9_10
for kc in 1/2 2 3 39/10; do
  echo "=== P3 prove spin $s k_c $kc $(date '+%F %T') $(.venv313/bin/python -V)"
  NVE_SPIN=$s R1_R0=$r R1_RHOS=4 R1_KC=$kc R1_HALF=1/20 R1_FLOATS=route1_floats_p3_$t.json \
    .venv313/bin/python -I -u scripts/_nve_route1_segment_v5.py prove || exit 1
done
echo "=== P3C_DONE $(date '+%F %T')"
