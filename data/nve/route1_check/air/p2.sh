#!/bin/zsh
# Pilot P2 (seal: data/nve/route1_check/P2_SEAL.md): spins 3/10 and 4/5 at k_c = 21/20, one process at a time.
# v2 (after T1 on 7f96efc failed; see the seal's amendment): the proof stage is v4's, as registered.
# 1. floats inputs with the 50-digit engine under .venv (Python 3.14.10 + numba: the engine's closure; the committed floats
#    files were made the same way, under the repo venv's 3.14). 2. v4 proof stage under .venv313 (3.13.18).
# Refuses to start if any input or output of P2 exists.
cd ~/GitHub/ansatz-air || exit 1
E=data/nve/eps
for f in $E/route1_floats_3_10.json $E/route1_floats_4_5.json $E/route1_seg_v4_3_10_*(N) $E/route1_seg_v4_4_5_*(N) $E/route1_seg_M_v4_3_10_*(N) $E/route1_seg_M_v4_4_5_*(N); do
  [[ -e $f ]] && { echo "REFUSE: $f exists"; exit 1; }
done
for sp in "3/10 1.1492" "4/5 1.3382"; do
  s=${sp% *}; r=${sp#* }; t=${s/\//_}
  echo "=== P2 floats spin $s R0 $r $(date '+%F %T') $(.venv/bin/python -V)"
  NVE_SPIN=$s R1_R0=$r R1_FLOATS=route1_floats_$t.json .venv/bin/python -I -u scripts/_nve_route1_floats.py 21/20 || exit 1
  echo "=== P2 prove spin $s $(date '+%F %T') $(.venv313/bin/python -V)"
  NVE_SPIN=$s R1_R0=$r .venv313/bin/python -I -u scripts/_nve_route1_segment_v4.py || exit 1
done
echo "=== P2_DONE $(date '+%F %T')"
