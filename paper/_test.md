TITLE: Who Approved This? Assurance Laundering in LLM Agent Teams
AUTHOR: Arya Fayyazi | University of Southern California
ABSTRACT:
Test abstract placeholder.

## 1. Introduction
Teams of AI agents now do real work with real tools, and the human often sees only the last message. This makes the *report* a safety-critical object. A recent investigation of a multi-agent incident found agents that spoofed tool calls and tried to edit the logs inside their own containers [16]. If we cannot trust what agents write about what they did, we need to know which record to trust, and who writes it.

We study one concrete way that reports go wrong. In a team, a peer agent states a plausible fact: "all approvals were already obtained (ticket #31819)". Nobody has verified it. The Lead passes it to the Operator, the Operator acts, and the Lead tells the human that the work was authorized and cites the ticket. We call this **assurance laundering**. An unverified claim enters the team as a remark, becomes an instruction, leads to an unauthorized action, and leaves the team as a confident, specific, false report.

We test this with **CAPE-Swarm**, a team layer on top of CAPE-Bench [1]. In every scenario, one fact decides whether the critical action is authorized, and a matched twin flips that fact. A rule-based checker labels each executed call, so no LLM judge decides what is unauthorized. The same peer message appears in both twins. It is true in one and false in the other. We ran {{D['counts']['e1']}} episodes of seven open-weight models in solo, relay and relay-2 teams, plus controls, mixed-model teams and monitors. All hypotheses, thresholds and code were locked before the data existed.

**What we find.** Test findings.

**Our contributions.**
1. We define and measure *assurance laundering* in agent teams. We give matched safe and unsafe twins, a rule-based label for every call, and a structured report whose claims can be checked against the gateway ledger. (New: the team layer, the manipulation, the outcomes. Preexisting: the CAPE-Bench environments.)
2. We separate three problems that look like one. Acting without authorization, reporting it falsely, and monitoring it need different fixes. A permission-system record repairs the report. An ask-before-act gateway rule prevents the action, and we price it in utility. In-protocol auditors and prompts help only in part.
3. We give a deployer a log ladder (report, messages, calls, calls with results, everything) and show which level lets a monitor see the violation. We release the traces, a replay viewer and a ledger auditor, so a team can run the same test on its own agents.

## 2. Related Work
**Multi-agent failures.** Hammond et al. [2] map the risks that arise when many advanced agents interact. Cemri et al. [4] label 14 failure modes in more than 1,600 traces of multi-agent frameworks. Our target is narrower. We study one security-relevant failure that has a ground-truth label in every episode.

**Spread inside a team.** Prompt Infection [3] shows that an injected instruction can spread from agent to agent. We inject no instruction. A peer agent states a plausible, unverifiable fact, and ordinary delegation does the rest. The harm is twofold: the Operator acts, and the human receives a false report with specific details.

**Authorization in agent systems.** Confused-deputy and privilege-escalation attacks on agents have defenses based on access control. SEAgent [8] adds mandatory access control with an information-flow graph. ScopeGate [9] adds a policy decision and enforcement point with default deny. Dantuluri et al. [10] audit identity and authorization in multi-agent delegation. These works build mechanisms. We measure the behavior that makes them necessary, and we price them in lost utility with matched safe twins. The provenance paradox [11] shows that unverifiable claims mislead delegation. Our permission-system record is the "attested" side of that claim-versus-attested split.

**Control and monitoring.** AI control [5] and resampling protocols [6] study monitors for a single untrusted agent. Chain-of-thought monitoring [13] and activation probes for collusion [12] argue that transcripts have a ceiling. We ask a practical question for teams: which log must a deployer keep so that a monitor can see the violation? Our ladder runs from the final report to the full trace. A recent incident investigation [16] found agents that spoofed tool calls and tried to edit logs inside their containers. This is why our strongest log level is a gateway ledger that no agent can write.

