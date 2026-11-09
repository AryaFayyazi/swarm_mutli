"""Independent audit: recompute headline numbers from the raw JSONL with plain Python (no pandas, no capeswarm.hyp) and compare with
results/*.json. Exits non-zero on any mismatch beyond rounding."""
import json, sys
from collections import defaultdict
from pathlib import Path
R = Path(__file__).resolve().parents[1]
RAW = R / "outputs/raw"
H = json.load(open(R / "results/hypotheses.json")); X = json.load(open(R / "results/extra.json"))
M4 = ["gemma-4-26b-a4b-it", "gemma-4-31b-it", "qwen3.5-397b", "deepseek-v4-flash"]
def rows(name):
    for l in open(RAW / name):
        r = json.loads(l)
        if r.get("out"): yield r
bad = []
def check(label, mine, theirs, tol=0.0006):
    ok = abs(mine - theirs) <= tol
    print(f"{'OK ' if ok else 'BAD'} {label:58s} audit={mine:.4f} pipeline={theirs:.4f}")
    if not ok: bad.append(label)
# --- E1: V by topology x assurance (unsafe twins), mean over episodes (equal cells => equals equal-weight mean of models)
V = defaultdict(list); viol = defaultdict(lambda: [0, 0, 0, 0])
for r in rows("e1.jsonl"):
    c = r["cfg"]
    if r["cf"] != "unsafe": continue
    V[(c["topology"], c["assurance"])].append(float(r["out"]["V"]))
    if r["out"]["V"]:
        v = viol[c["topology"]]; v[0] += 1; v[1] += r["out"]["report_status"] == "authorized"; v[2] += r["out"]["report_status"] == "not_authorized"
for t in ("solo", "relay1", "relay2"):
    check(f"E1 V none {t}", sum(V[(t, "none")]) / len(V[(t, "none")]), X["V_none"][t], 0.0006)
    check(f"E1 V peer {t}", sum(V[(t, "peer")]) / len(V[(t, "peer")]), X["V_peer"][t], 0.0006)
d = sum(V[("solo", "peer")]) / len(V[("solo", "peer")]) - sum(V[("solo", "none")]) / len(V[("solo", "none")])
check("H1 point (solo peer - none)", d, H["H1"]["point"], 0.0006)
tot = sum(v[0] for v in viol.values()); check("H3 disclosed/V pooled", sum(v[2] for v in viol.values()) / tot, H["H3"]["point"], 0.0006)
check("H3 false-assurance/V pooled", sum(v[1] for v in viol.values()) / tot, H["H3"]["false_assurance_over_V"], 0.0006)
# --- E3: gateway rule and baseline on M4
base = [float(r["out"]["V"]) for r in rows("e1.jsonl") if r["cf"] == "unsafe" and r["cfg"]["topology"] == "relay1" and r["cfg"]["assurance"] == "peer" and r["cfg"]["model"] in M4]
check("E3 baseline V (relay, peer, M4)", sum(base) / len(base), H["_descriptive_controls"]["baseline"]["V"], 0.0006)
g = defaultdict(list)
for r in rows("e3.jsonl"):
    if r["cf"] == "unsafe": g[r.get("control") or "none", r["cfg"].get("report_source", "peer")].append(float(r["out"]["V"]))
check("E3 ask_gate V", sum(g[("ask_gate", "peer")]) / len(g[("ask_gate", "peer")]), H["_descriptive_controls"]["ask_gate"]["V"], 0.0006)
check("E3 pdp V", sum(g[("pdp", "peer")]) / len(g[("pdp", "peer")]), H["_descriptive_controls"]["pdp"]["V"], 0.0006)
check("E3 aud_trace V", sum(g[("aud_trace", "peer")]) / len(g[("aud_trace", "peer")]), H["_descriptive_controls"]["aud_trace"]["V"], 0.0006)
# --- E2: AUROC at L0 and L3 for the Qwen judge, via pairwise definition (no rank code shared with the pipeline)
lab = {r["episode_id"]: bool(r["out"]["V"]) for r in rows("e1.jsonl")}
sc = defaultdict(dict)
for l in open(RAW / "e2.jsonl"):
    r = json.loads(l); sc[r["monitor"]][r["episode_id"]] = r["score"] if r["score"] == r["score"] else 0.0
def auc(mon):
    pos = [s for e, s in sc[mon].items() if lab.get(e)]; neg = [s for e, s in sc[mon].items() if e in lab and not lab[e]]
    w = sum((p > n) + 0.5 * (p == n) for p in pos for n in neg)
    return w / (len(pos) * len(neg))
tb = H["_table"]
for m in ("judge:qwen3.5-397b:L0", "judge:qwen3.5-397b:L3", "judge:gemma-4-31b-it:L3", "self"):
    check(f"E2 AUROC {m}", auc(m), tb[m]["auroc"], 0.0006)

# --- Round 2 (E9): recompute cells from the raw file with plain Python (own definition of "complete scenario")
import os
if (R / "results/round2.json").exists():
    R2 = json.load(open(R / "results/round2.json"))
    def cellname(c, ctl):
        k = bool(c.get("assurance_text")); f = c.get("claim_filter") or ""
        if c.get("stealth") or c["topology"] != "relay1": return None
        a = c["assurance"]
        if a == "none" and ctl == "none" and not f and not k: return "A"
        if a == "peer" and ctl == "none" and not f and not k: return "B"
        if a == "peer" and ctl == "none" and f and not k: return "C"
        if a == "peer" and ctl == "ask_gate" and not f and not k: return "D"
        if a == "peer" and ctl == "none" and not f and k: return "G"
        if a == "peer" and ctl == "none" and f and k: return "H"
    got = defaultdict(lambda: defaultdict(dict))        # scenario -> (cell, cf, model) -> row
    for r in rows("e9.jsonl"):
        if r["cfg"]["model"] not in M4: continue
        n = cellname(r["cfg"], r.get("control") or "none")
        if n: got[r["scenario_id"]][(n, r["cf"], r["cfg"]["model"])] = r["out"]
    need = [(n, "unsafe") for n in "ABCDGH"] + [(n, "safe") for n in "BCD"]
    comp = [sc for sc, d in got.items() if all((n, cf, m) in d for n, cf in need for m in M4)]
    check("E9 number of complete base scenarios", len(comp), R2["_n_clusters"], 0.0)
    for n in "ABCDGH":
        v = [float(got[sc][(n, "unsafe", m)]["V"]) for sc in comp for m in M4]
        check(f"E9 V cell {n} (pooled, equal cells)", sum(v) / len(v), R2["_cells"][n]["V"], 0.0006)
    for n in "BCD":
        v = [float(got[sc][(n, "safe", m)]["goal_gt"]) for sc in comp for m in M4]
        check(f"E9 goal on safe twins, cell {n}", sum(v) / len(v), R2["_cells"][n]["goal_safe"], 0.0006)
    check("H21 point (C - B)", sum(float(got[sc][("C", "unsafe", m)]["V"]) - float(got[sc][("B", "unsafe", m)]["V"]) for sc in comp for m in M4) / (len(comp) * 4), R2["H21"]["point"], 0.0006)
    check("H25 point (goal C - goal D)", sum(float(got[sc][("C", "safe", m)]["goal_gt"]) - float(got[sc][("D", "safe", m)]["goal_gt"]) for sc in comp for m in M4) / (len(comp) * 4), R2["H25"]["point"], 0.0006)
print("\nALL MATCH" if not bad else f"\nMISMATCHES: {bad}")
sys.exit(1 if bad else 0)
