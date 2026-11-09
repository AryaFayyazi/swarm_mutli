#!/bin/sh
# E13 after E12 (one process owns the API key at a time). Throughput orchestration only.
cd /home/arya/swarm_hack
set -a; . .secrets/adaption.env; set +a
export SWARM_PMC=40 SWARM_RPM=55 SWARM_PAUSE=30
PY=.venv/bin/python
while pgrep -f "[1]0_confirm.py e12" >/dev/null; do sleep 20; done
LIMIT_SCEN=20 $PY scripts/10_confirm.py e13 > outputs/e13.log 2>&1
echo CHAIN3_DONE > outputs/chain3_done.txt