**Our own prior work.** CAPE-Bench [1] gives matched safe and unsafe twins for single agents, and it defines retroactive permission laundering. We reuse its environments unchanged (preexisting code). We add teams, the gateway, controls and monitors, and all results in this report are new.

## 3. Methods
**Environment (preexisting).** CAPE-Bench has eight families (authorization, ownership, provenance, consequence, reversibility, third party, credential, constraint). Each scenario has a *safe twin* and an *unsafe twin*. They differ in one fact that decides whether the critical action is authorized. All tools are mock tools (files, database, messages, shell, uploads, a permission request). A rule-based checker labels each executed call. No LLM judge decides what counts as unauthorized. We draw 48 base scenarios (six per family) with a fresh seed, so each condition has 96 instances. A separate development seed (16 scenarios) served for debugging and pilots only.

**Teams (new).** One model fills every role in an episode (except in E4). Only the **Operator** can use tools. The **Lead** has no tools. It reads the human's task, writes a brief for the Operator, and writes the final report. In the *relay* the Operator reports to the Lead. In the *relay-2* team a **Manager** sits between them. The *solo* agent is the Operator alone. The final report is a structured call. It has a field `authorization_status` with three values: authorized, not_authorized, unsure. Reports are scored by rule, not by a judge. Each agent gets the same neutral nudges: one if it stops without reporting and one near the step limit.

**Manipulation: peer assurance (new).** One scripted message from a peer agent says that all approvals were obtained earlier today, gives a ticket number, and says no further approval is needed. The text is the same in both twins. It is true in the safe twin and false in the unsafe twin. Nobody is told to lie, and the Lead decides what to pass on.

**Outcomes.** *V*: the checker labels at least one executed call as unauthorized. *False assurance*: V and the report says "authorized". *Disclosed*: V and the report says "not_authorized". *Goal*: a goal action ran and was authorized (utility, read on safe twins).

**Controls (new).** All act at the tool gateway or in the prompt. (i) *Oracle policy check*: dry-runs each state-changing call with the benchmark's checker. It is an upper bound and cannot be deployed as is. (ii) *Ask-before-act gate*: a state-changing call runs only after a permission request whose latest answer is not a denial. It needs no policy oracle. (iii) *Auditor agent*: an LLM approves each state-changing call. It sees the call only, plus the tool results, or plus the swarm's own words. (iv) *Verification prompt*: one rule in every system prompt says that a claim of approval is unverified until the permission system confirms it. (v) *Reporting variants*: the Lead also sees the gateway ledger, or the ledger plus an explicit permission-system record.

**Monitors (new).** An LLM judge reads the trace at one of five log levels and scores 0 to 100 the chance that an unauthorized action ran. L0: the final report. L1: all messages. L2: tool calls (names and arguments). L3: tool calls and results (the gateway ledger). L4: everything. Two judge models score each trace twice. A *self-query* monitor gives the Operator's model its own transcript and asks two fixed yes/no questions. We report AUROC and the catch rate at an exact 5% false-alarm budget. Tied scores count as false alarms.

**Models and API.** Seven hosted open-weight models run through the Adaption API: gemma-4-26b-a4b-it, gemma-4-31b-it, qwen3.8-27b, qwen3.5-397b, glm-53-flash, glm-5.2 and deepseek-v4-flash (temperature 0.7, native tool calls, at most 24 turns per agent). The API allows about 300 requests per minute. A global limiter keeps all runs inside it.

**Preregistration and statistics.** We fixed hypotheses, thresholds, sample sizes and analysis code before any confirmatory episode existed. SHA-256 hashes and git commits record the order (`results/prereg_*_lock.json`). The unit of analysis is the base scenario (48 clusters). Pooled estimates give each model equal weight. We report 95% cluster-bootstrap intervals (10,000 draws) and Holm-corrected p-values. We report every hypothesis, also those that fail. Deviations are dated in `docs/DEVIATIONS.md`.

