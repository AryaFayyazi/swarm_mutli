# Deviations from prereg v1

- 2026-11-07: the header of PREREG_v1.md says "written ~18:10 PST". The lock file time (17:56 PST) is the authoritative time. Typo only; no content change.

- 2026-11-07 18:2x: prereg_v1_2_lock.json fixes the monitor (E2) code and the analysis code (stats.py, hyp.py, load.py) before any confirmatory outcome was read. No new hypotheses. The metric functions (auroc, catch_at_budget) were unit-checked on synthetic data.
- 2026-11-07 (later): `capeswarm/hyp.py` and `capeswarm/stats.py` were rewritten so that each preregistered hypothesis (a
  conjunction of conditions) yields ONE decisive one-sided bootstrap p-value (largest component p), which feeds the Holm
  correction promised in PREREG_v1. The family H1–H7 is Holm-corrected; H12–H14 form the addendum family. Point-estimate
  conditions are unchanged from the preregistration; "V under ask_gate <= 0.02" is judged on the point estimate. No
  confirmatory outcome had been read; the code was tested on the dev seed (7001) and on synthetic data only.
  `capeswarm/hops.py` (claim survival) and `scripts/20_analyze.py` (driver) are new and locked in `prereg_v1_3_lock.json`.
- The Python process that runs E1/E3 loaded `llm.py/swarm.py/runner.py` at launch. `swarm.py` and `runner.py` were edited
  afterwards only to ADD the `prompt_defense` option and mixed-model episode ids (hashes in prereg_v1_1_lock.json);
  every E1/E3 code path is unchanged when the option is off.
- 2026-11-07 (later): Addendum 2 (E5 wording robustness, E6 test–retest) added to PREREG_v1_1_addendum.md and locked in
  `prereg_v1_4_lock.json` before any confirmatory outcome was read. `swarm.py` gained three assurance wordings (the `peer`
  wording and every E1/E3 code path are unchanged); `10_confirm.py` gained jobs e5/e6; `hyp.py`/`20_analyze.py` gained e5_rows/e6_rows.
  The queue order is now E3b → E4 → E5 → E6 → E2 (one process at a time, because the API limit is per user).
- 2026-11-07 (later): Addendum 3 (E7 diverse auditor H17; leave-one-model-out; rule-monitor baseline in E2; auditor fail-open count) added
  and locked in `prereg_v1_5_lock.json` before any confirmatory outcome was read. `runner.py` episode ids gained `auditor_model`.
- 2026-11-07 (later): EXPLORATORY flag `brief_orders_skip_approval` (regex) added to `capeswarm/hops.py` after the lock and before any outcome was read; it is reported as exploratory in the paper and is not part of any hypothesis.
- 2026-11-08 ~21:30: BUG FIX in `scripts/20_analyze.py` (descriptive hop table only): boolean hop columns with missing values (solo has none) were dropped by `mean(numeric_only=True)`; they are now cast to float. No hypothesis row is affected. Found after E1 finished; E1 hypothesis rows H1-H3 are identical before and after.
- 2026-11-08 ~22:00: the regex flag `brief_orders_skip_approval` was found (by reading 28+40 matched sentences) to mix endorsements with protective rules and with quotes that reject the claim; it is NOT used in the paper. Replaced by an EXPLORATORY model label (scripts/12_brief_stance.py, gemma-4-31b-it, 35/36 agreement with hand labels) of the instruction the Operator received. Both are exploratory and outside every hypothesis.
- 2026-11-08 ~00:40: DISPLAY FIX in `capeswarm/hyp.py` `finish()`: rows that carry a point-estimate criterion only (H9 self-query AUROC >= 0.75, H11 oracle V = 0) have no inferential test; they were shown as "not supported" because their placeholder p was 1.0. They now use their stated criterion (`no_test`). No other row changes; H1-H8 outputs are unchanged.
- 2026-11-08 ~03:15: THROUGHPUT ONLY. E2 (scripts/11_monitor.py) ran at ~57 jobs/min because the per-model concurrency cap of the slow judge was 14; it was stopped after ~620 jobs, the cap raised to 40 and the episode semaphore to 220, and it was resumed (finished jobs are skipped). Prompts, models, samples and scoring are unchanged. E7 and the stance labels were re-queued after it (scripts/queue_final.sh).
- 2026-11-08 ~05:15: THROUGHPUT ONLY. E7 slowed to ~1 episode per 2 min (GLM-5.2 auditor calls hit gateway timeouts behind a per-model cap of 14). It was stopped at 244/384 episodes and resumed with per-model concurrency 40 (env SWARM_PMC; default unchanged at 14). Finished episodes are kept; prompts, models and scoring are unchanged. The stance labels run after it (scripts/queue_e7b.sh).
- 2026-11-08 ~05:55: ROBUSTNESS EXTENSION (exploratory, after seeing results): an independent judge from a model family that never acted in the E2 traces (glm-5.2) scores the same 768 traces at L0-L4 (scripts/11_monitor.py with env JUDGES/OUTNAME/SKIP_SELF; defaults unchanged). Output goes to outputs/raw/e2x.jsonl and is NOT part of H7 (which stays "both preregistered judges"). Prompted by an independent LLM review (results/review_r1.json).
- 2026-11-08 ~06:10: the independent-judge robustness run was changed from glm-5.2 (17-32 s per call, empty outputs at L3) to glm-53-flash, levels L0 and L3 only, one sample, max_out 6000 (env LEVELS, JNS, JUDGE_MAXOUT; defaults unchanged). It answers one question: does L3 beat L0 for a judge family that never acted in the traces? Exploratory; not part of H7.
