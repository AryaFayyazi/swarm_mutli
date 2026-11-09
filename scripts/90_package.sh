#!/bin/sh
# Builds the two upload archives (no secrets, no virtualenv, no nested archives) and scans their contents for key patterns.
# Run from the repo root after the final report build.
cd /home/arya/swarm_hack
rm -rf /tmp/swarm_pkg && mkdir -p /tmp/swarm_pkg
zip -r -q /tmp/swarm_pkg/swarm_hack_code.zip . -x ".secrets/*" ".venv/*" "*.env" "outputs/raw/*" "__pycache__/*" "*/__pycache__/*" "paper/_*" "template/x/*" "outputs/dev_dry/*" ".pytest_cache/*" "submission/*.zip" "submission/*.tar.gz"
tar -czf /tmp/swarm_pkg/swarm_hack_traces.tar.gz outputs/raw outputs/logs
ls -la /tmp/swarm_pkg
echo "--- filename check"; unzip -l /tmp/swarm_pkg/swarm_hack_code.zip | grep -E "secrets|\.env" || echo "no secret-like file names"
echo "--- content scan (code zip)"; mkdir -p /tmp/swarm_pkg/x && unzip -q -o /tmp/swarm_pkg/swarm_hack_code.zip -d /tmp/swarm_pkg/x && (grep -rIl -E "pt_live_|ghp_[A-Za-z0-9]{20,}|github_pat_|sk-ant-|AKIA[0-9A-Z]{16}" /tmp/swarm_pkg/x || echo "no key patterns")
echo "--- content scan (traces)"; mkdir -p /tmp/swarm_pkg/t && tar -xzf /tmp/swarm_pkg/swarm_hack_traces.tar.gz -C /tmp/swarm_pkg/t && (grep -rIl -E "pt_live_|ghp_[A-Za-z0-9]{20,}|github_pat_|sk-ant-|AKIA[0-9A-Z]{16}" /tmp/swarm_pkg/t || echo "no key patterns")
rm -rf /tmp/swarm_pkg/x /tmp/swarm_pkg/t
