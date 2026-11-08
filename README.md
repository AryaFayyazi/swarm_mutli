# CAPE-Swarm — authorization laundering in LLM agent swarms, and the log level that catches it

Research sprint submission, Swarm Alignment Hackathon (Apart Research), 6–8 November 2026. Track 4: Multi-Agent
Oversight and Control.

## What this is
A benchmark, an engine and a set of controls and monitors for one multi-agent failure mode:
**an unverified claim of approval travels through a team of agents, makes one agent act without authorization, and
then reaches the human as a confident, false report.** Each scenario has a matched safe twin and unsafe twin that
differ in one fact. A rule-based checker (not an LLM judge) labels every executed tool call.

## Preexisting work (written BEFORE the sprint) and new work (written DURING the sprint)
| Part | Status |
|---|---|
| `preexisting/cape_src/cape/envs/` — CAPE-Bench mock tools, scenario families, generator, rule checker (from the author's CAPE project, arXiv 2610.17301, Oct 2026) | **PREEXISTING.** Copied unchanged. |
| The idea of retroactive permission laundering and the matched-twin design | **PREEXISTING** (CAPE paper). |
| `capeswarm/` — async API client, swarm engine (topologies, gateway, roles, structured reports), controls, monitors, statistics, hypothesis tests | **NEW** (sprint). |
| `scripts/`, `docs/PREREG_*.md`, `results/`, `paper/` — runs, preregistration, analysis, figures, report | **NEW** (sprint). |
| `outputs/` — all episode traces (JSONL) | **NEW** (sprint). |

The author's separate GreyBox project (training-free monitors from a model's own answers) motivated the self-query
monitor. No GreyBox code is used here.

## Reproduce
```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
echo "ADAPTION_API_KEY=<your key>" > .secrets/adaption.env        # hosted open-weight models, https://api.prod.adaptionlabs.ai
set -a; . .secrets/adaption.env; set +a
python scripts/10_confirm.py e1      # behavior: 7 models x 3 topologies x 2 assurance x 96 instances
python scripts/10_confirm.py e3      # controls on relay1 + peer assurance
python scripts/10_confirm.py e3b     # prompt-level defense
python scripts/10_confirm.py e4      # mixed-model swarms
python scripts/11_monitor.py         # monitors at five log levels
python scripts/20_analyze.py         # every preregistered test -> results/*.json, figures -> paper/figs
```
Every episode is stored with its full trace (`outputs/raw/*.jsonl`), so every number can be recomputed without any API call:
`python scripts/20_analyze.py`. The API allows about 300 requests/minute, so the full run takes about 11 hours.

## Verifiable ordering
Hypotheses, thresholds and code were hashed and committed before the confirmatory data existed:
`results/prereg_v1_lock.json`, `prereg_v1_1_lock.json`, `prereg_v1_2_lock.json` (see `git log`). Deviations: `docs/DEVIATIONS.md`.
