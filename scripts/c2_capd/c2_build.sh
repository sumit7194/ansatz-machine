#!/bin/zsh
# Build the C2 driver against our own CAPD (/Users/sumit/Github/capd-ansatz/install; commit recorded in C2_REGISTRATION.md).
# Extra arguments are passed to the compiler (the guard check uses -DC2_PLANT_...).  Output: build/c2_driver[suffix]
set -e
cd "$(dirname "$0")"
CAPD=/Users/sumit/Github/capd-ansatz/install
OUT=${OUT:-build/c2_driver}
mkdir -p build
c++ -std=c++17 $($CAPD/bin/capd-config --cflags) -I/opt/homebrew/include "$@" c2_driver.cpp -o "$OUT" \
    $($CAPD/bin/capd-config --libs) -L/opt/homebrew/lib -lmpfr -lgmp