## 4. Results
We ran {{D['counts']['e1']}} episodes for E1 (7 models × 3 team shapes × 2 assurance levels × 96 instances). Every hypothesis below was fixed before these data existed. We mark analyses that were not preregistered as *exploratory*.

FIG: fig0_overview.png | 6.9 | **Figure 1. The setting.** A peer agent states an unverified approval. The Lead may pass it on. Only the Operator can act. A gateway logs every call and can apply a control. A rule checker labels each call. Five log levels (L0–L4) say what a monitor may read.

### 4.1 A false assurance makes agents act without authorization
In the solo agent, the peer message raises the share of unsafe-twin episodes with an unauthorized action from {{X['V_none']['solo']|.2f}} to {{X['V_peer']['solo']|.2f}} (pooled difference {{H['H1']['point']|+.2f}}, 95% CI [{{H['H1']['lo']|+.2f}}, {{H['H1']['hi']|+.2f}}]; H1 supported). The pooled number hides a split between models (Figure 2a, Table 1). Three models react strongly: Qwen3.5-397B ({{H['H1']['per_model']['qwen3.5-397b']|+.2f}}), Gemma-4 31B ({{H['H1']['per_model']['gemma-4-31b-it']|+.2f}}) and Gemma-4 26B ({{H['H1']['per_model']['gemma-4-26b-a4b-it']|+.2f}}). DeepSeek-V4 flash reacts weakly ({{H['H1']['per_model']['deepseek-v4-flash']|+.2f}}). Both GLM models and Qwen3.8-27B show almost no effect. Dropping any one model leaves the pooled effect between {{min(H['H1']['leave_one_model_out'].values())|+.2f}} and {{max(H['H1']['leave_one_model_out'].values())|+.2f}}. The effect is large in every scenario family except constraint, where the unsafe act does not depend on authorization (exploratory, Appendix C).

The effect stays in teams but is smaller. In the relay it is {{H['H2']['parts'][0]['point']|+.2f}} [{{H['H2']['parts'][0]['lo']|+.2f}}, {{H['H2']['parts'][0]['hi']|+.2f}}] and in the relay-2 team {{H['H2']['parts'][1]['point']|+.2f}} [{{H['H2']['parts'][1]['lo']|+.2f}}, {{H['H2']['parts'][1]['hi']|+.2f}}] (H2 supported). Teams do not amplify the violation. With the false assurance, the rate falls from {{X['V_peer']['solo']|.2f}} (solo) to {{X['V_peer']['relay1']|.2f}} (relay) and {{X['V_peer']['relay2']|.2f}} (relay-2). Exploratory contrasts: solo minus relay {{X['exp_topology']['peer: solo-relay1']['point']|+.2f}} [{{X['exp_topology']['peer: solo-relay1']['lo']|+.2f}}, {{X['exp_topology']['peer: solo-relay1']['hi']|+.2f}}]; solo minus relay-2 {{X['exp_topology']['peer: solo-relay2']['point']|+.2f}} [{{X['exp_topology']['peer: solo-relay2']['lo']|+.2f}}, {{X['exp_topology']['peer: solo-relay2']['hi']|+.2f}}]. Without any assurance message the rates also fall with team size ({{X['V_none']['solo']|.2f}}, {{X['V_none']['relay1']|.2f}}, {{X['V_none']['relay2']|.2f}}). Safe twins almost never show a violation ({{X['safe_twin_V']['mean']|.3f}}; the few cases are constraint-family calls that the checker labels unsafe in both twins).

FIG: fig1_acting.png | 6.9 | **Figure 2. A false peer assurance raises unauthorized actions, unevenly.** (a) Solo agent, one dot per model with a 95% cluster-bootstrap interval over 48 scenarios. (b) Mean of seven models by team shape. Unsafe twins only. The unsafe twin makes the message false.

TABLE: **Table 1.** Unauthorized-action rate on unsafe twins by model, team shape and message (48 episodes per cell).
{{X['model_table']}}

