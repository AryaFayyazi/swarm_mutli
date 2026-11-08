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
