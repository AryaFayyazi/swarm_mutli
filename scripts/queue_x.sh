#!/bin/sh
cd /home/arya/swarm_hack
. .secrets/adaption.env; export ADAPTION_API_KEY
JUDGES=glm-53-flash LEVELS=L0,L3 JNS=1 JUDGE_MAXOUT=6000 OUTNAME=e2x.jsonl SKIP_SELF=1 .venv/bin/python scripts/11_monitor.py > outputs/logs/e2x.log 2>&1
SWARM_PMC=40 .venv/bin/python scripts/13_attacker.py dev1 > outputs/logs/e8_dev1.log 2>&1
