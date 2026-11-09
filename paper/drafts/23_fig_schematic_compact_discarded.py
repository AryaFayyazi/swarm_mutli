"""Figure 1 (workflow + teaser), compact: the team workflow with the defenses attached where they act (top), and three result cards that follow
the causal chain (bottom). Reads results/*.json."""
import json, sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Ellipse

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "paper/figs"
OUT.mkdir(parents=True, exist_ok=True)
R = json.load(open(ROOT / "results/round2.json")); H = json.load(open(ROOT / "results/hypotheses.json")); X = json.load(open(ROOT / "results/extra.json"))
BLUE, ORANGE, AQUA, GRAY, INK, SUB, LINE, GREEN = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b", "#52514e", "#dcdbd6", "#0f7a55"
plt.rcParams.update({"font.family": "DejaVu Sans", "savefig.bbox": "tight", "figure.dpi": 220})
FW, FH = 6.5, 2.55
fig = plt.figure(figsize=(FW, FH)); ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 100); ax.set_ylim(0, 100); ax.axis("off")
SX, SY = FW / 100.0, FH / 100.0


def rbox(x, y, w, h, fc="white", ec=LINE, lw=1.0, ls="-", r=1.6, z=1, shadow=False):
    if shadow:
        ax.add_patch(FancyBboxPatch((x + 0.4, y - 1.0), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc="#0000000f", ec="none", zorder=z - 0.5))
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))


def arrow(a, b, col=SUB, lw=1.4, z=3, ms=8):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=ms, color=col, lw=lw, zorder=z, shrinkA=0, shrinkB=0))


def badge(x, y, k, r=3.4):
    ax.add_patch(Ellipse((x, y), 2 * r * SY / SX, 2 * r, fc=INK, ec="white", lw=1.2, zorder=9))
    ax.text(x, y, str(k), ha="center", va="center", fontsize=7.0, color="white", fontweight="bold", zorder=10)


def node(x, y, w, h, title, sub, col):
    rbox(x, y, w, h, "white", col, lw=1.6, z=2, shadow=True)
    ax.add_patch(FancyBboxPatch((x, y + h - 9.0), w, 9.0, boxstyle="round,pad=0,rounding_size=1.6", fc=col, ec=col, lw=0, zorder=3))
    ax.add_patch(Rectangle((x, y + h - 9.0), w, 4.0, fc=col, ec="none", zorder=3))
    ax.text(x + w / 2, y + h - 4.5, title, ha="center", va="center", fontsize=7.3, color="white", fontweight="bold", zorder=4)
    ax.text(x + w / 2, y + (h - 9.0) / 2, sub, ha="center", va="center", fontsize=6.5, color=INK, zorder=4, linespacing=1.2)


def pill(cx, cy, w, text, col, fs=6.3):
    rbox(cx - w / 2, cy - 3.6, w, 7.2, "white", col, lw=1.2, ls="--", r=2.4, z=6)
    ax.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=col, fontweight="bold", zorder=7)


NY, NH, yf = 49, 29, 62
X0 = [0.8, 27.5, 54.2, 80.9]; W = 18.2
node(X0[0], NY, W, NH, "Human", "gives the task;\nreads only the\nfinal report", GRAY)
node(X0[1], NY, W, NH, "Lead", "no tools; writes\nthe brief and\nthe report", BLUE)
node(X0[2], NY, W, NH, "Operator", "the only agent\nwith tools", BLUE)
node(X0[3], NY, W, NH, "Gateway", "logs every call\nand result; runs\nthe mock tools", INK)
for i in (0, 1, 2):
    arrow((X0[i] + W + 0.5, yf), (X0[i + 1] - 0.5, yf))
