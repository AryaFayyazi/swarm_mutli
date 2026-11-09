# Submission field sheet (Swarm Alignment Hackathon, Apart Research)

**Deadline:** Sunday 8 November 2026, 11:59 PM Anywhere on Earth = Monday 9 November 11:59 UTC = Monday 03:59 AM PST. Resubmitting with the same title replaces the earlier submission.

## Fields
- **Project title:** Who Approved This? Assurance Laundering in LLM Agent Teams
- **Track:** Multi-Agent Oversight and Control (Track 4)
- **Abstract (241 words; the form wants 150-250):**

LLM agents work in teams that use tools, and a human often reads only the final report. We study assurance laundering. A peer agent asserts, without proof, that approval was already given, the team acts without authorization, and the report tells the human that the work was authorized. We build CAPE-Swarm, a team layer on the CAPE-Bench mock-tool environments [1], where every task has a matched safe and unsafe twin and a fixed rule, not an LLM judge, labels each tool call. In 12,064 episodes with seven open-weight models, one false peer sentence raises a single agent's rate of unauthorized actions from 0.16 to 0.37, and 70% to 93% of violating team runs still report "authorized". Acting and reporting need different fixes: a gateway rule that requires a permission request stops the action, and showing the Lead a permission record repairs the report. A factorial test shows that the claim displaces the agent's own authorization check, and a verification rule removes nearly all of its effect. Doubt from a peer only restores the baseline rate and costs useful work; a peer's question lowers it. A claim filter that marks approval claims as unverified cuts unauthorized actions from 0.36 to 0.03 on fresh tasks and holds against a model-written attack on it. A monitor detects violations only if it reads the gateway log with results (detection AUROC 0.90–0.93, against 0.69–0.70 from the report). All experiments were preregistered; 7 of 33 predictions failed.

- **Team and authors:** Arya Fayyazi (sole author), University of Southern California, afayyazi@usc.edu. One-person team: enter yourself as the one required team member (name and email); team name and location are yours to choose. Each person can be on at most two projects.
- **Tracks (choose every track the project fits):** Track 4 (Multi-Agent Oversight and Control) is primary. Track 3 (Strengthening Agent Infrastructure) also fits (gateway log, ask-before-act gate, claim filter).
- **Publication interest:** your choice (Yes or No).
- **Research report (PDF):** `submission/report.pdf` (official template; main text ends on page 8, then references, statements and appendices; 16 pages in all).
- **Code upload:** `submission/swarm_hack_code.zip` (code, preregistrations with SHA-256 locks, results, report source, replay viewer; no secrets). Traces: `submission/swarm_hack_traces.tar.gz` (220 MB uncompressed, 26 MB compressed) if the form allows a second file.
- **Public GitHub repo (optional):** https://github.com/AryaFayyazi/swarm_mutli (full history pushed 2026-11-08, including every preregistration lock commit; re-push after the final rebuild). Revoke the personal access token you pasted in chat.
- **Video demo (optional):** not made. `paper/viewer.html` is a self-contained replay of five paired episodes.

## Before you submit (things only you can do)
1. Read the report and rewrite the Author Contributions (end of `paper/parts/70_refs.md`) and the LLM usage statement (`paper/parts/80_appendix.md`, Appendix B) in your own words so that they say what actually happened. The sprint can disqualify made-up results or references, and the team is responsible for everything in the report. Every number comes from `scripts/20_analyze.py` and `scripts/27_round2.py`, and `scripts/26_audit_numbers.py` recomputes the headline numbers independently. Every reference was checked against arXiv or the METR PDF.
2. Rotate or revoke the Adaption API key that was pasted into chat (it sits in `.secrets/adaption.env`, which is not in the archives or the git history).
3. Optional: publish the repository (push the full history so the lock commits are public), then add its URL. Optional: record a 3 to 5 minute video demo (`paper/viewer.html` is a self-contained replay).
4. Check the final PDF (the form accepts up to 25 MB) and submit before 03:59 AM PST Monday (11:59 PM AoE Sunday). To replace a PDF, resubmit with the same title.