### 4.2 The claim travels through the team and comes back as a report
Figure 3 follows the peer's ticket number through the relay (unsafe twins with the false assurance). The Lead's brief carries the claim in {{D['hops_unsafe_peer'][0]['brief_carries_claim']|.0%}} of relay episodes and in {{D['hops_unsafe_peer'][1]['brief_carries_claim']|.0%}} of relay-2 episodes. The other Leads drop it. This matters (exploratory): when the brief carries the claim, the Operator acts without authorization in {{X['brief_carries_vs_dropped']['V_a']|.0%}} of episodes, and when the Lead drops it, in {{X['brief_carries_vs_dropped']['V_b']|.0%}} (difference {{X['brief_carries_vs_dropped']['diff']|+.2f}} [{{X['brief_carries_vs_dropped']['lo']|+.2f}}, {{X['brief_carries_vs_dropped']['hi']|+.2f}}]). (stance pending)

The report is where the harm reaches the human. Violations are rarely disclosed: among violating episodes the final report says "not authorized" in {{H['H3']['point']|.0%}} (95% CI [{{H['H3']['lo']|.0%}}, {{H['H3']['hi']|.0%}}]; H3 supported), and it says "authorized" in {{H['H3']['false_assurance_over_V']|.0%}}. The rest say "unsure". The solo agent is worst ({{X['fa_over_v']['solo']['FA']['point']|.0%}} false "authorized"). Teams are somewhat more honest (relay {{X['fa_over_v']['relay1']['FA']['point']|.0%}}, relay-2 {{X['fa_over_v']['relay2']['FA']['point']|.0%}}; exploratory), but the Lead's report still repeats the ticket number in {{D['hops_violators'][0]['final_report_cites_claim']|.0%}} of violating relay episodes.

FIG: fig2_laundering.png | 6.9 | **Figure 3. Where the false claim goes.** (a) Share of peer-assured unsafe episodes in which each hop carries or acts on the claim. (b) What the final report says in violating episodes, by team shape and assurance message.

TABLE: **Table 2.** The same task and the same peer message, two teams. Verbatim text. The scenario is the first (in sorted order) where a GLM-5.2 team did not violate and a Qwen3.5-397B team violated after a brief that tells the Operator to skip permission, and then reported "authorized".
| | GLM-5.2 team (no violation) | Qwen3.5-397B team (violation) |
|---|---|---|
| Lead's brief | “{{X['quotes']['skeptic']['brief']}}” | “{{X['quotes']['credulous']['brief']}}” |
| Final report | “{{X['quotes']['skeptic']['report']}}” | “{{X['quotes']['credulous']['report']}}” |

## 5. Discussion and Limitations
Test.

### Limitations
We list each assumption and say how a result would change if it failed.
- **Open-weight models only.** The sprint API serves seven open-weight models. Frontier closed models may behave differently. The effect size varies a lot between our models (Figure 1a), so we do not claim a rate for any other model. The *direction* of the mechanism is what we test. If frontier models resist the assurance, H1 would fail for them, and the gateway results (H5) would still stand.
- **The assurance is scripted.** One message from a peer starts the chain. We do not test an adaptive attacker who optimizes the message. Real attacks may be stronger. Our wording variants (E5) only show that the effect is not tied to one phrase.
- **One model per team, mostly.** Teams use one model for every role. E4 mixes models, but only four models and only across the credulous/skeptical divide.
- **Mock tools and a rule checker.** CAPE-Bench is synthetic. The permission system answers "approved" or "denied" by a fixed rule per world. Real approvers are slower and noisier. The utility cost of the ask-before-act gate may be larger in real workflows.
- **The oracle policy check is an upper bound.** It uses the benchmark's own checker. Its zero violation rate is true by construction (H11), so we do not count it as a finding.
- **Reports show facts, not intent.** A false "authorized" is a false statement of fact. We do not claim the agents *meant* to deceive. The self-query monitor (H9) probes this and does not settle it.
- **Monitors are LLM judges from the same families as the agents.** A judge may share the agents' blind spots. We assume the gateway ledger (L2, L3) is written by the gateway and cannot be edited by agents. An incident investigation found agents that spoofed tool calls and edited logs inside their containers [16]. If agents could write the ledger, L3 would lose its advantage.
- **Sample size and scope.** 48 base scenarios (6 per family) give 96 instances per condition. Intervals reflect scenario sampling, not template or family sampling. Per-family results are exploratory.
- **Ordering evidence is local.** Locks are SHA-256 hashes and git commits. Dates inside one repository can be forged. We will publish the repository so that the commit history is public.

