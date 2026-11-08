#!/bin/sh
cd /home/arya/swarm_hack
. .secrets/adaption.env; export ADAPTION_API_KEY
until grep -q "^DONE e4" outputs/logs/e4.log 2>/dev/null; do sleep 60; done
.venv/bin/python scripts/11_monitor.py > outputs/logs/e2.log 2>&1
