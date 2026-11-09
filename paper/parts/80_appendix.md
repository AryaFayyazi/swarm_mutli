## Appendix A. Limitations and Dual-Use / Ethical Considerations
**What this result does and does not establish.** It establishes that, in mock-tool tasks with seven open-weight models, one unverified approval claim from a peer makes some teams act without authorization and report the work as authorized; that a gateway rule and a claim filter reduce this; and that a monitor needs the gateway log with tool results. It does not establish that frontier or closed models behave the same way, that real tools and real users behave like mock tools, that the claim filter survives a trained or long-running attacker, or that the agents "meant" to deceive. The sections below give each assumption and how the result would change if it failed.

### A.1 Limitations
We list each assumption and say how a result would change if it failed.
- **Open-weight models only.** The sprint API serves seven open-weight models. Frontier closed models may behave differently. The effect size varies a lot between our models (Figure 2a), so we do not claim a rate for any other model. The *direction* of the mechanism is what we test. If frontier models resist the assurance, the main effect would fail for them, and the gateway results would still stand.
- **The attacker is weak.** One message from a peer starts the chain. We tested four hand-written wordings (E5) and a two-round search by one attacker model that saw only a generic description and development-seed scores (E8). A stronger attacker that knows the scenario, the policy or the agents' prompts, or one trained against the team, may do more.
- **One model per team, mostly.** Teams use one model for every role. E4 mixes models, but only four models and only across the credulous/skeptical divide.
- **Controls were tested on four models.** We chose the four models with the highest violation rates in the development pilot. On the models that hardly react there is little to prevent, so the benefit would be smaller, and the utility cost would stay. We did not test controls on all seven models.
- **No tamper test.** We assume the gateway writes the ledger and agents cannot edit it. We did not test agents that try to edit or spoof it. Deployers should write the ledger from a separate process (a gateway or proxy) and, where needed, to an append-only store outside the agents' reach.
- **Small cells.** Each model cell has 48 episodes per condition, so per-model numbers are descriptive. Pooled estimates use 48 scenario clusters.
- **Mock tools and a rule checker.** CAPE-Bench is synthetic. The permission system answers "approved" or "denied" by a fixed rule per world. Real approvers are slower and noisier. The utility cost of the ask-before-act gate may be larger in real workflows.
- **The oracle policy check is an upper bound.** It uses the benchmark's own checker. Its zero violation rate is true by construction, so we do not count it as a finding.
- **Reports show facts, not intent.** A false "authorized" is a false statement of fact. We do not claim the agents *meant* to deceive. The self-query monitor probes this and does not settle it.
- **Monitors are LLM judges from the same families as the agents.** A judge may share the agents' blind spots. We assume the gateway ledger (L2, L3) is written by the gateway and cannot be edited by agents. An incident investigation found agents that spoofed tool calls and edited logs inside their containers [13]. If agents could write the ledger, L3 would lose its advantage.
- **Sample size and scope.** 48 base scenarios (6 per family) give 96 instances per condition. Intervals reflect scenario sampling, not template or family sampling. Per-family results are exploratory.
- **Round 2 is smaller than planned.** The API limit fell from about 300 to about 60 requests a minute during the sprint, so we cut the design (Amendments 5b, 5c). E9 stopped at its scheduled time: {{R['_n_clusters']}} of 40 planned base scenarios have every condition finished, and 26 of its 96 task prompts repeat prompts of round 1 (new entities, same templates). Its intervals use these {{R['_n_clusters']}} clusters. We looked once at the per-cell violation rates of the first 200 finished E9 episodes, and changed no prediction, threshold or test after that look (Amendment 5c; `docs/DEVIATIONS.md`).
- **The claim filter fails open.** If the filter model returns nothing, the original message passes: {{R['_filter']['fail_open']}} of {{R['_filter']['calls']}} calls, mostly on the Lead's brief. The filter's effect is therefore a lower bound for a filter that never fails. A filter is one more model in the path, so it adds latency and one more point of attack. It protects against *claims of approval*, not against other false claims.
- **The filter-aware attacker is white-box but brief.** It sees the full filter prompt, searches for two rounds on a development seed against two models, and tests one message. A longer search, or an attacker that is trained, may do more.
- **Ordering evidence is local.** Locks are SHA-256 hashes and git commits. Dates inside one repository can be forged. The commit history should be published with the report so that readers can check the order.


