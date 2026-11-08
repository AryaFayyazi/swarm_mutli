"""Confirmatory runs (prereg v1). Usage: 10_confirm.py e1|e3. Jobs are scenario-major and shuffled with a fixed seed, so
any prefix of the run is balanced over conditions. Resumable: finished episodes are skipped."""
import asyncio, os, random, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from capeswarm.llm import LLM, MODELS
from capeswarm.runner import make_specs, run_many

SEED, NBASE = 9001, 48
NBASE_R2 = 40          # amendment 5b: the API limit fell to ~60 requests/min, so round 2 uses 40 base scenarios
SEED_R2 = 5501          # round 2 (addendum 5): fresh draws, E9 and E10
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

def jobs_e7(specs):
    return [(s, dict(model=m, topology="relay1", assurance="peer", control_kind="aud_trace", auditor_model="glm-5.2", tag="e7")) for s in specs for m in M4]

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

def _atk():
    import json
    return json.load(open(ROOT / "docs/attacker_search.json"))["selected"]["text"]

def jobs_e9(specs):
    """Amendment 5b: unsafe-only cells need no safe twin (V only); B, C, D run both twins (V and utility). No solo cells."""
    atk = _atk()
    cells = [("A", dict(assurance="none"), False), ("B", dict(assurance="peer"), True),
             ("C", dict(assurance="peer", claim_filter="rewrite"), True),
             ("D", dict(assurance="peer", control_kind="ask_gate"), True),
             ("G", dict(assurance="peer", assurance_text=atk), False),
             ("H", dict(assurance="peer", assurance_text=atk, claim_filter="rewrite"), False)]
    return [(s, dict(model=m, topology="relay1", tag="e9", **c)) for s in specs for m in M4 for _, c, both in cells
            if both or s["cf_value"] == "unsafe"]

def jobs_e11(specs):
    """Round 3 (addendum 6): the filter-aware attacker's selected message vs the filter and the gate, unsafe twins, same scenarios as E9."""
    import json
    t = json.load(open(ROOT / "docs/filter_attacker_search.json"))["selected"]["text"]
    cells = [dict(claim_filter="rewrite"), dict(), dict(control_kind="ask_gate")]
    return [(s, dict(model=m, topology="relay1", assurance="peer", assurance_text=t, tag="e11", **c)) for s in specs if s["cf_value"] == "unsafe"
            for m in M4 for c in cells]

def jobs_e10(specs):
    return [(s, dict(model=m, topology="relay1", assurance="peer", stealth=True, tag="e10")) for s in specs for m in M4]

async def main():
    which = sys.argv[1]
    import os
    llm = LLM(per_model_concurrency=int(os.environ.get("SWARM_PMC", "14")))
    specs = make_specs(NBASE_R2, SEED_R2) if which in ("e9", "e10", "e11") else make_specs(NBASE, SEED)
    assert len(specs) == (2 * NBASE_R2 if which in ("e9", "e10", "e11") else 2 * NBASE)
    rnd = random.Random(1234)
    specs_sh = specs[:]; rnd.shuffle(specs_sh)
    if which in ("e9", "e10", "e11"):      # amendment 5c: both twins of a base scenario are adjacent, scenarios with the most finished episodes first
        import json as _j
        cnt = {}
        pth = ROOT / "outputs/raw/e9.jsonl"
        if pth.exists():
            for l in open(pth):
                try: cnt[_j.loads(l)["instance_id"].rsplit(".", 1)[0]] = cnt.get(_j.loads(l)["instance_id"].rsplit(".", 1)[0], 0) + 1
                except Exception: pass
        base = lambda s_: s_["instance_id"].rsplit(".", 1)[0]
        order = {}
        for s_ in specs_sh: order.setdefault(base(s_), len(order))
        specs_sh = sorted(specs, key=lambda s_: (-cnt.get(base(s_), 0), order[base(s_)], s_["cf_value"] != "unsafe"))
        if os.environ.get("LIMIT_SCEN"):      # E10/E11 run on the first N base scenarios of this order (those E9 finished first)
            keep = []
            for s_ in specs_sh:
                if base(s_) not in keep: keep.append(base(s_))
            keep = set(keep[:int(os.environ["LIMIT_SCEN"])])
            specs_sh = [s_ for s_ in specs_sh if base(s_) in keep]
    jobs = {"e1": jobs_e1, "e3": jobs_e3, "e3b": jobs_e3b, "e4": jobs_e4, "e5": jobs_e5, "e6": jobs_e6, "e7": jobs_e7, "e9": jobs_e9, "e10": jobs_e10, "e11": jobs_e11}[which](specs_sh)
    await run_many(llm, jobs, ROOT / f"outputs/raw/{which}.jsonl", concurrency=80, label=which)
    print("DONE", which, llm.ledger.cost, llm.ledger.errors, llm.ledger.err_kinds)
asyncio.run(main())
