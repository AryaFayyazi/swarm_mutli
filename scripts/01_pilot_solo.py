"""DEV pilot: solo-agent violation rates on dev scenarios (seed 7001), all 7 models. Exploratory; not confirmatory."""
import asyncio, sys, json
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from capeswarm.llm import LLM, MODELS
from capeswarm.runner import make_specs, run_many

async def main():
    llm = LLM(per_model_concurrency=12)
    specs = [s for s in make_specs(16, 7001) if s["cf_value"] == "unsafe"]
    models = sys.argv[1].split(",") if len(sys.argv) > 1 else MODELS
    jobs = [(s, dict(model=m, topology="solo", assurance=a, tag="pilot1")) for m in models for s in specs for a in ("none", "peer")]
    await run_many(llm, jobs, ROOT / "outputs/raw/pilot_solo.jsonl", concurrency=64, label="pilot_solo")
    print(llm.ledger)
asyncio.run(main())
