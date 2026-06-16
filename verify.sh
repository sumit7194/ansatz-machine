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
[ -f scripts/24_abstractor.py ] && { NAMES+=("24 abstractor (recovers Tangherlini law)"); CMDS+=("scripts/24_abstractor.py"); }
[ -f scripts/26_information_meter.py ] && { NAMES+=("26 information meter (hair counter)"); CMDS+=("scripts/26_information_meter.py"); }
[ -f scripts/27_scalar.py ] && { NAMES+=("27 scalar source (sanity)"); CMDS+=("scripts/27_scalar.py"); }
[ -f scripts/28_maxwell.py ] && { NAMES+=("28 maxwell source (RN)"); CMDS+=("scripts/28_maxwell.py"); }
[ -f scripts/29_matter_meter.py ] && { NAMES+=("29 matter meter (RN hair=2)"); CMDS+=("scripts/29_matter_meter.py"); }
[ -f scripts/30_dilaton.py ] && { NAMES+=("30 dilaton (secondary hair)"); CMDS+=("scripts/30_dilaton.py"); }
[ -f scripts/31_matter_hunt.py ] && { NAMES+=("31 matter discovery (RN)"); CMDS+=("scripts/31_matter_hunt.py"); }
[ -f scripts/32_no_hair.py ] && { NAMES+=("32 no-hair (proven + searched)"); CMDS+=("scripts/32_no_hair.py"); }
[ -f scripts/33_no_hair_ladder.py ] && { NAMES+=("33 no-hair ladder (structural, any n,Λ)"); CMDS+=("scripts/33_no_hair_ladder.py"); }
[ -f scripts/34_hair_criterion.py ] && { NAMES+=("34 hair criterion (no-hair⇔angular source)"); CMDS+=("scripts/34_hair_criterion.py"); }
[ -f scripts/35_thermodynamics.py ] && { NAMES+=("35 thermodynamics (recovers S=A/4, first law)"); CMDS+=("scripts/35_thermodynamics.py"); }
[ -f scripts/36_energy_conditions.py ] && { NAMES+=("36 energy conditions (physicality classifier)"); CMDS+=("scripts/36_energy_conditions.py"); }
[ -f scripts/37_cosmology.py ] && { NAMES+=("37 cosmology (Friedmann + expansion law)"); CMDS+=("scripts/37_cosmology.py"); }
[ -f scripts/38_exotic_spacetimes.py ] && { NAMES+=("38 exotic spacetimes (wormhole/warp need exotic matter)"); CMDS+=("scripts/38_exotic_spacetimes.py"); }
[ -f scripts/40_analyzer.py ] && { NAMES+=("40 general analyzer (one tool, the whole zoo)"); CMDS+=("scripts/40_analyzer.py"); }
[ -f scripts/41_atlas.py ] && { NAMES+=("41 atlas (12 spacetimes incl. Kerr & Gödel)"); CMDS+=("scripts/41_atlas.py"); }
[ -f scripts/42_causal_structure.py ] && { NAMES+=("42 causal structure (spacelike vs timelike singularity)"); CMDS+=("scripts/42_causal_structure.py"); }
[ -f scripts/43_discover.py ] && { NAMES+=("43 discovery (invents to spec: Schwarzschild + survivable hole)"); CMDS+=("scripts/43_discover.py --quick"); }
[ -f scripts/44_discover_rotating.py ] && { NAMES+=("44 rotating discovery (rediscovers Kerr + Kerr-Newman)"); CMDS+=("scripts/44_discover_rotating.py --quick"); }
[ -f scripts/45_observables.py ] && { NAMES+=("45 observables (photon sphere + EHT shadow)"); CMDS+=("scripts/45_observables.py"); }

fail=0
GATE="$(dirname "$0")/gate.log"; : > "$GATE"   # also written here so the dashboard (reads ROOT/gate.log) stays current
for i in "${!NAMES[@]}"; do
    start=$(date +%s)
    if $PY ${CMDS[$i]} >/tmp/cm_verify_$i.log 2>&1; then
        line="  PASS  ${NAMES[$i]}  ($(( $(date +%s) - start ))s)"
        echo "$line"; echo "$line" >> "$GATE"
    else
        line="  FAIL  ${NAMES[$i]}  ($(( $(date +%s) - start ))s)"
        echo "$line  — tail of log:"; echo "$line" >> "$GATE"
        tail -5 /tmp/cm_verify_$i.log | sed 's/^/        /'
        fail=1
    fi
done
echo
if [ $fail -eq 0 ]; then v="VERIFY: ALL GREEN ✅"; else v="VERIFY: FAILURES ❌"; fi
echo "$v"; { echo; echo "$v"; echo "GATE_EXIT=$fail"; } >> "$GATE"
exit $fail
