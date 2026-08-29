cd /Users/sumit/Github/conjecture_machine
L=data/kt_boxnight.log
say(){ echo "$(date '+%m-%d %H:%M:%S')  $*" >> "$L"; }

say "PHASE 2 RESUMED after power cut -- 338/338 points banked, rank step only"
s=$(date +%s)
.venv/bin/python scripts/_kt_zv_den2.py 2 4 --modp --box 16 20 --points 338 > data/kt_zvd2_d2_r4_b357.out 2>&1
d357=$(grep -o "DIMENSION [0-9]*" data/kt_zvd2_d2_r4_b357.out | tail -1 | awk '{print $2}')
say "  delta=2 rank 4, box 357 funcs -> dimension ${d357:-NONE}  ($(( $(date +%s) - s ))s)"

say "PHASE 3: delta=2 rank 4 at MARGIN-2 box x<=18,y<=22 (437 funcs) -- the flatness partner"
s=$(date +%s)
.venv/bin/python scripts/_kt_zv_den2.py 2 4 --modp --box 18 22 --points 413 > data/kt_zvd2_d2_r4_b437.out 2>&1
d437=$(grep -o "DIMENSION [0-9]*" data/kt_zvd2_d2_r4_b437.out | tail -1 | awk '{print $2}')
say "  delta=2 rank 4, box 437 funcs -> dimension ${d437:-NONE}  ($(( $(date +%s) - s ))s)"

say "  FLATNESS: 357 -> ${d357:-NONE}, 437 -> ${d437:-NONE}, 525 -> 34"
if [ -n "$d357" ] && [ "$d357" = "$d437" ]; then
  if [ "$d357" = "9" ]; then say "  FLAT AT 9 across 357 and 437. The 34 at 525 is box inflation, not the spacetime."
  else say "  FLAT AT $d357 across 357 and 437 but predicted 9 -- flat AND wrong is a different finding"; fi
else
  say "  NOT FLAT: 357 and 437 disagree. Onset lies between them; neither is trustworthy alone."
fi
say "ALL PHASES DONE"
