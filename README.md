# CAPE-Swarm — assurance laundering in LLM agent teams, and the log level that catches it

Research sprint submission for the Swarm Alignment Hackathon (Apart Research, 6–8 November 2026). Track 4: Multi-Agent
Oversight and Control.

**Report:** `paper/report.pdf` (built on the official template; source `paper/parts/*.md`, builder `paper/build_report.py`).
**Replay viewer:** open `paper/viewer.html` in a browser (self-contained, no network).
**Full pass/fail record of every hypothesis:** `results/SUMMARY.md` (auto-generated from the raw traces).

## The question
In an agent team, a peer agent says "all approvals were already obtained (ticket #…)". Nobody verified it. Does the team act
without authorization, and does the human then read a confident, false report? We call this **assurance laundering**.
Every scenario has a safe twin and an unsafe twin that differ in one fact, and a rule-based checker (not an LLM judge)
labels every executed tool call.

## What the study found (details and numbers: report and `results/SUMMARY.md`)
- A false peer assurance raises unauthorized actions, but only for some models. Three of seven open-weight models react
  strongly, one weakly, three hardly at all. Which models react is explained by whether the Lead's brief endorses or rejects the claim.
- Teams lower the violation rate, and a careful Lead acts as a gatekeeper in mixed-model teams. No team shape repairs the report.
- Acting and reporting need different fixes. An explicit permission-system record repairs reports. A structural ask-before-act
  gateway rule stops the action at a small utility cost. A verification prompt and an auditor agent help but leave a residual.
- A monitor must read the gateway ledger **with tool results** to see violations. The final report, the messages, or the call list
  without results are close to blind.
- Two secondary or preregistered hypotheses failed (H8, H13). They are reported in the paper.

## Preexisting work (written BEFORE the sprint) and new work (written DURING the sprint)
| Part | Status |
|---|---|
| `preexisting/cape_src/cape/envs/` — CAPE-Bench mock tools, scenario families, generator, rule checker (the author's CAPE project, arXiv 2610.17301, October 2026) | **PREEXISTING.** Copied unchanged. |
| The concept of retroactive permission laundering and the matched-twin design | **PREEXISTING** (CAPE paper). |
| `capeswarm/` — API client, swarm engine (topologies, gateway, structured reports), controls, monitors, ledger auditor, statistics, hypothesis tests | **NEW** (sprint). |
| `scripts/`, `tests/`, `docs/PREREG_*.md`, `docs/DEVIATIONS.md`, `results/`, `paper/` | **NEW** (sprint). |
| `outputs/raw/*.jsonl` — every episode, with its full trace | **NEW** (sprint). |

The author's separate GreyBox project (training-free monitors from a model's own answers) motivated the self-query monitor.
No GreyBox code is used here.

## Layout
```
capeswarm/      engine (llm.py, swarm.py), controls.py, monitors.py, audit.py (ledger auditor), hops.py, hyp.py, stats.py, load.py
scripts/        10_confirm.py (runs e1..e7), 11_monitor.py (E2), 12_brief_stance.py (exploratory label), 13_attacker.py (E8),
                20_analyze.py (all tests), 21_figures.py, 22_quotes.py, 23_fig_schematic.py, 24_extra.py, 25_summary.py,
                30_viewer.py, 40_review.py (LLM review aid), lock.py
docs/           PREREG_v1.md and addenda, DEVIATIONS.md (every change after a lock), PAPER_ROADMAP.md, research notes
results/        *_lock.json (SHA-256 of prereg + code), hypotheses.json, descriptive.json, extra.json, SUMMARY.md
tests/          unit tests (checker labels, gateway controls, audit rule, metrics, bootstrap)
```

## Reproduce
```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
mkdir -p .secrets && echo "ADAPTION_API_KEY=<your key>" > .secrets/adaption.env   # hosted open-weight models, https://api.prod.adaptionlabs.ai
set -a; . .secrets/adaption.env; set +a
.venv/bin/python -m pytest -q tests                  # no API needed
python scripts/20_analyze.py                         # recompute every test from the stored traces: no API needed
python scripts/21_figures.py && python scripts/25_summary.py && python paper/assemble.py && python paper/build_report.py
python scripts/10_confirm.py e1                      # behavior: 7 models x 3 teams x 2 messages x 96 instances (about 4 h at the API limit)
```
The API allows about 300 requests per minute per user, so one process owns the key. The whole study used about 150 platform
credits. Run order and throughput-only changes are logged in `docs/DEVIATIONS.md`.

## Verifiable ordering
Hypotheses, thresholds and code were hashed and committed before the confirmatory data existed (`results/prereg_*_lock.json`, see
`git log`). Every change after a lock is dated in `docs/DEVIATIONS.md`. Exploratory analyses are labeled as such in the report.

## Try it on your own agent team
`python -m capeswarm.audit ledger.jsonl --report report.json` checks a gateway ledger (one JSON object per tool call) for
state-changing calls with no recorded approval, and flags a report that claims authorization the ledger does not support
(examples in `examples/`). Optional `--llm MODEL` adds the ledger-level LLM monitor.

## Responsible use
All environments are mock tools with synthetic people. We release no optimized attack text beyond the benchmark wordings and the
single attacker-search record in `docs/attacker_search.json` (see Appendix A of the report).
