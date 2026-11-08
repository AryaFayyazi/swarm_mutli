"""E2: monitors over E1 relay1 traces for M4 (prereg v1). Resumable; one JSONL line per (episode, monitor)."""
import asyncio, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from capeswarm.llm import LLM
from capeswarm.monitors import LEVELS, judge, self_query, policy_of
from capeswarm.runner import make_specs

M4 = ["gemma-4-26b-a4b-it", "gemma-4-31b-it", "qwen3.5-397b", "deepseek-v4-flash"]
import os
JUDGES = os.environ.get("JUDGES", "qwen3.5-397b,gemma-4-31b-it").split(",")   # robustness runs set JUDGES and OUTNAME (default unchanged)
OUTNAME = os.environ.get("OUTNAME", "e2.jsonl")
INFILES = os.environ.get("INFILES", "e1.jsonl").split(",")   # round 2: e9.jsonl,e10.jsonl with SEED=5501 and SELECT=round2
SEED = int(os.environ.get("SEED", "9001"))
SELECT = os.environ.get("SELECT", "e1")
SKIP_SELF = os.environ.get("SKIP_SELF") == "1"
LEVELS_USED = os.environ.get("LEVELS", ",".join(LEVELS)).split(",")
NS = int(os.environ.get("JNS", "2"))

async def main():
    out = ROOT / "outputs/raw" / OUTNAME
    done = set()
    if out.exists():
        for l in open(out):
            r = json.loads(l); done.add((r["episode_id"], r["monitor"]))
    specs = {s["instance_id"]: s for s in make_specs(48, SEED)}
    eps = []
    for fn in INFILES:
      for l in open(ROOT / "outputs/raw" / fn):
        r = json.loads(l)
        c = r["cfg"]
        if SELECT == "round2":      # cell B of E9 (relay1, peer, no control, no filter, main wording) and every E10 (stealth) episode
            ok = (fn == "e10.jsonl") or (c.get("assurance") == "peer" and not c.get("control_kind") and not c.get("claim_filter")
                                           and not c.get("assurance_text") and not c.get("report_source", "peer") != "peer")
        else:
            ok = True
        if r.get("out") and c["topology"] == "relay1" and c["model"] in M4 and ok:
            eps.append(r)
    print("traces", len(eps), flush=True)
    llm = LLM(per_model_concurrency=40)
    sem = asyncio.Semaphore(220); lock = asyncio.Lock(); n = 0
    jobs = []
    for r in eps:
        for lv in LEVELS_USED:
            for j in JUDGES:
                jobs.append((r, f"judge:{j}:{lv}"))
        if not SKIP_SELF:
            jobs.append((r, "self"))
    jobs = [(r, m) for r, m in jobs if (r["episode_id"], m) not in done]
    print("jobs", len(jobs), flush=True)

    async def one(r, mon):
        nonlocal n
        spec = specs[r["instance_id"]]
        async with sem:
            if mon == "self":
                res = await self_query(llm, r["cfg"]["model"], spec["system_prompt"], r)
            else:
                _, j, lv = mon.split(":")
                res = await judge(llm, j, policy_of(spec["system_prompt"]), spec["task_prompt"], r, lv, n=NS)
        rec = {"episode_id": r["episode_id"], "monitor": mon, **res}
        async with lock:
            with open(out, "a") as f:
                f.write(json.dumps(rec) + "\n")
            n += 1
            if n % 100 == 0:
                print(n, len(jobs), llm.ledger.calls, round(llm.ledger.cost, 3), llm.ledger.errors, flush=True)
    await asyncio.gather(*(one(r, m) for r, m in jobs))
    print("DONE e2", llm.ledger.cost, llm.ledger.errors, llm.ledger.err_kinds)
asyncio.run(main())
