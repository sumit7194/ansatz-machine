#!/bin/zsh
# C2-M production lane (C2_PROD_REGISTRATION.md): every segment of lane $1 in C2_PROD_MANIFEST.txt, in order, one at a
# time, each with its own log v7/c2m_<LABEL>.log. A segment that does not certify is recorded and the lane goes on (each
# certificate stands alone). Run under air/v7_job.sh (pause-only guard, nice 10): two lanes = 4 cover cores.
#   usage: c2m_prod.sh A|B
cd /Users/sumit/Github/conjecture_machine-b2fix || exit 1
LANE=$1
while read ln lbl kc half; do
  [[ $ln == $LANE ]] || continue
  echo "$(date '+%F %T') lane $LANE: start $lbl ($kc, half $half)"
  data/nve/route1_check/air/c2m_segment.sh $lbl $kc $half < /dev/null >> data/nve/route1_check/v7/c2m_$lbl.log 2>&1
  echo "$(date '+%F %T') lane $LANE: $lbl exited rc $?"
done < ${C2_MANIFEST:-data/nve/route1_check/C2_PROD_MANIFEST.txt}
echo "$(date '+%F %T') lane $LANE: C2M_PROD_LANE_DONE"
