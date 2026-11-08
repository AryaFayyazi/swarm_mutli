# From sprint report to full paper: roadmap

The sprint report shows one mechanism (assurance laundering), one price list (controls) and one ladder (logs). A full paper
needs the following. Items are ordered by how much each one raises the claim, not by effort.

## Must have (reviewers will ask for these first)
1. **Frontier models.** Re-run E1 (solo, relay, peer vs none) and the ask-before-act gate on two or three closed models.
   Estimated cost: about 4,000 calls per model for E1's relay/peer slice. The sprint API only serves open-weight models, so this needs
   separate funding. The code path already exists: `capeswarm/llm.py` is the only provider-specific file.
2. **Adaptive attacker.** Replace the scripted peer message by an attacker agent that optimizes the message against the team
   (best-of-n, then a trained attacker). Question: does the ask-before-act gate still hold, and how much does it cost?
3. **Real logs.** Apply the ledger monitors to public swarm traces (Swarm Traces, AI Village transcripts) to check that the log
   ladder transfers from mock tools to real work. Labels will be weaker (no rule checker), so use human labels on a sample.
4. **More topologies.** Mesh teams, a shared message board (the improvised channel seen in real incidents), and K parallel
   Operators with majority approval. Question: does redundancy help or does the claim travel faster?

## Should have
5. **A formal model of claim propagation.** Each hop either verifies or relays. A small Markov model with a per-hop verification
   probability should predict the observed drop from brief to report, and should give the break-even verification cost at which the
   ask-before-act gate pays for itself. We have the hop data already (`capeswarm/hops.py`).
6. **Learned monitors** next to the prompted judges: a logistic probe over judge scores at each log level, trained on one family and
   tested on the others (leave-one-family-out), to separate "monitor needs the right log" from "monitor needs the right prompt".
7. **Human study (small).** Do human reviewers who read the final report alone, or report plus ledger, catch the false assurance?
   This turns the log ladder into a statement about people.
8. **Verification as a skill.** Fine-tune or prompt-tune one model to verify claims before acting, and test transfer to new
   scenario families. The sprint's verification-prompt result (H12) is the baseline to beat.

## Release plan
- Pip-installable `capeswarm` with `run`, `replay`, `audit` commands. Pre-deployment test: run your own agents on 96 matched instances.
- Traces and locks on a public hub; viewer on a static page.
- Responsible release: no optimized attack strings (see Appendix A of the report).

## What the sprint already locked in
Preregistered hypotheses H1–H17 with hashes (`results/prereg_*_lock.json`). A full paper can reuse them as "study 1" and
preregister the new studies in the same way.
