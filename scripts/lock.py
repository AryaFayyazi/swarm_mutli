import hashlib, json, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
name = sys.argv[1]
files = ["docs/PREREG_v1.md", "capeswarm/llm.py", "capeswarm/swarm.py", "capeswarm/controls.py", "capeswarm/runner.py",
         "scripts/10_confirm.py"] + sys.argv[2:]
lock = {"name": name, "time_local": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "sha256": {f: hashlib.sha256((ROOT / f).read_bytes()).hexdigest() for f in files}}
(ROOT / f"results/{name}_lock.json").write_text(json.dumps(lock, indent=1))
print(json.dumps(lock, indent=1))
