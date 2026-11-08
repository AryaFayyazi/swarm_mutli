"""E2: monitors over E1 relay1 traces for M4 (prereg v1). Resumable; one JSONL line per (episode, monitor)."""
import asyncio, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from capeswarm.llm import LLM
from capeswarm.monitors import LEVELS, judge, self_query, policy_of
from capeswarm.runner import make_specs

M4 = ["gemma-4-26b-a4b-it", "gemma-4-31b-it", "qwen3.5-397b", "deepseek-v4-flash"]
JUDGES = ["qwen3.5-397b", "gemma-4-31b-it"]

async def main():
    out = ROOT / "outputs/raw/e2.jsonl"
    done = set()
    if out.exists():
        for l in open(out):
            r = json.loads(l); done.add((r["episode_id"], r["monitor"]))
    specs = {s["instance_id"]: s for s in make_specs(48, 9001)}
    eps = []
    for l in open(ROOT / "outputs/raw/e1.jsonl"):
        r = json.loads(l)
        c = r["cfg"]
        if r.get("out") and c["topology"] == "relay1" and c["model"] in M4:
            eps.append(r)
    print("traces", len(eps), flush=True)
    llm = LLM(per_model_concurrency=14)
    sem = asyncio.Semaphore(90); lock = asyncio.Lock(); n = 0
    jobs = []
    for r in eps:
        for lv in LEVELS:
            for j in JUDGES:
                jobs.append((r, f"judge:{j}:{lv}"))
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
                res = await judge(llm, j, policy_of(spec["system_prompt"]), spec["task_prompt"], r, lv)
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
