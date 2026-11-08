"""Concatenates paper/parts/*.md (sorted) into paper/content.md. Refuses to build while any @@TODO@@ marker is left."""
import re, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
parts = sorted((ROOT / "paper/parts").glob("*.md"))
text = "\n\n".join(p.read_text().strip() for p in parts) + "\n"
left = re.findall(r"@@\w+@@|\{\{[A-Z_]+\}\}", text)
(ROOT / "paper/content.md").write_text(text)
print("parts:", [p.name for p in parts]); print("UNRESOLVED markers:", left if left else "none")
sys.exit(1 if left else 0)