### A.2 Dual-Use and Ethical Considerations
**What this work could enable.** The study shows that a single false, plausible sentence ("all approvals were obtained") can make agent teams act without authorization and then report with false confidence. A malicious actor could use the same idea to social-engineer an agent team. The idea is simple, and our wording variants add little to it. We release no attack tooling. The repository contains the wordings we tested and the record of the attacker search (`docs/attacker_search.json`): short, generic sentences that add little to the main message, which we include so that the search can be reproduced. All environments are mock tools with synthetic people and organizations. No real system, person or data was touched.

**Why we publish.** The same results tell deployers what to log and what to enforce. In our tests a gateway rule stops the action and a permission-system record cuts false reports. A monitor that reads only messages sees the violation poorly (AUROC {{X['mon']['L1'][0]|.2f}}–{{X['mon']['L1'][1]|.2f}}), so deployers who log only messages are close to blind. We judge that this defensive value outweighs the small uplift to attackers. We also state clearly that the in-protocol auditor and the verification prompt are not enough alone.

**Monitor evasion.** Our results show which logs a monitor needs. An attacker who knows this could try to write false entries into those logs. We therefore state our assumption that the gateway ledger is not agent-writable, and we cite evidence that real agents have tried to tamper with logs [13].

**Misuse of the auditor.** The ledger auditor can raise false alarms. It is a screening aid and not evidence of wrongdoing by any agent or person. We do not claim that the agents acted with intent.

**Data and models.** The data contain only synthetic traces from public open-weight models. Credentials were kept outside the repository.

**Limitations of this appendix.** We did not run a human study and did not consult an ethics board. We believe the risk is low, but we cannot rule out uses we did not foresee.

## Appendix B. LLM Usage Statement
We used Claude Code (Claude Sonnet 5.5) only to help write code (the harness, the analysis scripts and the figures) and to draft the first version of this report. The open-weight models served through the Adaption API are the subjects of the experiments and the monitors. The text pulls each number from `results/*.json`, which `scripts/20_analyze.py` writes from the raw traces. The preregistration and its locks were written before the confirmatory runs. The author is the only author and is responsible for all claims and for everything in this report and repository.

## Appendix C. Preregistration record
Before each experiment we wrote down its predictions, thresholds, sample size and analysis code, and we recorded SHA-256 hashes and git commits (`docs/PREREG_v1.md` and its addenda; `results/prereg_*_lock.json`). The lock times are self-reported, and they were not published before each run. Table C1 summarizes the outcome by experiment. We tested {{X['nh']}} predictions, and every one is reported. {{X['nfail_word']}} did not hold: that the Operator's model alone decides whether a mixed team acts (E4); that the team's own words recruit an auditor (E3); that a short adaptive search finds a message stronger than the scripted one (E8); and that the claim filter costs less useful work than the gate (E9). @@E13APPC@@ One more prediction held only weakly: the lower confidence bound of the self-query monitor's AUROC is below its threshold (E2). Two predictions for a stealthy Operator (E10) were preregistered and not run. `docs/HYPOTHESES.md` lists every prediction with its estimate, interval and corrected p-value. Holm correction is applied within each family of related predictions.

TABLE{1.2,3.2,0.9,1.0}: **Table C1.** Outcome of the preregistered predictions, by experiment.
| Experiment | Question | Tested | Held |
|---|---|---|---|
| E1 | Does a false peer message raise unauthorized actions, in teams too, and how often is the report false? | 3 | 3 |
| E2 | Which log level lets a monitor see a violation? | 2 | 2 (one weakly) |
| E3 | What stops the action, and what repairs the report? | 5 | 4 |
| E3b | Does a verification rule in the prompt help? | 1 | 1 |
| E4 | Does the Operator's model decide for a mixed team? | 2 | 1 |
| E5 | Does the effect depend on the wording? | 2 | 2 |
| E7 | Does an auditor from another model family do better? | 1 | 1 |
| E8 | Does a model-written message beat the scripted one, and does the gate hold? | 2 | 1 |
| E9 | Does the claim filter work on fresh tasks, at what cost? | 6 | 5 |
| E11 | Does the filter hold against an attacker who knows it? | 3 | 3 |
| E12 | Does the claim work by displacing the check? | 1 | 1 |
| E13 | Does doubt from a peer protect the team? | 5 | @@E13HELD@@ |
| E10 | Stealthy Operator | 2 | not run |

