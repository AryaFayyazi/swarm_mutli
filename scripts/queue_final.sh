#!/bin/sh
# resume E2 with higher concurrency (throughput only), then E7, then the exploratory stance labels
cd /home/arya/swarm_hack
. .secrets/adaption.env; export ADAPTION_API_KEY
.venv/bin/python scripts/11_monitor.py > outputs/logs/e2b.log 2>&1
.venv/bin/python scripts/10_confirm.py e7 > outputs/logs/e7.log 2>&1
.venv/bin/python scripts/12_brief_stance.py > outputs/logs/stance.log 2>&1
