#!/bin/sh
cd /home/arya/swarm_hack
. .secrets/adaption.env; export ADAPTION_API_KEY
SWARM_PMC=40 .venv/bin/python scripts/13_attacker.py conf > outputs/logs/e8_conf.log 2>&1
