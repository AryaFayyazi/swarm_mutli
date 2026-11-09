"""Round 2 analysis (H20-H27) + descriptive extras. Reads outputs/raw/e9.jsonl, e10.jsonl, r2mon.jsonl. Writes results/round2.json. No API calls."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from capeswarm.load import load
import capeswarm.hyp2 as H2
from capeswarm.audit import structural
from capeswarm.runner import make_specs

RAW = ROOT / "outputs/raw"
e9 = load(RAW / "e9.jsonl")
res = {"counts": {"e9": int(len(e9))}}
res.update(H2.e9_rows(e9))
# filter behaviour (fail-open rate, how often the rewrite changed the message)
tot = ok = chg = 0
ex = None
for l in open(RAW / "e9.jsonl"):
    r = json.loads(l)
    for f in (r.get("filter") or []):
        tot += 1; ok += bool(f["ok"]); chg += bool(f["ok"] and f["out"].strip() != f["in"].strip())
        if ex is None and f["where"] == "peer_message" and f["ok"]:
            ex = f
res["_filter"] = {"calls": tot, "ok": ok, "fail_open": tot - ok, "changed": chg, "example": ex}

# exploratory E9 checks: (1) all finished episodes, not only complete scenarios; (2) the filter hops that returned a rewrite
from capeswarm.hyp import M4
_d = e9[e9.model.isin(M4) & (e9.cf == "unsafe")]
res["_e9_all"] = {n: {"V": round(float(H2.cell(_d, n).V.mean()), 4), "n": int(len(H2.cell(_d, n)))} for n in H2.CELLS}
_hop = {}
for l in open(RAW / "e9.jsonl"):
    r = json.loads(l)
    c = r["cfg"]
    if not r.get("out") or r["cf"] != "unsafe" or c["model"] not in M4 or c["topology"] != "relay1" or c.get("claim_filter") != "rewrite" or (r.get("control") or "none") != "none":
        continue
    st = {f["where"]: bool(f["ok"]) for f in (r.get("filter") or [])}
    key = "peer hop ok, brief hop ok" if st.get("peer_message") and st.get("lead_brief") else "peer hop ok, brief hop failed open" if st.get("peer_message") else "peer hop failed open"
    a = _hop.setdefault(key, [0, 0]); a[0] += 1; a[1] += int(r["out"]["V"])
res["_e9_filter_hops"] = {k: {"n": v[0], "V": round(v[1] / v[0], 4)} for k, v in _hop.items()}
p11 = RAW / "e11.jsonl"
if p11.exists() and p11.stat().st_size:
    res["counts"]["e11"] = int(len(load(p11)))
    res.update(H2.e11_rows(e9, load(p11)))
    sel = json.load(open(ROOT / "docs/filter_attacker_search.json")).get("selected")
    res["_e11_selected"] = sel
    for h in ("H28", "H29", "H30"):
        if h in res: print(h, res[h]["point"], res[h]["lo"], res[h]["hi"], res[h].get("p_holm"), res[h]["supported"])
p12 = RAW / "e12.jsonl"
if p12.exists() and p12.stat().st_size:
    res["counts"]["e12"] = int(len(load(p12)))
    res.update(H2.e12_rows(e9, load(p12)))
    if "H31" in res:
        r = res["H31"]; print("H31", r["point"], r["lo"], r["hi"], r.get("p_holm"), r["supported"], res["_2x2"])
# report-level: false assurance among violators, cells B vs C vs D
p10 = RAW / "e10.jsonl"
pm = RAW / "r2mon.jsonl"
if p10.exists() and pm.exists():
    e10 = load(p10)
    res["counts"]["e10"] = int(len(e10))
    mon = pd.DataFrame([json.loads(l) for l in open(pm)])[["episode_id", "monitor", "score"]]
    specs = {x["instance_id"]: x["user_email"] for x in make_specs(48, 5501)}
    ids = set(mon.episode_id); rule = []
    for fn in ("e9.jsonl", "e10.jsonl"):
        for l in open(RAW / fn):
            r = json.loads(l)
            if r["episode_id"] in ids and r.get("out"):
                led = [{"tool": e["tool"], "args": e["args"], "obs": e["obs"]} for e in r["ledger"] if not e.get("blocked")]
                rule.append({"episode_id": r["episode_id"], "monitor": "rule", "score": float(bool(structural(led, specs.get(r["instance_id"]))["unrecorded_state_changes"]))})
    res.update(H2.e10_rows(e9, e10, mon, pd.DataFrame(rule)))
(ROOT / "results/round2.json").write_text(json.dumps(res, indent=1, default=str))
for h in ("H20", "H21", "H22", "H23", "H24", "H25", "H26", "H27", "H28", "H29", "H30", "H31"):
    if h in res:
        r = res[h]; print(h, r["name"][:55], "pt", r["point"], "CI", r["lo"], r["hi"], "p_holm", r.get("p_holm"), "SUPPORTED" if r["supported"] else "not supported")
if "_cells" in res:
    for k, v in res["_cells"].items():
        print(k, "V", v["V"], "goal_safe", v["goal_safe"], "FA/V", v["FA_over_V"], "n", v["n_unsafe"], v["n_safe"])
print(res["_filter"]["calls"], "filter calls, fail-open", res["_filter"]["fail_open"], "changed", res["_filter"]["changed"])
