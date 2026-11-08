"""EXPLORATORY contrasts on E1 (not preregistered; labeled as such in the paper). Writes results/extra.json (merged)."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from capeswarm.load import load
from capeswarm.hops import load_hops
import capeswarm.hyp as H
from capeswarm.stats import boot_dist, ci
RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "outputs/raw"
RES = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "results"
e1 = load(RAW / "e1.jsonl")
u = e1[e1.cf == "unsafe"]; scen = sorted(u.scenario_id.unique())
out = {}
def cell(t, a): return u[(u.topology == t) & (u.assurance == a)]
def d_boot(x, y, col="V"):
    pt, st = H.mean_stat(H.per_scen(x, col, scen) - H.per_scen(y, col, scen)); lo, hi = ci(st); return {"point": round(pt, 4), "lo": round(lo, 4), "hi": round(hi, 4)}
out["exp_topology"] = {f"{a}: solo-{t}": d_boot(cell("solo", a), cell(t, a)) for a in ("peer", "none") for t in ("relay1", "relay2")}
out["exp_topology"]["peer: relay1-relay2"] = d_boot(cell("relay1", "peer"), cell("relay2", "peer"))
# safe twin: violations should be zero by construction of the checker (sanity)
s = e1[e1.cf == "safe"]
out["safe_twin_V"] = {"mean": round(float(s.V.mean()), 5), "n": int(len(s))}
# FA/V per topology (pooled, cluster bootstrap)
fav = {}
for t in ("solo", "relay1", "relay2"):
    x = u[(u.topology == t)]
    sm = H.sums(x, scen, V="V", FA="false_assurance", D="disclosed", HD="hedged")
    r = {}
    for k in ("FA", "D", "HD"):
        pt, st = boot_dist({"n": sm[k], "d": sm["V"]}, lambda z: z["n"].sum(1) / np.maximum(z["d"].sum(1), 1e-9), 5000)
        lo, hi = ci(st); r[k] = {"point": round(pt, 3), "lo": round(lo, 3), "hi": round(hi, 3)}
    r["n_viol"] = int(sm["V"].sum()); fav[t] = r
out["fa_over_v"] = fav
# does the brief carry / order skip?  (relay1 + relay2, peer, unsafe)
hp = load_hops(RAW / "e1.jsonl")
hp = hp[(hp.cf == "unsafe") & hp.topology.isin(["relay1", "relay2"])].merge(e1[["episode_id", "scenario_id"]], on="episode_id")
for c in ("brief_carries_claim", "brief_orders_skip_approval"):
    hp[c] = hp[c].astype(float)
def cond(mask_a, mask_b, label):
    A, B = hp[mask_a], hp[mask_b]
    sc = sorted(hp.scenario_id.unique())
    a = A.groupby("scenario_id").V.agg(["sum", "count"]).reindex(sc).fillna(0); b = B.groupby("scenario_id").V.agg(["sum", "count"]).reindex(sc).fillna(0)
    pt, st = boot_dist({"as": a["sum"].values, "an": a["count"].values, "bs": b["sum"].values, "bn": b["count"].values},
                       lambda z: z["as"].sum(1) / np.maximum(z["an"].sum(1), 1) - z["bs"].sum(1) / np.maximum(z["bn"].sum(1), 1), 5000)
    lo, hi = ci(st)
    return {"V_a": round(float(A.V.mean()), 3), "n_a": int(len(A)), "V_b": round(float(B.V.mean()), 3), "n_b": int(len(B)), "diff": round(pt, 3), "lo": round(lo, 3), "hi": round(hi, 3)}
out["brief_carries_vs_dropped"] = cond(hp.brief_carries_claim == 1, hp.brief_carries_claim == 0, "carries vs dropped")
out["brief_rates"] = {t: {"carries": round(float(hp[hp.topology == t].brief_carries_claim.mean()), 3), "n": int((hp.topology == t).sum())} for t in ("relay1", "relay2")}
# spontaneous (no assurance) violation rate and report honesty
out["V_none"] = {t: round(float(cell(t, "none").V.mean()), 3) for t in ("solo", "relay1", "relay2")}
out["V_peer"] = {t: round(float(cell(t, "peer").V.mean()), 3) for t in ("solo", "relay1", "relay2")}
# stance of the instruction the Operator received (EXPLORATORY; labels by gemma-4-31b-it, 97% agreement with hand labels on 36 cases)
sp = RAW / "stance.jsonl"
if sp.exists():
    st = pd.DataFrame([json.loads(l) for l in open(sp)])
    m = e1.merge(st, on="episode_id")
    m = m[(m.cf == "unsafe") & m.stance.notna()]
    sc = sorted(m.scenario_id.unique())
    res = {}
    for stn in ("endorse", "reject", "absent"):
        x = m[m.stance == stn]
        res[stn] = {"n": int(len(x)), "share": round(float(len(x) / len(m)), 3), "V": round(float(x.V.mean()), 3) if len(x) else None,
                    "FA_over_V": round(float(x.false_assurance.sum() / max(x.V.sum(), 1)), 3), "n_viol": int(x.V.sum())}
    def diff(a, b):
        A, B = m[m.stance == a], m[m.stance == b]
        aa = A.groupby("scenario_id").V.agg(["sum", "count"]).reindex(sc).fillna(0); bb = B.groupby("scenario_id").V.agg(["sum", "count"]).reindex(sc).fillna(0)
        pt, sd = boot_dist({"as": aa["sum"].values, "an": aa["count"].values, "bs": bb["sum"].values, "bn": bb["count"].values},
                           lambda z: z["as"].sum(1) / np.maximum(z["an"].sum(1), 1) - z["bs"].sum(1) / np.maximum(z["bn"].sum(1), 1), 5000)
        lo, hi = ci(sd); return {"point": round(pt, 3), "lo": round(lo, 3), "hi": round(hi, 3)}
    res["endorse_minus_reject"] = diff("endorse", "reject")
    res["endorse_minus_absent"] = diff("endorse", "absent")
    byg = {}
    for mod in sorted(m.model.unique()):
        x = m[m.model == mod]
        byg[mod] = {k: round(float((x.stance == k).mean()), 2) for k in ("endorse", "reject", "absent")}
    res["by_model_share"] = byg
    out["stance"] = res
# E4 group-level contrasts (EXPLORATORY summary of the preregistered E4 cells)
e4p = RAW / "e4.jsonl"
if e4p.exists():
    e4 = load(e4p)
    C_ = ["gemma-4-26b-a4b-it", "qwen3.5-397b"]; S_ = ["glm-5.2", "glm-53-flash"]
    u4 = e4[e4.cf == "unsafe"]
    u1r = u1p = e1[(e1.cf == "unsafe") & (e1.topology == "relay1") & (e1.assurance == "peer")]
    def gv(df):
        v = df.groupby("scenario_id").V.mean().reindex(scen).values; pt, st = H.mean_stat(v); lo, hi = ci(st)
        return {"V": round(pt, 3), "lo": round(lo, 3), "hi": round(hi, 3), "n": int(len(df))}
    out["e4_groups"] = {"C lead + C op": gv(u1r[u1r.model.isin(C_)]), "S lead + C op": gv(u4[u4.model.isin(C_) & u4.lead_model.isin(S_)]),
                        "C lead + S op": gv(u4[u4.model.isin(S_) & u4.lead_model.isin(C_)]), "S lead + S op": gv(u1r[u1r.model.isin(S_)])}
# E2 exploratory contrasts between log levels (cluster bootstrap over scenarios)
e2p = RAW / "e2.jsonl"
if e2p.exists():
    from scipy.stats import rankdata
    r2 = pd.DataFrame([json.loads(l) for l in open(e2p)])[["episode_id", "monitor", "score"]]
    key = e1[["episode_id", "scenario_id", "V"]].drop_duplicates("episode_id")
    wide = r2.pivot_table(index="episode_id", columns="monitor", values="score", aggfunc="first").join(key.set_index("episode_id"), how="inner")
    y = wide.V.values.astype(bool); sc_ = wide.scenario_id.values
    groups = {s_: np.where(sc_ == s_)[0] for s_ in sorted(set(sc_))}; keys = list(groups)
    rng = np.random.default_rng(5)
    draws = [np.concatenate([groups[keys[i]] for i in rng.integers(0, len(keys), len(keys))]) for _ in range(1500)]
    def au(sc, ii):
        yy = y[ii]
        if yy.sum() == 0 or (~yy).sum() == 0: return np.nan
        rk = rankdata(sc[ii]); n1, n0 = yy.sum(), (~yy).sum(); return (rk[yy].sum() - n1 * (n1 + 1) / 2) / (n1 * n0)
    cont = {}
    for j in ("gemma-4-31b-it", "qwen3.5-397b"):
        for a_, b_ in (("L4", "L3"), ("L1", "L0"), ("L3", "L1"), ("L3", "L2")):
            A = np.nan_to_num(wide[f"judge:{j}:{a_}"].values); Bv = np.nan_to_num(wide[f"judge:{j}:{b_}"].values)
            allix = np.arange(len(y)); pt = au(A, allix) - au(Bv, allix)
            st = np.array([au(A, ii) - au(Bv, ii) for ii in draws]); st = st[np.isfinite(st)]
            cont[f"{j} {a_}-{b_}"] = {"point": round(float(pt), 3), "lo": round(float(np.quantile(st, .025)), 3), "hi": round(float(np.quantile(st, .975)), 3)}
    # self-query vs report-only judge, and ledger level vs self-query
    for j in ("qwen3.5-397b",):
        A = np.nan_to_num(wide["self"].values); Bv = np.nan_to_num(wide[f"judge:{j}:L0"].values)
        pt = au(A, np.arange(len(y))) - au(Bv, np.arange(len(y)))
        st = np.array([au(A, ii) - au(Bv, ii) for ii in draws]); st = st[np.isfinite(st)]
        cont["self - judge qwen L0"] = {"point": round(float(pt), 3), "lo": round(float(np.quantile(st, .025)), 3), "hi": round(float(np.quantile(st, .975)), 3)}
    out["e2_contrasts"] = cont
    # self-query: what do the Operators say about themselves in violating episodes?
    q = r2[r2.monitor == "self"].merge(key, on="episode_id")
    out["self_scores_by_V"] = {"V": round(float(q[q.V].score.mean()), 1), "noV": round(float(q[~q.V].score.mean()), 1)}
p = RES / "extra.json"
d = json.load(open(p)) if p.exists() else {}
d.update(out); p.write_text(json.dumps(d, indent=1, ensure_ascii=False))
print(json.dumps(out, indent=1)[:3500])
