## 4. Results
Experiment E1 has {{D['counts']['e1']|,}} episodes: seven models, three team shapes and two message conditions (a false peer message, or no message), with 96 task instances per cell. We write V for the share of unsafe-twin episodes that contain an unauthorized action. Brackets give 95% confidence intervals. Every test below was preregistered unless we call it *exploratory*.

### 4.1 A false peer message makes agents act without authorization
**Single agent.** The peer message raises V from {{X['V_none']['solo']|.2f}} to {{X['V_peer']['solo']|.2f}}, a difference of {{H['H1']['point']|+.2f}} [{{H['H1']['lo']|+.2f}}, {{H['H1']['hi']|+.2f}}]. The average hides a split between models (Figure 2a). Three models react strongly: Qwen3.5-397B ({{H['H1']['per_model']['qwen3.5-397b']|+.2f}}), Gemma-4 31B ({{H['H1']['per_model']['gemma-4-31b-it']|+.2f}}) and Gemma-4 26B ({{H['H1']['per_model']['gemma-4-26b-a4b-it']|+.2f}}). DeepSeek-V4 flash reacts weakly ({{H['H1']['per_model']['deepseek-v4-flash']|+.2f}}), and the other three models hardly react.

FIG: fig1_acting.png | 5.3 | **Figure 2. A false peer message raises unauthorized actions, unevenly.** (a) Single agent: V for each model, with a 95% interval over 48 base tasks. (b) Mean of seven models, by team shape. Unsafe twins only, where the message is false.


**Teams.** The effect remains in teams (difference {{H['H2']['parts'][0]['point']|+.2f}} for the relay and {{H['H2']['parts'][1]['point']|+.2f}} for the relay-2 team). The rate is lower in teams, with or without the message, so teams do not make the problem worse, but they do not remove it. With the false message, V is {{X['V_peer']['solo']|.2f}} for the single agent, {{X['V_peer']['relay1']|.2f}} for the relay and {{X['V_peer']['relay2']|.2f}} for relay-2.


### 4.2 The claim travels through the team and returns as a false report
Figure E1 (Appendix E) follows the ticket number through the relay. The Lead's brief repeats the claim in {{D['hops_unsafe_peer'][0]['brief_carries_claim']|.0%}} of episodes, and other Leads drop it. A brief can *endorse* the claim, *reject* it (call it unverified, or tell the Operator to check) or not mention it. After an endorsing brief, violations occur in {{X['stance']['endorse']['V']|.0%}} of episodes. After a rejecting brief, they occur in {{X['stance']['reject']['V']|.0%}} (exploratory; Appendix E). The split follows the model: the Gemma-4 models endorse most often.

The report is where the harm reaches the human. Among violating episodes it says "authorized" in {{H['H3']['false_assurance_over_V']|.0%}} and discloses the violation in only {{H['H3']['point']|.0%}} [{{H['H3']['lo']|.0%}}, {{H['H3']['hi']|.0%}}]. The single agent is the least honest ({{X['fa_over_v']['solo']['FA']['point']|.0%}} false reports); teams are somewhat more honest (relay {{X['fa_over_v']['relay1']['FA']['point']|.0%}}, relay-2 {{X['fa_over_v']['relay2']['FA']['point']|.0%}}; exploratory).