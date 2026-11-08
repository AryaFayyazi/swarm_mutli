## 1. Introduction
Teams of AI agents now do real work with real tools, and the human often sees only the last message. This makes the *report* a safety-critical object. A recent investigation of a multi-agent incident found agents that spoofed tool calls and tried to edit the logs inside their own containers [13]. If we cannot trust what agents write about what they did, we need to know which record to trust, and who writes it.

We study one concrete way that reports go wrong. In a team, a peer agent states a plausible fact: "all approvals were already obtained (ticket #31819)". Nobody has verified it. The Lead passes it to the Operator, the Operator acts, and the Lead tells the human that the work was authorized and cites the ticket. We call this **assurance laundering**. An unverified claim enters the team as a remark, becomes an instruction, leads to an unauthorized action, and leaves the team as a confident, specific, false report.

We test this with **CAPE-Swarm**, a team layer on top of CAPE-Bench [1]. In every scenario, one fact decides whether the critical action is authorized, and a matched twin flips that fact. A rule-based checker labels each executed call, so no LLM judge decides what is unauthorized. The same peer message appears in both twins. It is true in one and false in the other. We ran {{D['counts']['e1']}} episodes of seven open-weight models in solo, relay and relay-2 teams, plus controls, mixed-model teams and monitors. All hypotheses, thresholds and code were locked before the data existed.

**What we find.** {{INTRO_FINDINGS}}

**Our contributions.**
1. We define and measure *assurance laundering* in agent teams. We give matched safe and unsafe twins, a rule-based label for every call, and a structured report whose claims can be checked against the gateway ledger. (New: the team layer, the manipulation, the outcomes. Preexisting: the CAPE-Bench environments.)
2. We separate three problems that look like one. Acting without authorization, reporting it falsely, and monitoring it need different fixes. A permission-system record repairs the report. An ask-before-act gateway rule prevents the action, and we price it in utility. In-protocol auditors and prompts help only in part.
3. We give a deployer a log ladder (report, messages, calls, calls with results, everything) and show which level lets a monitor see the violation. We release the traces, a replay viewer and a ledger auditor, so a team can run the same test on its own agents.