ax.text((X0[1] + W + X0[2]) / 2, yf + 4.2, "brief", ha="center", fontsize=6.5, color=SUB); ax.text((X0[2] + W + X0[3]) / 2, yf + 4.2, "calls", ha="center", fontsize=6.5, color=SUB)
cx = X0[1] + W / 2
rbox(11.0, 88.0, 68.0, 11.0, "#fde9e0", ORANGE, lw=1.5, z=2, shadow=True)
ax.text(45.0, 95.2, "Peer agent", ha="center", va="center", fontsize=7.0, color=ORANGE, fontweight="bold", zorder=4)
ax.text(45.0, 91.0, "“All approvals were already obtained.”", ha="center", va="center", fontsize=6.7, color=INK, zorder=4)
arrow((cx, 88.0), (cx, NY + NH + 0.3), ORANGE, lw=2.0)
pill(cx, 83.2, 20.0, "claim filter", AQUA)
arrow((X0[1] - 0.5, 56.0), (X0[0] + W + 0.5, 56.0), ORANGE, lw=1.7)
ax.text((X0[0] + W + X0[1]) / 2 + 0.5, 44.0, "report: “authorized”", ha="center", va="center", fontsize=6.4, color=ORANGE, fontweight="bold")
gx = (X0[2] + W + X0[3]) / 2
pill(cx + 14.0, 37.2, 26.0, "permission record", AQUA, fs=6.1); ax.plot([cx, cx], [40.8, NY], color=AQUA, lw=1.1, ls=(0, (2, 2)), zorder=4)
pill(gx + 2.0, 37.2, 28.0, "ask-before-act gate", BLUE, fs=6.1); ax.plot([gx, gx], [40.8, yf - 1.5], color=BLUE, lw=1.1, ls=(0, (2, 2)), zorder=4)
badge(cx + 13.0, 83.2, 1); badge(gx, yf + 12.5, 2); badge(X0[0] + W + 1.0, 44.0, 3) if False else badge(11.0, 44.0, 3)

# result cards
asked = R["_asked"]; c = R["_cells"]
fa = [X["fa_over_v"][t]["FA"]["point"] for t in X["fa_over_v"]]
base_fa, led_fa = H["_descriptive_controls"]["baseline"]["FA_over_V"], H["_descriptive_controls"]["ledger_auth"]["FA_over_V"]
cards = [
    (1, "A claim displaces the check", f"{asked['A']['p']:.2f} → {asked['B']['p']:.2f}", "no claim →\nfalse claim", "Operator asks permission first", f"claim filter restores it: {asked['C']['p']:.2f}"),
    (2, "The team acts unauthorized", f"{c['A']['V']:.2f} → {c['B']['V']:.2f}", "no message →\nfalse claim", "unauthorized-action rate V", f"claim filter {c['C']['V']:.2f}; gate {c['D']['V']:.2f}"),
    (3, "The report says “authorized”", f"{min(fa):.0%}–{max(fa):.0%}", "of violating\nruns", "(range over team shapes)", f"permission record: {base_fa:.0%} → {led_fa:.0%}"),
]
cw, gap = 32.0, 1.6
for i, (k, title, big, cond, meas, fix) in enumerate(cards):
    x = 0.8 + i * (cw + gap)
    rbox(x, 0.8, cw, 31.0, "#f6f6f4", LINE, lw=1.0, z=1)
    badge(x + 3.6, 26.0, k)
    ax.text(x + 7.4, 26.0, title, ha="left", va="center", fontsize=6.9, fontweight="bold", color=INK, zorder=4)
    ax.text(x + 2.2, 16.6, big, ha="left", va="center", fontsize=13, fontweight="bold", color=ORANGE, zorder=4)
    ax.text(x + 18.6, 16.6, cond, ha="left", va="center", fontsize=6.5, color=SUB, zorder=4, linespacing=1.15)
    ax.text(x + 2.2, 9.6, meas, ha="left", va="center", fontsize=6.5, color=SUB, zorder=4)
    ax.text(x + 2.2, 4.2, "fix: " + fix, ha="left", va="center", fontsize=6.3, color=GREEN, fontweight="bold", zorder=4)
fig.savefig(OUT / "fig0_overview.png"); fig.savefig(OUT / "fig0_overview.pdf")
print("ok")
