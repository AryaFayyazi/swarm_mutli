#!/bin/sh
cd /home/arya/swarm_hack
. .secrets/adaption.env; export ADAPTION_API_KEY
SWARM_PMC=40 .venv/bin/python scripts/10_confirm.py e7 > outputs/logs/e7b.log 2>&1
.venv/bin/python scripts/12_brief_stance.py > outputs/logs/stance.log 2>&1
