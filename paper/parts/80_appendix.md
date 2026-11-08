## Appendix A. Limitations and Dual-Use / Ethical Considerations
### A.1 Limitations
We list each assumption and say how a result would change if it failed.
- **Open-weight models only.** The sprint API serves seven open-weight models. Frontier closed models may behave differently. The effect size varies a lot between our models (Figure 2a), so we do not claim a rate for any other model. The *direction* of the mechanism is what we test. If frontier models resist the assurance, H1 would fail for them, and the gateway results (H5) would still stand.
- **The attacker is weak.** One message from a peer starts the chain. We tested four hand-written wordings (E5) and a two-round search by one attacker model that saw only a generic description and development-seed scores (E8). A stronger attacker that knows the scenario, the policy or the agents' prompts, or one trained against the team, may do more.
- **One model per team, mostly.** Teams use one model for every role. E4 mixes models, but only four models and only across the credulous/skeptical divide.
- **Mock tools and a rule checker.** CAPE-Bench is synthetic. The permission system answers "approved" or "denied" by a fixed rule per world. Real approvers are slower and noisier. The utility cost of the ask-before-act gate may be larger in real workflows.
- **The oracle policy check is an upper bound.** It uses the benchmark's own checker. Its zero violation rate is true by construction (H11), so we do not count it as a finding.
- **Reports show facts, not intent.** A false "authorized" is a false statement of fact. We do not claim the agents *meant* to deceive. The self-query monitor (H9) probes this and does not settle it.
- **Monitors are LLM judges from the same families as the agents.** A judge may share the agents' blind spots. We assume the gateway ledger (L2, L3) is written by the gateway and cannot be edited by agents. An incident investigation found agents that spoofed tool calls and edited logs inside their containers [13]. If agents could write the ledger, L3 would lose its advantage.
- **Sample size and scope.** 48 base scenarios (6 per family) give 96 instances per condition. Intervals reflect scenario sampling, not template or family sampling. Per-family results are exploratory.
- **Ordering evidence is local.** Locks are SHA-256 hashes and git commits. Dates inside one repository can be forged. The commit history should be published with the report so that readers can check the order.


### A.2 Dual-Use and Ethical Considerations
**What this work could enable.** The study shows that a single false, plausible sentence ("all approvals were obtained") can make agent teams act without authorization and then report with false confidence. A malicious actor could use the same idea to social-engineer an agent team. The idea is simple, and our wording variants add little to it. We release no attack tooling. The repository contains the wordings we tested and the record of the attacker search (`docs/attacker_search.json`): short, generic sentences that add little to the main message, which we include so that the search can be reproduced. All environments are mock tools with synthetic people and organizations. No real system, person or data was touched.

**Why we publish.** The same results tell deployers what to log and what to enforce. In our tests a gateway rule stops the action and a permission-system record cuts false reports. A monitor that reads only messages sees the violation poorly (AUROC {{X['mon']['L1'][0]|.2f}}–{{X['mon']['L1'][1]|.2f}}), so deployers who log only messages are close to blind. We judge that this defensive value outweighs the small uplift to attackers. We also state clearly that the in-protocol auditor and the verification prompt are not enough alone.

**Monitor evasion.** Our results show which logs a monitor needs. An attacker who knows this could try to write false entries into those logs. We therefore state our assumption that the gateway ledger is not agent-writable, and we cite evidence that real agents have tried to tamper with logs [13].

**Misuse of the auditor.** The ledger auditor can raise false alarms. It is a screening aid and not evidence of wrongdoing by any agent or person. We do not claim that the agents acted with intent.

**Data and models.** The data contain only synthetic traces from public open-weight models. Credentials were kept outside the repository.

**Limitations of this appendix.** We did not run a human study and did not consult an ethics board. We believe the risk is low, but we cannot rule out uses we did not foresee.

## Appendix B. LLM Usage Statement
We used Claude Code (Claude Sonnet 5.5) as a coding assistant for the harness, the analysis code and the figures, and to draft the first version of this report. The open-weight models served through the Adaption API are the subjects of the experiments and the monitors. No number in this report was typed by hand: the text pulls each number from `results/*.json`, which `scripts/20_analyze.py` writes from the raw traces. The preregistration and its locks were written before the confirmatory runs. The human author is responsible for all claims and should verify them against the repository.

## Appendix C. All preregistered hypotheses
We list every hypothesis, including those that did not hold. Directions and thresholds were fixed before the data existed (`docs/PREREG_v1.md` and its addenda). Holm correction is applied within each family (H1–H7; H12–H14; H15–H16; H18–H19; H17 is a single test).

TABLE: **Table C1.** Outcome of every hypothesis. Estimates are pooled over models with equal weight; intervals are 95% cluster-bootstrap over base scenarios.
{{X['hyp_table']}}

TABLE: **Table C2.** Unauthorized-action rate on unsafe twins by model, team shape and message (48 episodes per cell).
{{X['model_table']}}

TABLE: **Table C3.** Unauthorized-action rate on unsafe twins by scenario family (pooled over 7 models and 3 team shapes; exploratory).
{{X['family_table']}}

TABLE: **Table C4.** All controls on the peer-assured relay (four models; 96 instances each: unsafe twins for violations and reports, safe twins for goal completion). Report ratios rest on few violations when violations are near zero (for example, one violation under the gate).
{{X['controls_table']}}

## Appendix D. Implementation details and cost
All agents run at temperature 0.7 with native tool calls and at most 24 turns. An agent that stops without reporting gets up to two neutral nudges; a neutral warning appears three turns before the step limit. Auditors run at temperature 0. Judges run at temperature 0.5 and score each trace twice. The API allows about 300 requests per minute, so one process owns the key and a global limiter paces calls. The whole study (about {{D['counts']['e1'] + D['counts']['e3'] + D['counts']['e3b'] + D['counts']['e4'] + D['counts']['e5'] + D['counts']['e6'] + D['counts']['e7']}} episodes plus monitor calls) used about {{D['cost_total']}} Adaption platform credits for the episodes and monitors listed in the run logs. Code is in `capeswarm/`; every confirmatory run and analysis step has a script in `scripts/`; `tests/` holds unit tests for the checker labels, gateway controls, audit rule, metrics and bootstrap.
