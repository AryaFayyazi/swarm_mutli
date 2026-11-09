## 6. Conclusion
A single unverified sentence from a peer agent is enough to make some agent teams act without authorization and then report the work as authorized. How much depends on the model, on the team shape and on the Lead. The fixes are separate and cheap to price. An explicit permission record repairs the report. A structural ask-before-act gateway rule stops the action. Prompts and auditors help but leave a residual. A monitor must read the gateway ledger with tool results to see the violation. We preregistered {{X['nh']}} hypotheses and report all of them; {{X['nfail_word'].lower()}} failed ({{X['failed_ids']}}). We release the traces, a replay viewer and a ledger auditor.

## Code and Data
Code: `swarm_hack/` (README marks preexisting and new code), replay viewer `paper/viewer.html`, ledger auditor `python -m capeswarm.audit`. Data: all traces (`outputs/raw/*.jsonl`), preregistrations and locks (`docs/`, `results/`). Every number comes from `scripts/20_analyze.py` and `scripts/27_round2.py`.

## Author Contributions
A.F. is the only author. A.F. is responsible for all claims, results and conclusions in this report. Claude Code (an AI assistant; Appendix B) helped only with writing code and with drafting the first version of the report.
