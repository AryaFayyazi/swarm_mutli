#!/bin/sh
# Unattended round-2/3 chain (one process owns the API key at a time). Throughput orchestration only.
cd /home/arya/swarm_hack
set -a; . .secrets/adaption.env; set +a
export SWARM_PMC=40 SWARM_RPM=55 SWARM_PAUSE=30
PY=.venv/bin/python
while [ "$(date +%H%M)" -lt 1630 ]; do sleep 30; done
pkill -f "[1]0_confirm.py e9"
sleep 5
$PY scripts/14_filter_attacker.py dev1 > outputs/e11_dev1.log 2>&1
$PY scripts/14_filter_attacker.py gen2 > outputs/e11_gen2.log 2>&1
$PY scripts/14_filter_attacker.py dev2 > outputs/e11_dev2.log 2>&1
$PY scripts/14_filter_attacker.py select > outputs/e11_select.log 2>&1
LIMIT_SCEN=20 $PY scripts/10_confirm.py e11 > outputs/e11.log 2>&1
LIMIT_SCEN=20 $PY scripts/10_confirm.py e12 > outputs/e12.log 2>&1
if [ "$(date +%H%M)" -lt 2115 ]; then
  LIMIT_SCEN=20 $PY scripts/10_confirm.py e10 > outputs/e10.log 2>&1
  INFILES=e9.jsonl,e10.jsonl SEED=5501 SELECT=round2 OUTNAME=r2mon.jsonl JUDGES=glm-53-flash LEVELS=L0,L1,L3 JNS=1 SKIP_SELF=1 JUDGE_MAXOUT=6000 $PY scripts/11_monitor.py > outputs/r2mon.log 2>&1
fi
echo CHAIN_DONE > outputs/chain_done.txt
