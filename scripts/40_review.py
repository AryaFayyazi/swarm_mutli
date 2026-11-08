"""Independent harsh review: three different hosted models act as Apart judges with the official rubric. Reads paper/report.pdf (text).
Writes results/review_<tag>.json. Usage: 40_review.py <tag>.  This is a drafting aid, not evidence; the models are not human judges."""
import asyncio, json, subprocess, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from capeswarm.llm import LLM
tag = sys.argv[1] if len(sys.argv) > 1 else "r1"
txt = subprocess.run(["pdftotext", "-layout", str(ROOT / "paper/report.pdf"), "-"], capture_output=True, text=True).stdout
RUBRIC = """You are a strict judge for a 3-day AI-safety research sprint (Swarm Alignment Hackathon, Apart Research). Score the report on three dimensions, each 1-5:
IMPACT POTENTIAL & INNOVATION: 1 negligible; 2 real problem but generic/well-trodden; 3 clear problem, reasonable approach, some novelty in framing/method; 4 important problem with an original approach or a neglected area, others could build on it; 5 critical problem with a genuinely novel approach or new research direction and a clear theory of change. For 4-5 ask: is it new, or a replication of recent work?
EXECUTION QUALITY: 1 seriously flawed; 2 weak, significant gaps (missing validation, flawed design, incomplete); 3 competent for a short sprint; sound method, interpretable results, acknowledged limitations; 4 strong, thorough methodology with convincing validation, results clearly support conclusions; 5 exceptional: ambitious scope executed rigorously, surprising findings, novel methods or unusually robust validation.
PRESENTATION & CLARITY: 1 incomprehensible; 2 hard to follow, key info buried or diluted by excess length; 3 clear enough, problem/approach/results/limitations present and easy to find; 4 well presented, well structured, suited to the audience; 5 exceptionally clear, complex ideas made accessible, could serve as a model.
Be harsh and specific. Do not give 5 unless it is truly exceptional. Report scores via the `review` tool. List the 5 most damaging weaknesses a skeptical judge would raise (concrete: quote the claim, say what is missing), any claim that looks unsupported or internally inconsistent, and the 3 changes that would raise the score most. Also say what is strongest."""
TOOL = {"type": "function", "name": "review", "description": "Submit the review.", "parameters": {"type": "object", "properties": {
    "impact": {"type": "integer"}, "execution": {"type": "integer"}, "presentation": {"type": "integer"},
    "weaknesses": {"type": "array", "items": {"type": "string"}}, "inconsistencies": {"type": "array", "items": {"type": "string"}},
    "top_changes": {"type": "array", "items": {"type": "string"}}, "strengths": {"type": "string"}},
    "required": ["impact", "execution", "presentation", "weaknesses", "top_changes"]}}
async def main():
    llm = LLM(per_model_concurrency=3)
    models = ["glm-5.2", "qwen3.5-397b", "deepseek-v4-flash"]
    async def one(m):
        r = await llm.call(m, RUBRIC, [{"role": "user", "content": "REPORT TEXT (pdf extraction):\n\n" + txt[:60000] + "\n\nCall `review`."}], tools=[TOOL], max_out=6000, temperature=0.3)
        c = next((c for c in r.calls if c["name"] == "review"), None)
        return m, (c["args"] if c else {"error": r.error or r.text[:300]})
    res = dict(await asyncio.gather(*(one(m) for m in models)))
    (ROOT / f"results/review_{tag}.json").write_text(json.dumps(res, indent=1))
    for m, r in res.items():
        print(m, {k: r.get(k) for k in ("impact", "execution", "presentation")})
        for w in (r.get("weaknesses") or [])[:5]: print("   -", w[:260])
asyncio.run(main())
