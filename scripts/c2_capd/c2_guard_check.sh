#!/bin/zsh
# Positive check of the compile-time guard (Bridge ruling, 2026-11-28): every excluded type must FAIL to compile, and
# fail ON THE GUARD (the "C2 GUARD" static_assert message), not on some incidental error; the MPFR-interval build must
# succeed. Exit 0 only if all of that holds.
cd "$(dirname "$0")"
ok=1
for plant in IMAP DMAP LDMAP MPMAP; do
  log=build/guard_$plant.log
  if OUT=build/plant_$plant ./c2_build.sh -DC2_PLANT_$plant > $log 2>&1; then
    echo "plant $plant: COMPILED  -> guard FAILED"; ok=0
  elif grep -q "C2 GUARD" $log; then
    echo "plant $plant: refused by the guard ($(grep -c 'C2 GUARD' $log) guard diagnostics):"
    grep 'C2 GUARD' $log | sed 's|^.*c2_driver.cpp|    c2_driver.cpp|' 
  else
    echo "plant $plant: failed to compile but NOT on the guard -> check FAILED"; ok=0
  fi
done
if OUT=build/c2_driver ./c2_build.sh > build/guard_MPI.log 2>&1 && ! grep -q "C2 GUARD" build/guard_MPI.log; then
  echo "MPFR intervals (capd::MpIMap): compiles"
else
  echo "MPFR intervals: did NOT compile -> check FAILED"; ok=0
fi
[[ $ok == 1 ]] && echo "guard check: PASS" || echo "guard check: FAIL"
[[ $ok == 1 ]]
