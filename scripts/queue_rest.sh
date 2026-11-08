#!/bin/sh
# waits for E3 to finish (the E1 -> E3 chain is already running), then runs E3b and E4 with the same key
cd /home/arya/swarm_hack
. .secrets/adaption.env; export ADAPTION_API_KEY
until grep -q "^DONE e3" outputs/logs/e3.log 2>/dev/null; do sleep 60; done
.venv/bin/python scripts/10_confirm.py e3b > outputs/logs/e3b.log 2>&1
.venv/bin/python scripts/10_confirm.py e4 > outputs/logs/e4.log 2>&1
