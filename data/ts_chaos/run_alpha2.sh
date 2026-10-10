#!/bin/zsh
cd "${0:A:h}/../.." || exit 2
exec < /dev/null
P=.venv/bin/python
$P -u scripts/_ts_chaos_alpha.py 2 1500 --ts ts35 --E 0.95 --L -5.333333333333334 --kerr kerr35 --tag p35 >> data/ts_chaos/alpha2.out 2>&1
$P -u scripts/_ts_chaos_alpha.py 2 1500 --ts ts45 --E 0.97 --L 5.875 --kerr kerr45 --tag p45b >> data/ts_chaos/alpha2.out 2>&1
$P -u scripts/_ts_chaos_alpha.py 2 1500 --ts ts45 --E 0.97 --L 5.125 --kerr kerr45 --nsec 600 --tag p45_n600 >> data/ts_chaos/alpha2.out 2>&1
echo "ALL DONE $(date)" >> data/ts_chaos/alpha2.out
