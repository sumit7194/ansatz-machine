cd /Users/sumit/Github/conjecture_machine
L=data/kt_boxnight.log
say(){ echo "$(date '+%m-%d %H:%M:%S')  $*" >> "$L"; }
while pgrep -f "_kt_zv_den2.py 2 4" >/dev/null; do sleep 60; done

# The box was swept and the points were not. 338 points came from a ROW-COUNT heuristic, which is
# the same kind of unexamined default that produced the 34. If 14 is point-limited it will fall
# when points rise, exactly as 34 fell when the box shrank. Box held FIXED at 357 so only one
# variable moves.
say "PHASE 4: delta=2 rank 4, box FIXED at 357, POINTS 338 -> 500. Does 14 hold?"
s=$(date +%s)
.venv/bin/python scripts/_kt_zv_den2.py 2 4 --modp --box 16 20 --points 500 > data/kt_zvd2_d2_r4_b357_p500.out 2>&1
d=$(grep -o "DIMENSION [0-9]*" data/kt_zvd2_d2_r4_b357_p500.out | tail -1 | awk '{print $2}')
say "  box 357, 500 points -> dimension ${d:-NONE}  ($(( $(date +%s) - s ))s)"
case "${d:-x}" in
  14) say "  14 HOLDS at 1.5x the points. Not point-limited. 14-9=5 remains unexplained and needs the exact test." ;;
  9)  say "  FELL TO 9 with more points. The 14 was point-limited; prediction holds and the rung closes." ;;
  *)  say "  dimension ${d:-NONE} -- neither 14 nor 9, read the run" ;;
esac
say "PHASE 4 DONE"
