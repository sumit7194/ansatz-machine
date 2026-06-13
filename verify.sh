#!/bin/bash
# The local gate: every battery, both directions (knowns pass, sabotage
# fails), one verdict. Run before any "done" claim.
cd "$(dirname "$0")" || exit 1
PY=.venv/bin/python

declare -a NAMES CMDS
NAMES+=("01 verifier (+Kerr)");   CMDS+=("scripts/01_verifier.py --kerr")
NAMES+=("02 fingerprints");       CMDS+=("scripts/02_fingerprints.py")
NAMES+=("03 rediscovery");        CMDS+=("scripts/03_rediscover.py")
NAMES+=("04 campaign");           CMDS+=("scripts/04_campaign.py")
[ -f scripts/05_generalize.py ] && { NAMES+=("05 catalog growth"); CMDS+=("scripts/05_generalize.py"); }
[ -f scripts/06_two_function.py ] && { NAMES+=("06 two-function hall"); CMDS+=("scripts/06_two_function.py --quick"); }
[ -f scripts/07_expedition.py ] && { NAMES+=("07 expedition"); CMDS+=("scripts/07_expedition.py"); }
[ -f scripts/08_stationary.py ] && { NAMES+=("08 stationary hall"); CMDS+=("scripts/08_stationary.py --quick"); }
[ -f scripts/10_edgb_reduce.py ] && { NAMES+=("10 EdGB E0 (vs Kanti)"); CMDS+=("scripts/10_edgb_reduce.py"); }
[ -f scripts/21_rot_fingerprint.py ] && { NAMES+=("21 rotating fingerprint"); CMDS+=("scripts/21_rot_fingerprint.py"); }
[ -f scripts/22_rot_fit.py ] && { NAMES+=("22 rotating fit (banked-formula verify)"); CMDS+=("scripts/22_rot_fit.py"); }
[ -f scripts/sealed_holdout.py ] && { NAMES+=("SH sealed-holdout guard"); CMDS+=("scripts/sealed_holdout.py"); }

fail=0
for i in "${!NAMES[@]}"; do
    start=$(date +%s)
    if $PY ${CMDS[$i]} >/tmp/cm_verify_$i.log 2>&1; then
        echo "  PASS  ${NAMES[$i]}  ($(( $(date +%s) - start ))s)"
    else
        echo "  FAIL  ${NAMES[$i]}  ($(( $(date +%s) - start ))s)  — tail of log:"
        tail -5 /tmp/cm_verify_$i.log | sed 's/^/        /'
        fail=1
    fi
done
echo
if [ $fail -eq 0 ]; then echo "VERIFY: ALL GREEN ✅"; else echo "VERIFY: FAILURES ❌"; fi
exit $fail
