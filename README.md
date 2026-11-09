# CAPE-Swarm — assurance laundering in LLM agent teams, and the log level that catches it

Research sprint submission for the Swarm Alignment Hackathon (Apart Research, 6–8 November 2026). Track 4: Multi-Agent
Oversight and Control.

**Report:** `paper/report.pdf` (built on the official template; source `paper/parts/*.md`, builder `paper/build_report.py`).
**Replay viewer:** open `paper/viewer.html` in a browser (self-contained, no network).
**Full pass/fail record of every hypothesis:** `results/SUMMARY.md` (auto-generated from the raw traces). Numbers for the later experiments (E9–E13): `results/round2.json`. Every prediction with its estimate: `docs/HYPOTHESES.md`. Public repository: https://github.com/AryaFayyazi/swarm_mutli.

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
- **Why the claim works (E12, preregistered 2x2).** The false claim raises violations (0.10 to 0.38) only when no verification rule is in the prompt. With the rule the claim adds +0.04. The logs agree (exploratory): the Operator asks the permission system first in 0.82 of runs with no claim and 0.47 with the claim.
- A **claim filter** marks every approval claim that crosses an agent boundary as unverified. On fresh tasks (E9) it cut unauthorized actions from 0.36 to 0.03 with no measurable loss of useful work, and it also worked on an attacker wording it was not tuned on (0.50 to 0.01). An attacker who read the filter prompt (E11) reached 0.31 without a control and 0.05 with the filter; the ask-before-act gate held at 0.00. A message with no claim at all would pass the filter.
- **Doubt from a peer (E13, preregistered replication of an exploratory E5 result).** A hedged message brings violations back to the no-message rate (0.09 against 0.10). It does not beat silence, the same V appears with a neutral message, and it costs useful work (goal 0.60 against 0.78). A peer's question lowers V to 0.01.
- Seven of 33 preregistered predictions failed (H8, H13, H18, H25, H32, H34, H35). They are reported in the paper (Appendix C) and in `docs/HYPOTHESES.md`. Two predictions for a stealthy Operator (E10, H26 and H27) were not run.

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
scripts/        10_confirm.py (runs e1..e13), 26_audit_numbers.py (independent recomputation of headline numbers), 11_monitor.py (E2), 12_brief_stance.py (exploratory label), 13_attacker.py (E8), 14_filter_attacker.py (E11 search), 27_round2.py (tests for E9–E13), 28_fig_round2.py,
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
