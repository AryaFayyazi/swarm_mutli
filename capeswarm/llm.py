"""Async client for the Adaption Responses API (hosted open-weight models).

NEW in the sprint. One shared client: per-model concurrency limits, retries with back-off, token/cost ledger.
The key is read from ADAPTION_API_KEY (never stored in the repo).
"""
from __future__ import annotations

import asyncio
import collections
import json
import os
import random
import time
from dataclasses import dataclass, field

from adaption import AsyncAdaption

MODELS = ["gemma-4-26b-a4b-it", "gemma-4-31b-it", "qwen3.8-27b", "qwen3.5-397b", "glm-53-flash", "glm-5.2",
          "deepseek-v4-flash"]


@dataclass
class Resp:
    text: str
    calls: list            # [{"name":..., "args": dict, "call_id":..., "raw_args": str}]
    items: list            # replayable output items (messages + function_calls; reasoning stripped)
    cost: float = 0.0
    in_tok: int = 0
    out_tok: int = 0
    reasoning_tok: int = 0
    error: str = ""


@dataclass
class Ledger:
    cost: float = 0.0
    calls: int = 0
    in_tok: int = 0
    out_tok: int = 0
    errors: int = 0
    by_model: dict = field(default_factory=dict)
    err_kinds: dict = field(default_factory=dict)
    incomplete: int = 0
    err_samples: list = field(default_factory=list)


def to_responses_tools(chat_tools: list[dict]) -> list[dict]:
    """CAPE tool specs are Chat-Completions style; the Responses API wants them flat."""
    out = []
    for t in chat_tools:
        f = t["function"]
        out.append({"type": "function", "name": f["name"], "description": f["description"],
                    "parameters": f["parameters"]})
    return out


class LLM:
    def __init__(self, per_model_concurrency: int = 16, max_retries: int = 7, timeout: float = 100.0):
        self.client = AsyncAdaption(max_retries=0, timeout=timeout)
        self.limits: dict[str, asyncio.Semaphore] = {}
        self.per_model = per_model_concurrency
        self.max_retries = max_retries
        self.ledger = Ledger()
        self.timeout = timeout
        self.rate = int(os.environ.get("SWARM_RPM", "270"))      # server limit is ~300 requests/min/user, all models
        self._stamps: collections.deque = collections.deque()
        self._rl = asyncio.Lock()
        self._pause_until = 0.0

    async def _throttle(self):
        """Global sliding-window limiter (one process must own the key's budget)."""
        while True:
            async with self._rl:
                now = time.monotonic()
                if now < self._pause_until:
                    wait = self._pause_until - now
                else:
                    while self._stamps and now - self._stamps[0] > 60.0:
                        self._stamps.popleft()
                    if len(self._stamps) < self.rate:
                        self._stamps.append(now)
                        return
                    wait = 60.0 - (now - self._stamps[0]) + 0.05
            await asyncio.sleep(min(max(wait, 0.05), 5.0))

    def _sem(self, model: str) -> asyncio.Semaphore:
        if model not in self.limits:
            self.limits[model] = asyncio.Semaphore(self.per_model)
        return self.limits[model]

    async def call(self, model: str, instructions: str, items: list, tools: list | None = None,
                   max_out: int = 1200, temperature: float = 0.7) -> Resp:
        kw = dict(model=model, instructions=instructions, input=items, max_output_tokens=max_out,
                  temperature=temperature)
        if tools:
            kw["tools"] = tools
        last = ""
        for attempt in range(self.max_retries):
            try:
                async with self._sem(model):
                    await self._throttle()
                    r = await self.client.responses.create(**kw)
                return self._parse(model, r)
            except Exception as e:  # network, 429, 5xx, parse
                last = f"{type(e).__name__}: {str(e)[:600]}"
                if "429" in last:
                    self._pause_until = time.monotonic() + 20.0
                self.ledger.errors += 1
                k = last[:90]
                if len(self.ledger.err_samples) < 6 and '429' in last:
                    self.ledger.err_samples.append((model, last))
                self.ledger.err_kinds[k] = self.ledger.err_kinds.get(k, 0) + 1
                await asyncio.sleep(min(30.0, (2 ** attempt) * 0.7) * (0.5 + random.random()))
        return Resp(text="", calls=[], items=[], error=last)

    def _parse(self, model: str, r) -> Resp:
        calls, items = [], []
        for o in r.output:
            if o.type == "function_call":
                try:
                    args = json.loads(o.arguments) if o.arguments else {}
                    if not isinstance(args, dict):
                        args = {"_value": args}
                except json.JSONDecodeError:
                    args = {"_unparsed": o.arguments}
                calls.append({"name": o.name, "args": args, "call_id": o.call_id, "raw_args": o.arguments})
                items.append(o.model_dump(exclude_none=True))
            elif o.type == "message":
                items.append(o.model_dump(exclude_none=True))
        u = r.usage
        cost = float(getattr(u, "cost", 0.0) or 0.0)
        rt = 0
        try:
            rt = int(u.output_tokens_details.reasoning_tokens or 0)
        except Exception:
            pass
        L = self.ledger
        L.cost += cost
        L.calls += 1
        L.in_tok += int(u.input_tokens or 0)
        L.out_tok += int(u.output_tokens or 0)
        bm = L.by_model.setdefault(model, {"calls": 0, "cost": 0.0})
        bm["calls"] += 1
        bm["cost"] += cost
        return Resp(text=r.output_text or "", calls=calls, items=items, cost=cost, in_tok=int(u.input_tokens or 0),
                    out_tok=int(u.output_tokens or 0), reasoning_tok=rt)
