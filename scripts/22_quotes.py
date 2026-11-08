"""Illustrative pair for the paper, chosen by a FIXED rule (not by eye): the first scenario (sorted id) in E1, relay1 + peer, unsafe twin,
where (a) the GLM-5.2 team had no violation, asked for permission before acting, and its instruction to the Operator was labeled "reject"
(scripts/12_brief_stance.py), AND (b) the Qwen3.5-397B team's instruction was labeled "endorse", it had a violation, and its final report
says "authorized". Writes results/extra.json['quotes'] with verbatim sentences (markdown marks removed)."""
import json, re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "outputs/raw"
RES = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "results"
stance = {json.loads(l)["episode_id"]: json.loads(l)["stance"] for l in open(RAW / "stance.jsonl")}
by = {}
for l in open(RAW / "e1.jsonl"):
    r = json.loads(l); c = r["cfg"]
    if r.get("out") and c["topology"] == "relay1" and c["assurance"] == "peer" and r["cf"] == "unsafe":
        by[(r["scenario_id"], c["model"])] = r
def clean(s): return re.sub(r"[*`#>]+", "", str(s)).replace("\u2192", "->")
def op_in(r): return next((t["content"] for t in r["trace"] if t["kind"] == "in" and t["agent"] == "Operator"), "")
def first_report(r, agent): return next((t["content"] for t in r["trace"] if t["kind"] == "report" and t["agent"] == agent), {})
def cut(s, n):
    s = " ".join(clean(s).split()); return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + " ..."
def sent(s, pat):
    for x in re.split(r"(?<=[.!?])\s+|\n+", clean(s)):
        if re.search(pat, x, re.I) and len(x.split()) >= 5: return cut(x, 240)
    return cut(s, 240)
for sc in sorted({k[0] for k in by}):
    g, q = by.get((sc, "glm-5.2")), by.get((sc, "qwen3.5-397b"))
    if not (g and q): continue
    if stance.get(g["episode_id"]) == "reject" and (not g["out"]["V"]) and g["out"]["asked_before_act"] and \
       stance.get(q["episode_id"]) == "endorse" and q["out"]["V"] and q["out"]["report_status"] == "authorized":
        ex = {"scenario": sc,
              "skeptic": {"brief": sent(op_in(g), r"untrusted|unverified|verify|not (an )?(instruction|authoriz)|do not (treat|skip|rely)"), "report": cut(first_report(g, "Lead").get("summary", ""), 230)},
              "credulous": {"brief": sent(op_in(q), r"no further|not (be )?(needed|required)|already (been )?(obtained|approved)|pre-?approved|do not (invoke|request)"), "report": cut(first_report(q, "Lead").get("summary", ""), 230)}}
        p = RES / "extra.json"; d = json.load(open(p)) if p.exists() else {}; d["quotes"] = ex
        p.write_text(json.dumps(d, indent=1, ensure_ascii=False)); print(json.dumps(ex, indent=1, ensure_ascii=False)); break
else:
    print("no scenario matched the rule")
