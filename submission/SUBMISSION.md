# Submission field sheet (Swarm Alignment Hackathon, Apart Research)

**Deadline:** Sunday 8 November 2026, 11:59 PM Anywhere on Earth = Monday 9 November 11:59 UTC = Monday 03:59 AM PST. Resubmitting with the same title replaces the earlier submission.

## Fields
- **Project title:** Who Approved This? Assurance Laundering in LLM Agent Teams
- **Track:** Multi-Agent Oversight and Control (Track 4)
- **Abstract (199 words; the form wants 150-250):**

Teams of AI agents act with tools, and humans often read only the final report. We study assurance laundering: an unverified claim of approval from a peer agent travels through a team, leads an agent to act without authorization, and returns to the human as a confident, false report. We built CAPE-Swarm, a team layer on CAPE-Bench with matched safe and unsafe twins and rule-based labels (no LLM judge). We preregistered 18 hypotheses and ran 10,368 episodes of seven open-weight models. A false peer assurance raised unauthorized actions in a solo agent from 0.16 to 0.37 (+0.21, 95% CI [+0.16, +0.25]), unevenly: three models reacted strongly and three hardly at all. Teams lowered violation rates, but 82% of violations were reported as authorized. Acting and reporting need different fixes. A permission-system record cut false reports by 68% with no measurable change in actions. An ask-before-act gateway rule cut violations to 0.5% for a 5-point utility cost. Auditors and a verification prompt left about 9%. A monitor reading the gateway ledger with tool results reached AUROC 0.90–0.93, while the report alone (0.69–0.70) did not. Three hypotheses failed and are reported. We release traces, a replay viewer and a ledger auditor.

- **Authors and affiliations:** Arya Fayyazi, University of Southern California. **ADD every team member and affiliation before submitting** (the report header lists one author only). Each person can be on at most two projects.
- **Research report (PDF):** `submission/report.pdf` (official template, main text 8 pages, then references and appendices).
- **Code upload:** `submission/swarm_hack_code.zip` (code, preregistrations with SHA-256 locks, results, report source, replay viewer; no secrets). Traces: `submission/swarm_hack_traces.tar.gz` (220 MB uncompressed, 26 MB compressed) if the form allows a second file.
- **Public GitHub repo (optional):** not created (git CLI `gh` is not installed here). If you publish the repo, push the full history so the lock commits are public, then add the URL to the report's "Code and Data" section and rebuild.
- **Video demo (optional):** not made. `paper/viewer.html` is a self-contained replay of five paired episodes.

## Before you submit (things only you can do)
1. Add the other authors and affiliations (edit `paper/parts/00_header.md`, then `python scripts/25_summary.py && python paper/assemble.py && python paper/build_report.py`).
2. Read the report and rewrite the Author Contributions (`paper/parts/60_conclusion_code.md`) and the LLM usage statement (`paper/parts/80_appendix.md`, Appendix B) in your own words so that they say what actually happened. The template says the report should be primarily written by the team, and the sprint can disqualify made-up results or references. Every number comes from `scripts/20_analyze.py`, and `scripts/26_audit_numbers.py` recomputes the headline numbers independently. Every reference was checked against arXiv or the METR PDF.
3. Rotate or revoke the Adaption API key that was pasted into chat (it sits in `.secrets/adaption.env`, which is not in the archives or the git history).
4. Optional: publish the repository, then add its URL.
