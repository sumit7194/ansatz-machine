#!/bin/zsh
# Pilot P3 (seal: data/nve/route1_check/P3_SEAL.md, 4a7bb55): rho = 4 at k_c 1/2, 2, 3, 39/10, half 1/20, spins 3/5 and 9/10.
# Floats inputs with the 50-digit engine under .venv (3.14 + numba), into P3's own files; then v5.1 + B1 proof stages
# under .venv313 (3.13.18). A rejected row (expected at 39/10) is a result, not an error: the stage still exits 0.
# Refuses if any P3 input or output exists.
cd ~/GitHub/ansatz-air || exit 1
E=data/nve/eps
for f in $E/route1_floats_p3_*(N) $E/*_kc*(N); do echo "REFUSE: $f exists"; exit 1; done
for sp in "3/5 1.35" "9/10 1.2639"; do
  s=${sp% *}; r=${sp#* }; t=${s/\//_}
  echo "=== P3 floats spin $s $(date '+%F %T') $(.venv/bin/python -V)"
  NVE_SPIN=$s R1_R0=$r R1_FLOATS=route1_floats_p3_$t.json .venv/bin/python -I -u scripts/_nve_route1_floats.py 1/2 2 3 39/10 || exit 1
done
for sp in "3/5 1.35" "9/10 1.2639"; do
  s=${sp% *}; r=${sp#* }; t=${s/\//_}
  for kc in 1/2 2 3 39/10; do
    echo "=== P3 prove spin $s k_c $kc $(date '+%F %T') $(.venv313/bin/python -V)"
    NVE_SPIN=$s R1_R0=$r R1_RHOS=4 R1_KC=$kc R1_HALF=1/20 R1_FLOATS=route1_floats_p3_$t.json \
      .venv313/bin/python -I -u scripts/_nve_route1_segment_v5.py prove || exit 1
  done
done
echo "=== P3_DONE $(date '+%F %T')"
