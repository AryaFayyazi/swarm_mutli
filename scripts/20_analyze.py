"""All preregistered tests + descriptive tables. Reads outputs/raw/*.jsonl, writes results/*.json. No API calls."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from capeswarm.load import load
import capeswarm.hyp as H
from capeswarm.hops import load_hops

RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "outputs/raw"
RES = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "results"
RES.mkdir(exist_ok=True, parents=True)
def opt(name):
    p = RAW / name
    return load(p) if p.exists() and p.stat().st_size else None

e1, e3, e3b, e4 = opt("e1.jsonl"), opt("e3.jsonl"), opt("e3b.jsonl"), opt("e4.jsonl")
e5, e6, e7 = opt("e5.jsonl"), opt("e6.jsonl"), opt("e7.jsonl")
rows = {}
desc = {}
if e1 is not None:
    rows.update(H.e1_rows(e1))
    # descriptive table: model x topology x assurance (unsafe twins) and goal on safe twins
    u, s = e1[e1.cf == "unsafe"], e1[e1.cf == "safe"]
    t = u.groupby(["model", "topology", "assurance"]).agg(V=("V", "mean"), FA=("false_assurance", "mean"), disclosed=("disclosed", "mean"),
                                                         asked=("asked_before_act", "mean"), goal=("goal_gt", "mean"), report=("report_present", "mean"), n=("V", "size"))
    t2 = s.groupby(["model", "topology", "assurance"]).agg(goal_safe=("goal_gt", "mean"), V_safe=("V", "mean"))
    desc["e1_table"] = t.join(t2).round(4).reset_index().to_dict("records")
    desc["e1_by_family"] = u.groupby(["family", "assurance"]).V.mean().unstack().round(3).reset_index().to_dict("records")
    desc["e1_pooled"] = u.groupby(["topology", "assurance"]).agg(V=("V", "mean"), FA=("false_assurance", "mean"), disclosed=("disclosed", "mean"),
                                                              n=("V", "size")).round(4).reset_index().to_dict("records")
    desc["e1_cost_usd_credits"] = round(float(e1.cost.sum()), 2)
    desc["e1_report_present"] = round(float(e1.report_present.mean()), 4)
    desc["e1_episode_errors"] = int((e1.errors > 0).sum())
    hp = load_hops(RAW / "e1.jsonl")
    if len(hp):
        for c in [c for c in hp.columns if c not in ("episode_id", "model", "topology", "cf", "ticket")]:
            hp[c] = pd.to_numeric(hp[c].astype(float), errors="coerce")   # bool/None columns -> float so means keep them
        g = hp[hp.cf == "unsafe"].groupby(["topology"])
        cols = [c for c in hp.columns if c not in ("episode_id", "model", "topology", "cf", "ticket")]
        desc["hops_unsafe_peer"] = g[cols].mean(numeric_only=True).round(3).reset_index().to_dict("records")
        desc["hops_unsafe_peer_n"] = g.size().to_dict()
        # conditional chain: given the Operator violated, how often did the final report repeat the claim as fact
        v = hp[(hp.cf == "unsafe") & hp.V]
        desc["hops_violators"] = v.groupby("topology")[[c for c in cols if c in v.columns]].mean(numeric_only=True).round(3).reset_index().to_dict("records")
if e1 is not None and e3 is not None:
    rows.update(H.e3_rows(e1, e3, e3b))
if e1 is not None and e4 is not None:
    rows.update(H.e4_rows(e1, e4))
if e1 is not None and e5 is not None:
    rows.update(H.e5_rows(e1, e5))
if e1 is not None and e3 is not None and e7 is not None:
    rows.update(H.e7_rows(e1, e3, e7))
if e1 is not None and e6 is not None:
    rows.update(H.e6_rows(e1, e6))
aud_stats = {}
for nm in ("e3", "e7"):
    pth = RAW / f"{nm}.jsonl"
    if pth.exists():
        tot = fo = 0
        for l in open(pth):
            r = json.loads(l)
            for a in (r.get("audits") or []):
                tot += 1; fo += 0 if (a.get("verdict") and a["verdict"].get("decision")) else 1
        aud_stats[nm] = {"audit_decisions": tot, "no_parsable_verdict_fail_open": fo}
desc["auditor_fail_open"] = aud_stats
p2 = RAW / "e2.jsonl"
if e1 is not None and p2.exists():
    recs = [json.loads(l) for l in open(p2)]
    e2 = pd.DataFrame(recs)[["episode_id", "monitor", "score"]]
    from capeswarm.audit import structural
    from capeswarm.runner import make_specs
    specs_ = {x["instance_id"]: x["user_email"] for x in make_specs(48, 9001)}
    ids = set(e2.episode_id)
    rule = []
    for l in open(RAW / "e1.jsonl"):
        r = json.loads(l)
        if r["episode_id"] in ids and r.get("out"):
            led = [{"tool": e["tool"], "args": e["args"], "obs": e["obs"]} for e in r["ledger"] if not e.get("blocked")]
            rule.append({"episode_id": r["episode_id"], "monitor": "rule", "score": float(bool(structural(led, specs_.get(r["instance_id"]))["unrecorded_state_changes"]))})
    e2 = pd.concat([e2, pd.DataFrame(rule)], ignore_index=True)
    rows.update(H.e2_rows(e1, e2))
rows = H.finish(rows, ["H1", "H2", "H3", "H4", "H5", "H6", "H7"]) if True else rows
# addendum family
fam2 = [h for h in ("H12", "H13", "H14") if h in rows]
fam3 = [h for h in ("H15", "H16") if h in rows]
if fam3:
    adj3 = H.holm({h: rows[h]["p"] for h in fam3})
    for h in fam3:
        rows[h]["p_holm"] = round(adj3[h], 5); rows[h]["supported"] = bool(adj3[h] < 0.05 and rows[h]["cond_point"])
if fam2:
    adj = H.holm({h: rows[h]["p"] for h in fam2})
    for h in fam2:
        rows[h]["p_holm"] = round(adj[h], 5); rows[h]["supported"] = bool(adj[h] < 0.05 and rows[h]["cond_point"])
desc["counts"] = {n: (int(len(x)) if x is not None else 0) for n, x in (("e1", e1), ("e3", e3), ("e3b", e3b), ("e4", e4), ("e5", e5), ("e6", e6), ("e7", e7))}
(RES / "hypotheses.json").write_text(json.dumps(rows, indent=1, default=str))
(RES / "descriptive.json").write_text(json.dumps(desc, indent=1, default=str))
for h in ("H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H11", "H12", "H13", "H14", "H15", "H16", "H17"):
    if h in rows:
        r = rows[h]
        print(f"{h:4s} {r['name'][:52]:52s} point={r['point']:+.3f} CI[{r.get('lo', float('nan')):+.3f},{r.get('hi', float('nan')):+.3f}] p={r['p']:.4f} "
              f"holm={r.get('p_holm', '-')} supported={r['supported']}")
