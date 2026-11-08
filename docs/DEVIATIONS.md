# Deviations from prereg v1

- 2026-11-07: the header of PREREG_v1.md says "written ~18:10 PST". The lock file time (17:56 PST) is the authoritative time. Typo only; no content change.

- 2026-11-07 18:2x: prereg_v1_2_lock.json fixes the monitor (E2) code and the analysis code (stats.py, hyp.py, load.py) before any confirmatory outcome was read. No new hypotheses. The metric functions (auroc, catch_at_budget) were unit-checked on synthetic data.
