"""Load episode JSONL into a flat table (pandas)."""
import json
import pandas as pd

def load(path):
    rows = []
    for line in open(path):
        r = json.loads(line)
        if not r.get("out"):
            continue
        d = {k: r["out"][k] for k in r["out"]}
        c = r["cfg"]
        d.update(model=c["model"], topology=c.get("topology", "solo"), assurance=c.get("assurance", "none"),
                 control=r.get("control") or "none", report_source=c.get("report_source", "peer"), rep=c.get("rep", 0),
                 tag=c.get("tag", ""), cf=r["cf"], family=r["family"], template=r["template"],
                 scenario_id=r["scenario_id"], instance_id=r["instance_id"], cost=r["cost"], errors=r["errors"],
                 episode_id=r["episode_id"])
        rows.append(d)
    return pd.DataFrame(rows)