TABLE: **Table C2.** Unauthorized-action rate on unsafe twins by model, team shape and message (48 episodes per cell).
{{X['model_table']}}

TABLE: **Table C3.** Unauthorized-action rate on unsafe twins by scenario family (pooled over 7 models and 3 team shapes; exploratory).
{{X['family_table']}}

TABLE{1.75,0.95,0.7,1.15,1.0,0.95}: **Table C4.** All controls on the peer-assured relay (four models; 96 instances each: unsafe twins for violations and reports, safe twins for goal completion). Report ratios rest on few violations when violations are near zero (for example, one violation under the gate).
{{X['controls_table']}}

## Appendix D. Experiments, implementation and cost
TABLE{1.25,2.65,0.65,0.8,1.1}: **Table D1.** Every experiment, its design and its size (all on the confirmatory seed unless noted).
| Experiment | What varies | Models | Episodes | Predictions |
|---|---|---|---|---|
| E1 behavior | model × team shape × message × twin (96 instances per cell) | 7 | {{D['counts']['e1']}} | 3 |
| E3 controls | controls and report sources, relay + false message | 4 | {{D['counts']['e3']}} | 5 |
| E3b prompt rule | verification rule in every system prompt | 4 | {{D['counts']['e3b']}} | 1 |
| E4 mixed teams | Lead and Operator from different models | 4 | {{D['counts']['e4']}} | 2 |
| E5 wording | manager, terse and hedged messages | 4 | {{D['counts']['e5']}} | 2 |
| E6 repeat | 48 unsafe instances rerun | 4 | {{D['counts']['e6']}} | descriptive |
| E7 diverse auditor | GLM-5.2 as the auditor | 4 | {{D['counts']['e7']}} | 1 |
| E8 attacker | selected message, with and without the gate | 4 | {{D['counts']['e8']}} | 2 |
| E9 claim filter | none / peer message / filter / gate / attacker message / attacker message + filter (fresh seed 5501) | 4 | {{R['counts']['e9']}} | 6 |
| E11 filter-aware attacker | message chosen against the filter; filter / none / gate | 4 | {{R['counts'].get('e11',0)}} | 3 |
| E12 2×2 | false claim × verification reminder | 4 | {{R['counts'].get('e12',0)}} | 1 |
| E13 doubt | hedged, question and neutral peer messages; no message on safe twins | 4 | {{R['counts'].get('e13',0)}} | 5 |
| E10 stealth Operator | planned, not run | – | 0 | 2 (not run) |
| E2 monitors | 768 E1 relay traces × 5 log levels × 2 judges × 2 scores, plus self-query | 4 | monitor calls only | 2 |

**Models.** The seven open-weight models are gemma-4-26b-a4b-it, gemma-4-31b-it, qwen3.8-27b, qwen3.5-397b, glm-53-flash, glm-5.2 and deepseek-v4-flash, all served through the Adaption Labs API. The four-model experiments use the first two, qwen3.5-397b and deepseek-v4-flash, chosen before the main runs because they reacted most in a small pilot.

**Implementation.** All agents run at temperature 0.7 with native tool calls and at most 24 turns. An agent that stops without reporting gets up to two neutral nudges; a neutral warning appears three turns before the step limit. Auditors run at temperature 0. Each of two judge models runs at temperature 0.5 and scores each trace twice (the scores are averaged). The API allowed about 300 requests per minute in round 1 and about 60 in round 2, so one process owns the key and a global limiter paces calls. The whole study (about {{D['counts']['e1'] + D['counts']['e3'] + D['counts']['e3b'] + D['counts']['e4'] + D['counts']['e5'] + D['counts']['e6'] + D['counts']['e7']}} episodes plus monitor calls) used about {{D['cost_total']}} Adaption platform credits for the episodes and monitors listed in the run logs. Code is in `capeswarm/`; every confirmatory run and analysis step has a script in `scripts/`; `tests/` holds unit tests for the checker labels, gateway controls, audit rule, metrics and bootstrap.
