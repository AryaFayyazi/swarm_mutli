"""Cluster bootstrap over base scenarios (NEW in the sprint)."""
from __future__ import annotations

import numpy as np

B_DEFAULT = 10000


def boot_dist(cols: dict, fn, B: int = B_DEFAULT, seed: int = 0):
    """cols: {name: array (n_clusters,)} of per-cluster sums or values. fn(dict of arrays (B,n)) -> (B,) statistic.
    Returns (point estimate on the original data, bootstrap distribution)."""
    n = len(next(iter(cols.values())))
    rng = np.random.default_rng(seed)
    idx = rng.integers(0, n, size=(B, n))
    stat = np.asarray(fn({k: np.asarray(v, float)[idx] for k, v in cols.items()}), float)
    point = float(np.asarray(fn({k: np.asarray(v, float)[None, :] for k, v in cols.items()}), float)[0])
    return point, stat[np.isfinite(stat)]


def ci(stat, level=0.95):
    if len(stat) == 0:
        return float("nan"), float("nan")
    a = (1 - level) / 2
    return float(np.quantile(stat, a)), float(np.quantile(stat, 1 - a))


def p_le(stat, x):   # one-sided bootstrap p for H: parameter > x   (small when the distribution sits above x)
    if len(stat) == 0:
        return 1.0
    return float((np.sum(stat <= x) + 1) / (len(stat) + 1))


def p_ge(stat, x):   # one-sided bootstrap p for H: parameter < x
    if len(stat) == 0:
        return 1.0
    return float((np.sum(stat >= x) + 1) / (len(stat) + 1))


def holm(pvals: dict) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m, out, running = len(items), {}, 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return out
