"""Concurrent, resumable episode runner (NEW in the sprint). One JSONL line per finished episode."""
from __future__ import annotations

import asyncio
import json
import sys
import time
from pathlib import Path

from capeswarm.llm import LLM
from capeswarm.swarm import run_episode

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "preexisting" / "cape_src"))
from cape.envs.capebench.generator import generate  # noqa: E402


def make_specs(num_base: int, seed: int, paraphrases: int = 1, **knobs) -> list[dict]:
    return generate(num_base, paraphrases, seed, nuisance=False, **knobs)


def episode_id(spec: dict, cfg: dict) -> str:
    parts = [spec["instance_id"], cfg["model"], cfg.get("topology", "solo"), cfg.get("assurance", "none"),
             cfg.get("control_kind") or "none", cfg.get("report_source", "peer"), str(cfg.get("rep", 0)),
             cfg.get("tag", "")]
    if cfg.get("prompt_defense"):
        parts.append("pd")
    if cfg.get("models"):
        parts.append(json.dumps(cfg["models"], sort_keys=True))
    return "|".join(parts)


def done_ids(path: Path) -> set:
    ids = set()
    if path.exists():
        for line in open(path):
            try:
                ids.add(json.loads(line)["episode_id"])
            except Exception:
                pass
    return ids


async def run_many(llm: LLM, jobs: list[tuple[dict, dict]], out_path: Path, concurrency: int = 48, label: str = ""):
    """jobs: [(spec, cfg)]; cfg['episode_id'] is set here. Skips episodes already in out_path."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    have = done_ids(out_path)
    todo = []
    for spec, cfg in jobs:
        cfg = dict(cfg)
        cfg["episode_id"] = episode_id(spec, cfg)
        if cfg["episode_id"] not in have:
            todo.append((spec, cfg))
    print(f"[{label}] {len(todo)} to run, {len(jobs) - len(todo)} cached", flush=True)
    sem = asyncio.Semaphore(concurrency)
    lock = asyncio.Lock()
    t0 = time.time()
    n_done = 0

    async def one(spec, cfg):
        nonlocal n_done
        async with sem:
            try:
                res = await run_episode(llm, spec, cfg)
            except Exception as e:  # keep the run alive; record the failure
                res = {"episode_id": cfg["episode_id"], "instance_id": spec["instance_id"], "error_fatal": repr(e)[:300],
                       "cfg": {k: v for k, v in cfg.items() if k != "control"}, "out": None}
        async with lock:
            with open(out_path, "a") as f:
                f.write(json.dumps(res, default=str) + "\n")
            n_done += 1
            if n_done % 25 == 0 or n_done == len(todo):
                L = llm.ledger
                print(f"[{label}] {n_done}/{len(todo)}  {time.time() - t0:.0f}s  calls={L.calls} err={L.errors} "
                      f"cost={L.cost:.4f}", flush=True)

    await asyncio.gather(*(one(s, c) for s, c in todo))
