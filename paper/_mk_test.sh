#!/bin/sh
cd /home/arya/swarm_hack
python3 - <<'PY'
from pathlib import Path
R=Path('/home/arya/swarm_hack')
parts=sorted((R/'paper/parts').glob('*.md'))
t="\n\n".join(p.read_text().strip() for p in parts)
t=t.replace('@@ABSTRACT@@','Test abstract. '*20).replace('@@DISCUSSION@@','Test discussion paragraph with a number of words in it. '*40).replace('@@STANCE@@','(stance pending)').replace('{{CONCLUSION}}','Test conclusion. '*40).replace('{{INTRO_FINDINGS}}','Test findings. '*40).replace('@@E7@@','(e7)').replace('@@E6@@','(e6)')
(R/'paper/_test.md').write_text(t)
PY
.venv/bin/python paper/build_report.py paper/_test.md paper/_test.docx 2>&1 | tail -1
