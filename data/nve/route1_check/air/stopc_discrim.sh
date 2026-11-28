#!/bin/zsh
# Stop-(c) discriminator at spin 9/10 (seal: STOPC_DISCRIM_SEAL.md, committed with this runner before launch).
# Floats at k_c 5/2, then two v6 PROVE stages in parallel (no verdict): A half-width 1/20, B half-width 1/40, with the
# production driver's settings (rho = 4, mode F, tol rel). Run under stopc_job.sh (pause-only guard, nice 10).
cd /Users/sumit/Github/conjecture_machine-check || exit 1
L=data/nve/route1_check/stopc_discrim
P13=/Users/sumit/Github/conjecture_machine-check/.venv313/bin/python
P14=/Users/sumit/Github/conjecture_machine/.venv/bin/python
export NVE_SPIN=9/10 R1_R0=1.2639 R1_KC=5/2 R1_FLOATS=route1_floats_stopc_9_10.json R1_RHOS=4 R1_MODE=F R1_TOLMODE=rel
echo "=== floats $(date '+%F %T')"
${=P14} -I -u scripts/_nve_route1_floats.py 5/2 || exit 1
echo "=== prove A (half 1/20) and B (half 1/40) start $(date '+%F %T')"
R1_HALF=1/20 ${=P13} -I -u scripts/_nve_route1_segment_v6.py prove > $L/prove_A.out 2>&1 &
pa=$!
R1_HALF=1/40 ${=P13} -I -u scripts/_nve_route1_segment_v6.py prove > $L/prove_B.out 2>&1 &
pb=$!
echo "prove A pid $pa, prove B pid $pb"
wait $pa; ra=$?
echo "=== prove A rc $ra $(date '+%F %T')"
wait $pb; rb=$?
echo "=== prove B rc $rb $(date '+%F %T')"
echo "=== STOPC_DISCRIM_DONE"