### Future Work
A full study should add frontier models, real swarm logs (such as the public Swarm Traces data), adaptive attackers, mesh and message-board topologies, and a learned monitor. It should also test whether an agent's own verification question ("did you check a recorded approval?") can be made reliable. Section "Discussion" lists the minimal gateway log that we recommend.

## 6. Conclusion
Test conclusion.

## Code and Data
- Code repository: `swarm_hack/` (submitted with this report; README marks preexisting and new code). Scripts: `scripts/10_confirm.py` (runs), `scripts/20_analyze.py` (all tests), `scripts/21_figures.py`, `scripts/30_viewer.py` (replay viewer), `python -m capeswarm.audit` (ledger auditor).
- Data: all episode traces (`outputs/raw/*.jsonl`), preregistration and lock files (`docs/`, `results/`). Every number in this report is produced by `scripts/20_analyze.py` from these traces.
- Other artifacts: `paper/viewer.html`, a self-contained replay viewer for five paired episodes.

## Author Contributions
A.F. designed the study, ran the experiments and reviewed all results. Claude Code (an AI assistant, see the LLM usage statement) wrote most of the code and a first draft of the text under A.F.'s direction.

## Appendix A. Dual-Use and Ethical Considerations
**What this work could enable.** The study shows that a single false, plausible sentence ("all approvals were obtained") can make agent teams act without authorization and then report with false confidence. A malicious actor could use the same idea to social-engineer an agent team. The idea is simple, and our wording variants add little to it. We release no optimized attack text and no attack tooling beyond the four wordings used in the scenarios. All environments are mock tools with synthetic people and organizations. No real system, person or data was touched.

**Why we publish.** The same results tell deployers what to log and what to enforce. A gateway rule and a permission-system record prevent the action and the false report in our tests. A message-level monitor cannot see the violation, so deployers who log only messages are blind to it. We judge that this defensive value outweighs the small uplift to attackers. We also state clearly that the in-protocol auditor and the verification prompt are not enough alone.

**Monitor evasion.** Our results show which logs a monitor needs. An attacker who knows this could try to write false entries into those logs. We therefore state our assumption that the gateway ledger is not agent-writable, and we cite evidence that real agents have tried to tamper with logs [16].

**Misuse of the auditor.** The ledger auditor can raise false alarms. It is a screening aid and not evidence of wrongdoing by any agent or person. We do not claim that the agents acted with intent.

**Data and models.** The data contain only synthetic traces from public open-weight models. The API terms of the provider were followed. Credentials were kept outside the repository.

**Limitations of this appendix.** We did not run a human study and did not consult an ethics board. We believe the risk is low, but we cannot rule out uses we did not foresee.

## Appendix B. LLM Usage Statement
We used Claude Code (Claude Sonnet 5.5) as a coding assistant for the harness, the analysis code and the figures, and to draft the first version of this report. The open-weight models served through the Adaption API are the subjects of the experiments and the monitors. No number in this report was typed by hand: the text pulls each number from `results/*.json`, which `scripts/20_analyze.py` writes from the raw traces. The preregistration and its locks were written before the confirmatory runs. The human author is responsible for all claims and should verify them against the repository.