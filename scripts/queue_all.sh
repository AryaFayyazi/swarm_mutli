#!/bin/sh
# one process at a time (API limit is per user): waits for the running E1 -> E3 chain, then E3b, E4, E5, E6, E2
cd /home/arya/swarm_hack
. .secrets/adaption.env; export ADAPTION_API_KEY
until grep -q "^DONE e3" outputs/logs/e3.log 2>/dev/null; do sleep 60; done
for x in e3b e4 e5 e6; do .venv/bin/python scripts/10_confirm.py $x > outputs/logs/$x.log 2>&1; done
.venv/bin/python scripts/11_monitor.py > outputs/logs/e2.log 2>&1
cd /home/arya/swarm_hack; .venv/bin/python scripts/10_confirm.py e7 > outputs/logs/e7.log 2>&1
