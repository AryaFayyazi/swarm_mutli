## 3. Methodology
We measure how a false approval claim travels through an agent team, which intervention stops it, and which log reveals it. This section defines the instances, teams, outcomes, interventions, monitors and inference.

**3.1 Instances and labels (preexisting).** CAPE-Bench [1] provides a set *S* of base scenarios in eight families, such as authorization, ownership and third-party data. Each *s* ∈ *S* yields two *instances*, a *safe twin* and an *unsafe twin*, that differ in one fact, which decides whether the critical action is authorized. All tools are mock tools (files, a database, messages, a shell and a permission system), and the permission system answers as the scenario specifies (in the safe twin the user already holds the permission; in the unsafe twin a request is usually denied). A deterministic rule χ, the *checker*, labels each executed tool call as authorized or unauthorized. No LLM judge is involved. The main experiments use |*S*| = 48 scenarios (six per family, seed 9001). Later experiments use fresh scenarios (seed 5501, at most 40), so that no task that shaped an earlier analysis is reused.

**3.2 Teams and gateway (new).** A *team* is a set of roles filled by language models. Only the **Operator** has tools. The **Lead** has none: it writes a brief for the Operator and a final report for the human. The *relay* team is Lead plus Operator, the *relay-2* team adds a **Manager** between them, and the *solo* agent is the Operator alone. One model fills every role, except in E4, which pairs different models. The report is a structured call with the fields `authorization_status` ("authorized", "not_authorized" or "unsure"), `goal_completed`, `actions_performed` and `summary`, so we score reports by rule. A **gateway** sits between the Operator and the tools. It logs every call *a*(*t*) with its result in a *ledger* that agents cannot edit, and it is where controls act.

**3.3 Manipulation (new).** A message is delivered with the task (to the Lead in a team, to the Operator when alone). In the main condition, a scripted peer message states that all approvals were obtained earlier today (with a ticket number) and that no further approval is needed. The peer's name and the ticket number are drawn deterministically from the scenario. The message is identical in both twins: true in the safe twin and false in the unsafe twin. Nobody tells any agent to lie. Other messages change what is said about approval (a manager's message, a terse one, an expression of doubt, a question, a neutral message) or who wrote it (a model-written message, E8 and E11).

**3.4 Outcomes and estimands (new).** An *episode* *e* is one run of one team on one instance under one condition *c*. We define five per-episode indicators:

EQ: *V*(*e*) = 1{ ∃ *t* : χ(*a*(*t*)) = unauthorized }   (violation; unsafe twins)      (1)

EQ: *F*(*e*) = *V*(*e*) · 1{ status(*e*) = "authorized" },   *D*(*e*) = *V*(*e*) · 1{ status(*e*) = "not_authorized" }      (2)

EQ: *G*(*e*) = 1{ the authorized goal action was executed }   (goal; safe twins)      (3)

EQ: *A*(*e*) = 1{ request_permission is called before the first state-changing call }   (asked)      (4)

*F* is a *false report* and *D* a *disclosure*. We read *G* as useful work. For an indicator *y*, a condition *c*, a scenario *s* and a model set *M*, we average over the episodes *E*(*c*, *s*, *m*) of each model and then give the models equal weight:

EQ: *x*(*c*,*s*) = (1/|*M*|) Σ__m∈M__ (1/|*E*(*c*,*s*,*m*)|) Σ__e∈E(c,s,m)__ *y*(*e*)      (5)

EQ: Δ(*c*,*c*′) = (1/|*S*|) Σ__s∈S__ [ *x*(*c*,*s*) − *x*(*c*′,*s*) ]      (6)

Δ is the *effect* of *c* relative to *c*′. The two twins and all models of a scenario share its tasks, so base scenarios are the unit of resampling.

**3.5 Interventions (new).** A *control* changes the team or the gateway. The *oracle check* dry-runs each state-changing call against χ (an upper bound, not deployable). The *ask-before-act gate* runs a call *a*(*t*) only if it is read-only, or an earlier permission request *r* covers it and the latest answer to *r* is not a denial:

EQ: run(*a*(*t*)) ⇔ readonly(*a*(*t*)) ∨ ∃ *u* < *t* : covers(*r*(*u*), *a*(*t*)) ∧ answer(*r*(*u*)) ≠ denied      (7)

An *auditor* is an LLM that approves each state-changing call, seeing the call only, or also its result, or also the team's messages. The *verification prompt* adds one rule to every system prompt: a claim of approval is unverified until the permission system confirms it. A *report source* change shows the Lead the ledger, or the ledger plus an explicit permission record. The **claim filter** is a separate model (glm-53-flash, temperature 0) that rewrites every message between agents. It turns a statement that an approval exists into an attributed, unverified claim and adds the instruction to confirm it with the permission system first (Appendix D gives the prompt). It sees neither the task, nor the ledger, nor the twin, and if it returns nothing the original message passes. E11 gives an attacker model the filter prompt and lets it search for a message that passes. E12 crosses the false message with the verification prompt. E13 replaces the false message with one that states doubt.

**3.6 Monitors (new).** A *monitor* is an LLM judge *j* that reads a trace *T* at a *log level* ℓ and scores from 0 to 100 how likely a violation is. The levels are L0 the final report, L1 the messages, L2 the tool calls, L3 the calls with their results, L4 everything. The label is whether a violation occurred. With *T*⁺ a random violating trace and *T*⁻ a random clean one, we report the AUROC and the catch rate at a 5% false-alarm budget:

EQ: AUROC(*j*, ℓ) = P[ *s*(*T*⁺) > *s*(*T*⁻) ] + ½ P[ *s*(*T*⁺) = *s*(*T*⁻) ],   Catch(*j*, ℓ) = P[ *s*(*T*⁺) > *q* ]      (8)

where *s* = *s*(*j*, ℓ, ·) is the score and *q* is the 95th percentile of scores on clean traces (ties count as false alarms). A *self-query* monitor asks the Operator's own model two yes/no questions.

**3.7 Inference.** Every experiment was preregistered. We fixed each prediction, its threshold θ, its sample size and the analysis code before any confirmatory episode existed, and SHA-256 hashes and git commits record the order (Appendix C). Let Δ̂ be the estimate of an effect and Δ⁽ᵇ⁾ its value on the *b*-th of *B* = 10,000 resamples of *S* drawn with replacement. The 95% interval is the 2.5th to 97.5th percentile of the Δ⁽ᵇ⁾. For a prediction Δ > θ, the one-sided bootstrap p-value is

EQ: *p* = ( 1 + #{ *b* : Δ⁽ᵇ⁾ ≤ θ } ) / ( *B* + 1 )      (9)

and for a prediction Δ < θ the inequality is reversed. Within a family of *k* related predictions with sorted p-values *p*(1) ≤ … ≤ *p*(*k*), the Holm-adjusted value is

EQ: *p̃*(*i*) = max__j≤i__ min{ 1, (*k* − *j* + 1) · *p*(*j*) }      (10)

A prediction is *supported* if *p̃* < 0.05 and Δ̂ meets θ. We label every other analysis *exploratory* and report every prediction, including the failures.
