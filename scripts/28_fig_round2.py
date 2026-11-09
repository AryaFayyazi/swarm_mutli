"""Figure 6: the claim filter (E9). (a) Unauthorized-action rate by message wording and control. (b) Safe-twin goal completion (utility).
Reads results/round2.json. Palette as in the other figures."""
import json, sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "paper/figs"; OUT.mkdir(exist_ok=True, parents=True)
R = json.load(open(ROOT / "results/round2.json"))["_cells"]
BLUE, ORANGE, AQUA, GRAY, INK, SUB = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b", "#52514e"
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 7, "axes.spines.top": False, "axes.spines.right": False, "savefig.bbox": "tight", "figure.dpi": 220})
fig, (a, b) = plt.subplots(1, 2, figsize=(5.4, 2.3), gridspec_kw={"width_ratios": [1.55, 1]})
groups = [("main message", ("B", "C", "D")), ("attacker message", ("G", "H", None))]
cols = (BLUE, ORANGE, AQUA); labs = ("no control", "claim filter", "ask-before-act gate")
w = 0.26
for gi, (g, cs) in enumerate(groups):
    for k, c in enumerate(cs):
        if c is None:
            continue
        d = R[c]; x = gi + (k - 1) * w
        a.bar(x, d["V"], w * 0.9, color=cols[k], label=labs[k] if gi == 0 else None)
        a.errorbar(x, d["V"], yerr=[[d["V"] - d["V_lo"]], [d["V_hi"] - d["V"]]], color=INK, lw=0.8, capsize=2)
        a.text(x, d["V_hi"] + 0.02, f"{d['V']:.2f}", ha="center", fontsize=6.5, color=INK)
a.axhline(R["A"]["V"], color=GRAY, ls="--", lw=0.9); a.text(0.52, R["A"]["V"] + 0.02, "no-message base rate", fontsize=6.5, color=SUB, ha="center")
a.set_xticks(range(2)); a.set_xticklabels([g for g, _ in groups]); a.set_ylabel("unauthorized-action rate\n(unsafe twins)"); a.set_ylim(0, 1.0)
a.legend(frameon=False, fontsize=6.5, loc="upper right", bbox_to_anchor=(1.0, 1.02)); a.set_title("(a) violations", fontsize=7.5, loc="left")
for k, c in enumerate(("B", "C", "D")):
    d = R[c]
    b.bar(k, d["goal_safe"], 0.6, color=cols[k])
    b.errorbar(k, d["goal_safe"], yerr=[[d["goal_safe"] - d["goal_lo"]], [d["goal_hi"] - d["goal_safe"]]], color=INK, lw=0.8, capsize=2)
    b.text(k, d["goal_hi"] + 0.02, f"{d['goal_safe']:.2f}", ha="center", fontsize=6.5)
b.set_xticks(range(3)); b.set_xticklabels(["none", "filter", "gate"]); b.set_ylim(0, 1.0); b.set_ylabel("goal completed\n(safe twins)"); b.set_title("(b) utility", fontsize=7.5, loc="left")
fig.tight_layout(); fig.savefig(OUT / "fig6_filter.png"); print("ok")
