cd /Users/sumit/Github/conjecture_machine
L=data/kt_boxnight.log
say(){ echo "$(date '+%m-%d %H:%M:%S')  $*" >> "$L"; }
say "CONFIRM 2 RETRY: box 437 after scoping the cross-check to the box it was measured on."
.venv/bin/python scripts/_kt_exact.py --box 18 22 --points 413 \
  --matrix data/kt_zvd2_d2_r4.pkl.modp.p413.npz > data/kt_exact_d2_r4_b437.out 2>&1
c=$(grep -o "EXACT solution dimension *: [0-9]*" data/kt_exact_d2_r4_b437.out | tail -1 | awk '{print $NF}')
d=$(grep -o "IRREDUCIBLE.*: [0-9]*" data/kt_exact_d2_r4_b437.out | tail -1 | awk '{print $NF}')
r=$(grep -o "reducible span dimension *: [0-9]*" data/kt_exact_d2_r4_b437.out | tail -1 | awk '{print $NF}')
say "  box 437 -> exact dim ${c:-NONE}, reducible ${r:-NONE}, irreducible ${d:-NONE}  (sampled 24)"
say "REGRESSION: box 357 prime 1 re-run, to prove the cross-check edit did not break the working path."
.venv/bin/python scripts/_kt_exact.py --box 16 20 --points 338 \
  --matrix data/kt_zvd2_d2_r4.pkl.modp.p338.npz > data/kt_exact_d2_r4_b357_regress.out 2>&1
g=$(grep -o "EXACT solution dimension *: [0-9]*" data/kt_exact_d2_r4_b357_regress.out | tail -1 | awk '{print $NF}')
x=$(grep -c "cross-check: vectors 0,2 zero" data/kt_exact_d2_r4_b357_regress.out)
say "  regression box 357 -> exact dim ${g:-NONE} (expect 9), cross-check line present: $x (expect 1)"
if [ "${c:-x}" = "9" ] && [ "${g:-x}" = "9" ] && [ "$x" = "1" ]; then
  say "  CONFIRMED: exact dim 9 at two primes AND two boxes; cross-check intact. Sampled 14/24 was slack."
else
  say "  NOT CONFIRMED: b437=${c:-NONE} regress=${g:-NONE} xcheck=$x -- read the runs before believing anything."
fi
say "CONFIRM2 DONE"
