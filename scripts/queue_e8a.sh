#!/bin/sh
cd /home/arya/swarm_hack
. .secrets/adaption.env; export ADAPTION_API_KEY
export SWARM_RPM=220 SWARM_PMC=40
.venv/bin/python scripts/13_attacker.py dev1 > outputs/logs/e8_dev1a.log 2>&1
.venv/bin/python scripts/13_attacker.py gen2 > outputs/logs/e8_gen2.log 2>&1
.venv/bin/python scripts/13_attacker.py dev2 > outputs/logs/e8_dev2.log 2>&1
.venv/bin/python scripts/13_attacker.py select > outputs/logs/e8_select.log 2>&1
