"""Illustrative pair for the paper, chosen by a FIXED rule (not by eye): the first scenario (sorted id) in E1, relay1 + peer, unsafe twin,
where the skeptical model (glm-5.2) asked for permission before acting and had no violation, AND the credulous model (qwen3.5-397b) had
a violation whose Lead brief orders the Operator to skip approval. Writes results/extra.json['quotes'] with verbatim text."""
import json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from capeswarm.hops import SKIP_ORDER
RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "outputs/raw"
RES = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "results"
by = {}
for l in open(RAW / "e1.jsonl"):
    r = json.loads(l)
    c = r["cfg"]
    if r.get("out") and c["topology"] == "relay1" and c["assurance"] == "peer" and r["cf"] == "unsafe":
        by[(r["scenario_id"], c["model"])] = r
def brief(r): return next(t["content"] for t in r["trace"] if t["kind"] == "say" and t["agent"] == "Lead")
def first_report(r, agent): return next((t["content"] for t in r["trace"] if t["kind"] == "report" and t["agent"] == agent), {})
for sc in sorted({k[0] for k in by}):
    g, q = by.get((sc, "glm-5.2")), by.get((sc, "qwen3.5-397b"))
    if not (g and q):
        continue
    if (not g["out"]["V"]) and g["out"]["asked_before_act"] and q["out"]["V"] and SKIP_ORDER.search(brief(q)):
        def cut(s, n): s = " ".join(str(s).split()); return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + " …"
        def sent(s, pat):
            import re
            for x in re.split(r"(?<=[.!?])\s+|\n+", str(s)):
                if re.search(pat, x, re.I): return cut(x, 230)
            return cut(s, 230)
        ex = {"scenario": sc,
              "skeptic": {"model": "glm-5.2", "brief": sent(brief(g), r"verif|authoriz|unverified|ACL"), "violation": g["out"]["V"],
                          "report": cut(first_report(g, "Lead").get("summary", ""), 330), "status": g["out"]["report_status"]},
              "credulous": {"model": "qwen3.5-397b", "brief": sent(brief(q), r"permission|approval|compliance"), "violation": q["out"]["V"],
                            "report": cut(first_report(q, "Lead").get("summary", ""), 330), "status": q["out"]["report_status"]}}
        p = RES / "extra.json"
        d = json.load(open(p)) if p.exists() else {}
        d["quotes"] = ex
        p.write_text(json.dumps(d, indent=1, ensure_ascii=False)); print(json.dumps(ex, indent=1, ensure_ascii=False)); break
else:
    print("no scenario matched the rule yet")
