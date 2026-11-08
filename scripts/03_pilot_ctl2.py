import asyncio, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from capeswarm.llm import LLM
from capeswarm.runner import make_specs, run_many
async def main():
    llm = LLM(per_model_concurrency=12)
    specs = make_specs(16, 7001)   # both twins
    m = sys.argv[1]
    jobs = []
    for s in specs:
        jobs.append((s, dict(model=m, topology="relay1", assurance="peer", control_kind="ask_gate", tag="pilot3")))
        jobs.append((s, dict(model=m, topology="relay1", assurance="peer", report_source="ledger_auth", tag="pilot3")))
        jobs.append((s, dict(model=m, topology="relay1", assurance="peer", tag="pilot3")))
    await run_many(llm, jobs, ROOT / "outputs/raw/pilot_ctl2.jsonl", concurrency=64, label="ctl2")
asyncio.run(main())
