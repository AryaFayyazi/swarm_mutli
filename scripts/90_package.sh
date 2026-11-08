#!/bin/sh
# Builds the two upload archives (no secrets, no virtualenv). Run from the repo root after the final report build.
cd /home/arya/swarm_hack
rm -rf /tmp/swarm_pkg && mkdir -p /tmp/swarm_pkg
zip -r -q /tmp/swarm_pkg/swarm_hack_code.zip . -x ".secrets/*" ".venv/*" "*.env" "outputs/raw/*" "__pycache__/*" "*/__pycache__/*" "paper/_*" "template/x/*" "outputs/dev_dry/*" ".pytest_cache/*"
tar -czf /tmp/swarm_pkg/swarm_hack_traces.tar.gz outputs/raw outputs/logs
ls -la /tmp/swarm_pkg
unzip -l /tmp/swarm_pkg/swarm_hack_code.zip | grep -E "secrets|\.env|pt_live" || echo "no secrets in code zip (filename check)"
