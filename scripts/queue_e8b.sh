#!/bin/sh
cd /home/arya/swarm_hack
. .secrets/adaption.env; export ADAPTION_API_KEY
export SWARM_RPM=250 SWARM_PMC=40
.venv/bin/python scripts/13_attacker.py gen2 > outputs/logs/e8_gen2b.log 2>&1
.venv/bin/python scripts/13_attacker.py dev2 > outputs/logs/e8_dev2b.log 2>&1
.venv/bin/python scripts/13_attacker.py select > outputs/logs/e8_selectb.log 2>&1
