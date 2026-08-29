cd /Users/sumit/Github/conjecture_machine
L=data/kt_boxnight.log
say(){ echo "$(date '+%m-%d %H:%M:%S')  $*" >> "$L"; }
say "CONFIRM 1: exact dimension at box 357, SECOND prime 2147483629. One prime can vanish falsely."
.venv/bin/python scripts/_kt_exact.py --box 16 20 --points 338 --prime 1 \
  --matrix data/kt_zvd2_d2_r4.pkl.modp.p338.npz > data/kt_exact_d2_r4_b357_p2.out 2>&1
a=$(grep -o "IRREDUCIBLE.*: [0-9]*" data/kt_exact_d2_r4_b357_p2.out | tail -1 | awk '{print $NF}')
b=$(grep -o "EXACT solution dimension *: [0-9]*" data/kt_exact_d2_r4_b357_p2.out | tail -1 | awk '{print $NF}')
say "  box 357 prime 2 -> exact dim ${b:-NONE}, irreducible ${a:-NONE}  (prime 1 gave 9 and 0)"
say "CONFIRM 2: exact dimension at box 437, where the SAMPLED count was 24. Tests box-flatness of the EXACT number."
.venv/bin/python scripts/_kt_exact.py --box 18 22 --points 413 \
  --matrix data/kt_zvd2_d2_r4.pkl.modp.p413.npz > data/kt_exact_d2_r4_b437.out 2>&1
c=$(grep -o "EXACT solution dimension *: [0-9]*" data/kt_exact_d2_r4_b437.out | tail -1 | awk '{print $NF}')
d=$(grep -o "IRREDUCIBLE.*: [0-9]*" data/kt_exact_d2_r4_b437.out | tail -1 | awk '{print $NF}')
say "  box 437 -> exact dim ${c:-NONE}, irreducible ${d:-NONE}  (sampled there was 24)"
if [ "${b:-x}" = "9" ] && [ "${c:-x}" = "9" ]; then
  say "  CONFIRMED: exact dimension 9 at two primes and two boxes; sampled 14/24 was slack."
else
  say "  NOT CONFIRMED: prime2=${b:-NONE} box437=${c:-NONE}; the single-prime 9 does not stand alone."
fi
say "CONFIRM DONE"
