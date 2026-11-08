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

def jobs_e5(specs):
    return [(s, dict(model=m, topology="relay1", assurance=a, tag="e5")) for s in specs for m in M4 for a in ("manager", "terse", "hedged")]

def jobs_e6(specs):
    return [(s, dict(model=m, topology="relay1", assurance="peer", rep=1, tag="e1")) for s in specs if s["cf_value"] == "unsafe" for m in M4]

C_GRP = ["gemma-4-26b-a4b-it", "qwen3.5-397b"]
S_GRP = ["glm-5.2", "glm-53-flash"]

def jobs_e3b(specs):
    return [(s, dict(model=m, topology="relay1", assurance="peer", prompt_defense=True, tag="e3b")) for s in specs for m in M4]

def jobs_e4(specs):
    jobs = []
    for s in specs:
        for lead in C_GRP + S_GRP:
            for op in C_GRP + S_GRP:
                if lead == op or ((lead in C_GRP) == (op in C_GRP)):
                    continue            # E4 = pairs across the C/S divide only (mixed within a group is not needed)
                jobs.append((s, dict(model=op, models={"lead": lead, "operator": op, "manager": lead}, topology="relay1",
                                     assurance="peer", tag="e4")))
    return jobs

async def main():
    which = sys.argv[1]
    llm = LLM(per_model_concurrency=14)
    specs = make_specs(NBASE, SEED)
    assert len(specs) == 2 * NBASE
    rnd = random.Random(1234)
    specs_sh = specs[:]; rnd.shuffle(specs_sh)
    jobs = {"e1": jobs_e1, "e3": jobs_e3, "e3b": jobs_e3b, "e4": jobs_e4, "e5": jobs_e5, "e6": jobs_e6}[which](specs_sh)
    await run_many(llm, jobs, ROOT / f"outputs/raw/{which}.jsonl", concurrency=80, label=which)
    print("DONE", which, llm.ledger.cost, llm.ledger.errors, llm.ledger.err_kinds)
asyncio.run(main())
