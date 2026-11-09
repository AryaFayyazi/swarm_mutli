"""First-time-reader check by three hosted models (a drafting aid, not evidence). Lists terms used before they are defined, unclear sentences,
paragraphs with too many numbers, and anything that reads like a report rather than a paper. Usage: 41_clarity_review.py <tag>."""
import asyncio, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from capeswarm.llm import LLM
tag = sys.argv[1] if len(sys.argv) > 1 else "c1"
txt = subprocess.run(["pdftotext", "-layout", str(ROOT / "paper/report.pdf"), "-"], capture_output=True, text=True).stdout
SYS = """You are a researcher who has never seen this paper and is not an expert in agent security. Read the MAIN TEXT (title to Conclusion; ignore references and appendices) and
report, using the `clarity` tool: (1) terms, symbols or experiment labels used before they are defined (quote the first use and its section); (2) the 8 hardest sentences to
understand (quote them and say why); (3) paragraphs with too many numbers for a first-time reader (name the section); (4) places where the text reads like a lab report or
a log instead of a paper (give examples); (5) any claim that is not supported by the evidence shown; (6) the 5 changes that would most improve clarity. Be specific and short. Quote exact text."""
TOOL = {"type": "function", "name": "clarity", "description": "Submit the reader report.", "parameters": {"type": "object", "properties": {
    "undefined_terms": {"type": "array", "items": {"type": "string"}}, "hard_sentences": {"type": "array", "items": {"type": "string"}},
    "number_heavy": {"type": "array", "items": {"type": "string"}}, "report_like": {"type": "array", "items": {"type": "string"}},
    "unsupported": {"type": "array", "items": {"type": "string"}}, "top_changes": {"type": "array", "items": {"type": "string"}}},
    "required": ["undefined_terms", "hard_sentences", "number_heavy", "top_changes"]}}
async def main():
    llm = LLM(per_model_concurrency=3)
    models = ["glm-5.2", "qwen3.5-397b", "gemma-4-31b-it"]
    main_txt = txt.split("\nReferences\n")[0]
    async def one(m):
        r = await llm.call(m, SYS, [{"role": "user", "content": "PAPER TEXT (pdf extraction):\n\n" + main_txt[:60000] + "\n\nCall `clarity`."}], tools=[TOOL], max_out=6000, temperature=0.3)
        c = next((c for c in r.calls if c["name"] == "clarity"), None)
        return m, (c["args"] if c else {"error": r.error or r.text[:300]})
    res = dict(await asyncio.gather(*(one(m) for m in models)))
    (ROOT / f"results/clarity_{tag}.json").write_text(json.dumps(res, indent=1))
    for m, r in res.items():
        print("==", m)
        for k in ("undefined_terms", "number_heavy", "report_like", "top_changes"):
            for w in (r.get(k) or [])[:6]: print(f"  [{k}]", w[:230])
asyncio.run(main())
