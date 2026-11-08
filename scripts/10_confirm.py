"""Confirmatory runs (prereg v1). Usage: 10_confirm.py e1|e3. Jobs are scenario-major and shuffled with a fixed seed, so
any prefix of the run is balanced over conditions. Resumable: finished episodes are skipped."""
import asyncio, random, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from capeswarm.llm import LLM, MODELS
from capeswarm.runner import make_specs, run_many

SEED, NBASE = 9001, 48
M4 = ["gemma-4-26b-a4b-it", "gemma-4-31b-it", "qwen3.5-397b", "deepseek-v4-flash"]
CONTROLS = ["pdp", "ask_gate", "aud_min", "aud_trace", "aud_trace_just"]

def jobs_e1(specs):
    jobs = []
    for s in specs:
        for m in MODELS:
            for topo in ("solo", "relay1", "relay2"):
                for a in ("none", "peer"):
                    jobs.append((s, dict(model=m, topology=topo, assurance=a, tag="e1")))
    return jobs

def jobs_e3(specs):
    jobs = []
    for s in specs:
        for m in M4:
            for ck in CONTROLS:
                jobs.append((s, dict(model=m, topology="relay1", assurance="peer", control_kind=ck, tag="e3")))
            for rs in ("ledger", "ledger_auth"):
                jobs.append((s, dict(model=m, topology="relay1", assurance="peer", report_source=rs, tag="e3")))
    return jobs

async def main():
    which = sys.argv[1]
    llm = LLM(per_model_concurrency=14)
    specs = make_specs(NBASE, SEED)
    assert len(specs) == 2 * NBASE
    rnd = random.Random(1234)
    specs_sh = specs[:]; rnd.shuffle(specs_sh)
    jobs = jobs_e1(specs_sh) if which == "e1" else jobs_e3(specs_sh)
    await run_many(llm, jobs, ROOT / f"outputs/raw/{which}.jsonl", concurrency=80, label=which)
    print("DONE", which, llm.ledger.cost, llm.ledger.errors, llm.ledger.err_kinds)
asyncio.run(main())
