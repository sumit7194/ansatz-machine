#!/bin/zsh
cd "${0:A:h}/../.." || exit 2
exec < /dev/null
.venv/bin/python -u scripts/_ts_chaos_alpha.py 2 1500 --ts ts35 --E 0.95 --L -5.333333333333334 --kerr kerr35 --minw-factor 10 --tag p35w >> data/ts_chaos/alpha3.out 2>&1
echo "ALL DONE $(date)" >> data/ts_chaos/alpha3.out
