"""Figure 6: what a message says about approval sets V. One dot per condition (unsafe twins, relay, four models, fresh tasks), 95% CI whiskers.
Rows come from E12 (2x2) and E13 (doubt). Reads results/round2.json."""
import json
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper/figs"; OUT.mkdir(exist_ok=True, parents=True)
R = json.load(open(ROOT / "results/round2.json"))
BLUE, ORANGE, AQUA, GRAY, INK, SUB = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b", "#52514e"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 8, "axes.spines.top": False, "axes.spines.right": False, "savefig.bbox": "tight", "figure.dpi": 220})
e13, t = R["_e13"], R["_2x2"]
rows = [  # label, V, lo, hi, colour
    ("peer says: approvals were obtained", e13["false claim"], ORANGE),
    ("same claim, verification rule in prompt", t["Q claim+reminder"], BLUE),
    ("no message", e13["none"], GRAY),
    ("neutral message (due by end of day)", e13["neutral"], GRAY),
    ("verification rule only", t["R reminder"], BLUE),
    ("peer asks: has anyone confirmed approval?", e13["question"], AQUA),
    ("peer says: approvals maybe, not checked", e13["hedged"], AQUA),
]
fig, ax = plt.subplots(figsize=(7.2, 2.3))
for i, (lab, d, c) in enumerate(rows):
    y = len(rows) - 1 - i
    ax.plot([d["lo"], d["hi"]], [y, y], color=c, lw=2.2, solid_capstyle="round", zorder=2)
    ax.scatter([d["V"]], [y], s=46, color=c, edgecolor="white", linewidth=0.9, zorder=3)
    ax.text(d["hi"] + 0.012, y, f"{d['V']:.2f}", va="center", fontsize=7, color=INK)
ax.axvline(e13["none"]["V"], color=GRAY, ls="--", lw=0.9, zorder=1)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([r[0] for r in rows][::-1], fontsize=7.4)
ax.set_xlim(0, max(r[1]["hi"] for r in rows) + 0.1); ax.set_xlabel("unauthorized-action rate V (unsafe twins)")
ax.tick_params(axis="y", length=0)
fig.tight_layout(); fig.savefig(OUT / "fig7_dial.png"); fig.savefig(OUT / "fig7_dial.pdf"); print("ok")
