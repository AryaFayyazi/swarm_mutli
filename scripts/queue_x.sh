#!/bin/sh
cd /home/arya/swarm_hack
. .secrets/adaption.env; export ADAPTION_API_KEY
JUDGES=glm-5.2 OUTNAME=e2x.jsonl SKIP_SELF=1 .venv/bin/python scripts/11_monitor.py > outputs/logs/e2x.log 2>&1
