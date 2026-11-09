# Submission field sheet (Swarm Alignment Hackathon, Apart Research)

**Deadline:** Sunday 8 November 2026, 11:59 PM Anywhere on Earth = Monday 9 November 11:59 UTC = Monday 03:59 AM PST. Resubmitting with the same title replaces the earlier submission.

## Fields
- **Project title:** Who Approved This? Assurance Laundering in LLM Agent Teams
- **Track:** Multi-Agent Oversight and Control (Track 4)
- **Abstract (199 words; the form wants 150-250):**

Teams of AI agents act with tools, and humans often read only the final report. We study assurance laundering: an unverified claim of approval from a peer agent travels through a team, leads an agent to act without authorization, and returns to the human as a confident, false report. We built CAPE-Swarm, a team layer on CAPE-Bench with matched safe and unsafe twins and rule-based labels (no LLM judge). We preregistered 18 hypotheses and ran 10,368 episodes of seven open-weight models. A false peer assurance raised unauthorized actions in a solo agent from 0.16 to 0.37 (+0.21, 95% CI [+0.16, +0.25]), unevenly: three models reacted strongly and three hardly at all. Teams lowered violation rates, but 82% of violations were reported as authorized. Acting and reporting need different fixes. A permission-system record cut false reports by 68% with no measurable change in actions. An ask-before-act gateway rule cut violations to 0.5% for a 5-point utility cost. Auditors and a verification prompt left about 9%. A monitor reading the gateway ledger with tool results reached AUROC 0.90–0.93, while the report alone (0.69–0.70) did not. Three hypotheses failed and are reported. We release traces, a replay viewer and a ledger auditor.

- **Team and authors:** Arya Fayyazi (sole author), University of Southern California, afayyazi@usc.edu. One-person team: enter yourself as the one required team member (name and email); team name and location are yours to choose. Each person can be on at most two projects.
- **Tracks (choose every track the project fits):** Track 4 (Multi-Agent Oversight and Control) is primary. Track 3 (Strengthening Agent Infrastructure) also fits (gateway log, ask-before-act gate, claim filter).
- **Publication interest:** your choice (Yes or No).
- **Research report (PDF):** `submission/report.pdf` (official template, main text 8 pages, then references and appendices).
- **Code upload:** `submission/swarm_hack_code.zip` (code, preregistrations with SHA-256 locks, results, report source, replay viewer; no secrets). Traces: `submission/swarm_hack_traces.tar.gz` (220 MB uncompressed, 26 MB compressed) if the form allows a second file.
- **Public GitHub repo (optional):** not created (git CLI `gh` is not installed here). If you publish the repo, push the full history so the lock commits are public, then add the URL to the report's "Code and Data" section and rebuild.
- **Video demo (optional):** not made. `paper/viewer.html` is a self-contained replay of five paired episodes.

## Before you submit (things only you can do)
1. Read the report and rewrite the Author Contributions (end of `paper/parts/70_refs.md`) and the LLM usage statement (`paper/parts/80_appendix.md`, Appendix B) in your own words so that they say what actually happened. The sprint can disqualify made-up results or references, and the team is responsible for everything in the report. Every number comes from `scripts/20_analyze.py` and `scripts/27_round2.py`, and `scripts/26_audit_numbers.py` recomputes the headline numbers independently. Every reference was checked against arXiv or the METR PDF.
2. Rotate or revoke the Adaption API key that was pasted into chat (it sits in `.secrets/adaption.env`, which is not in the archives or the git history).
3. Optional: publish the repository (push the full history so the lock commits are public), then add its URL. Optional: record a 3 to 5 minute video demo (`paper/viewer.html` is a self-contained replay).
4. Check the final PDF (the form accepts up to 25 MB) and submit before 03:59 AM PST Monday (11:59 PM AoE Sunday). To replace a PDF, resubmit with the same title.
