"""DEV pilot of relay topologies and controls (dev seed 7001; exploratory)."""
import asyncio, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from capeswarm.llm import LLM
from capeswarm.runner import make_specs, run_many
async def main():
    llm = LLM(per_model_concurrency=12)
    specs = [s for s in make_specs(16, 7001) if s["cf_value"] == "unsafe"]
    models = sys.argv[1].split(",")
    jobs = []
    for m in models:
        for s in specs:
            for topo in ("relay1", "relay2"):
                for a in ("none", "peer"):
                    jobs.append((s, dict(model=m, topology=topo, assurance=a, tag="pilot2")))
            for ck in ("pdp", "aud_min", "aud_trace", "aud_trace_just"):
                jobs.append((s, dict(model=m, topology="relay1", assurance="peer", control_kind=ck, tag="pilot2")))
            jobs.append((s, dict(model=m, topology="relay1", assurance="peer", report_source="ledger", tag="pilot2")))
    await run_many(llm, jobs, ROOT / "outputs/raw/pilot_relay.jsonl", concurrency=64, label="pilot_relay")
    print(llm.ledger.cost, llm.ledger.errors, llm.ledger.err_kinds)
asyncio.run(main())
