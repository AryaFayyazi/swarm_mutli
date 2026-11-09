## 6. Conclusion
One unverified sentence from a peer agent can make an agent team act without authorization, and then report the work as authorized. How much depends on the model, the team shape and the Lead. The fixes work on different parts of the problem. A permission record repairs the report. An ask-before-act gate stops the action. A claim filter, which marks approval claims as unverified, removes most of the harm at no measurable cost in our tests. The filter held against a message written by an attacker who knew it, but a message with no approval claim would pass it, so it should sit behind the gate. @@E12CONC@@ A monitor must read the gateway log with tool results to see the violation. We preregistered {{X['nh']}} hypotheses and report all of them. {{X['nfail_word']}} failed ({{X['failed_ids']}}). We release the traces, a replay viewer and a ledger auditor.

## Code and Data
Code, traces, locks and the replay viewer are in `swarm_hack/` (README marks preexisting and new code). Every number comes from `scripts/20_analyze.py` and `scripts/27_round2.py`.

## Author Contributions
A.F. is the only author. A.F. is responsible for all claims, results and conclusions in this report. Claude Code (an AI assistant; Appendix B) helped only with writing code and with drafting the first version of the report.
