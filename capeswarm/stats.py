"""Cluster bootstrap over base scenarios (NEW in the sprint)."""
from __future__ import annotations

import numpy as np

B_DEFAULT = 10000


def cluster_table(df, key="scenario_id"):
    """Group a frame to one row per cluster (sum of each numeric column) -> dict of arrays + cluster order."""
    g = df.groupby(key)
    return g


def boot(cols: dict, fn, B: int = B_DEFAULT, seed: int = 0):
    """cols: {name: array (n_clusters,)} of per-cluster SUMS/values. fn(dict of arrays (B,n)) -> (B,) statistic.
    Returns (point, lo, hi). point = fn on the original data (shape (1,n))."""
    n = len(next(iter(cols.values())))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(B, n))
    sm = {k: np.asarray(v, float)[idx] for k, v in cols.items()}
    stat = np.asarray(fn(sm), float)
    point = float(np.asarray(fn({k: np.asarray(v, float)[None, :] for k, v in cols.items()}), float)[0])
    stat = stat[np.isfinite(stat)]
    if len(stat) == 0:
        return point, float("nan"), float("nan")
    return point, float(np.quantile(stat, 0.025)), float(np.quantile(stat, 0.975))


def holm(pvals: dict) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m = len(items)
    out, running = {}, 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return out


def boot_p_one_sided(cols, fn, B=B_DEFAULT, seed=0, null=0.0, greater=True):
    """One-sided bootstrap p-value for H: stat > null (greater) or < null."""
    n = len(next(iter(cols.values())))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(B, n))
    stat = np.asarray(fn({k: np.asarray(v, float)[idx] for k, v in cols.items()}), float)
    stat = stat[np.isfinite(stat)]
    p = (np.sum(stat <= null) + 1) / (len(stat) + 1) if greater else (np.sum(stat >= null) + 1) / (len(stat) + 1)
    return float(p)
