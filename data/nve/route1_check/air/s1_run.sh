#!/bin/zsh
# S1 split discriminator (S1_SPLIT_SEAL.md): prove-only runs for one region. usage: s1_run.sh A|B
cd /Users/sumit/Github/conjecture_machine-check || exit 1
P13=/Users/sumit/Github/conjecture_machine-check/.venv313/bin/python
P14=/Users/sumit/Github/conjecture_machine/.venv/bin/python
REG=$1
export NVE_SPIN=3/5 R1_R0=1.35 R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel
if [ $REG = B ]; then
  FL=route1_floats_s1B_3_5.json; SCRIPT=scripts/_nve_route1_segment_v7B.py
  D1=(33/8 167/40); D2=(329/80 331/80 333/80 335/80)
  echo "=== floats B $(date '+%F %T')"; R1_FLOATS=$FL ${=P14} -I -u scripts/_nve_v7_floatsB.py $D1 $D2 || exit 1
else
  FL=route1_floats_s1A_3_5.json; SCRIPT=scripts/_nve_route1_segment_v7.py
  D1=(157/40 159/40); D2=(313/80 315/80 317/80 319/80)
  echo "=== floats A $(date '+%F %T')"; R1_FLOATS=$FL ${=P14} -I -u scripts/_nve_route1_floats.py $D1 $D2 || exit 1
fi
echo "=== control $(date '+%F %T')"
PICTURE=$REG R1_KC=$D2[1] R1_HALF=1/80 R1_FLOATS=$FL ${=P13} -I -u scripts/_nve_v7_s1_control.py; echo "control rc $?"
for kc in $D1; do echo "=== prove depth 1 k_c $kc $(date '+%F %T')"; R1_KC=$kc R1_HALF=1/40 R1_FLOATS=$FL ${=P13} -I -u $SCRIPT prove; echo "prove rc $?"; done
for kc in $D2; do echo "=== prove depth 2 k_c $kc $(date '+%F %T')"; R1_KC=$kc R1_HALF=1/80 R1_FLOATS=$FL ${=P13} -I -u $SCRIPT prove; echo "prove rc $?"; done
echo "=== S1_DONE $REG $(date '+%F %T')"
