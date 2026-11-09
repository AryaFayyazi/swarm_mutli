"""Figure 1 (workflow + teaser). Left: the team workflow with the defenses attached where they act, and the log ladder a monitor may read (with AUROC).
Right: three result cards that follow the causal chain (claim displaces the check -> unauthorized action -> false report). Reads results/*.json."""
import json, sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "paper/figs"
OUT.mkdir(parents=True, exist_ok=True)
R = json.load(open(ROOT / "results/round2.json")); H = json.load(open(ROOT / "results/hypotheses.json")); X = json.load(open(ROOT / "results/extra.json"))
BLUE, ORANGE, AQUA, GRAY, INK, SUB, RED, LINE, GREEN = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b", "#52514e", "#c8312f", "#dcdbd6", "#0f7a55"
RAMP = ["#c9dcf5", "#9bbfec", "#6ba2e2", "#2a78d6", "#14447f"]
plt.rcParams.update({"font.family": "DejaVu Sans", "savefig.bbox": "tight", "figure.dpi": 220})
fig = plt.figure(figsize=(6.5, 3.7))
A = fig.add_axes([0.0, 0.0, 0.645, 1.0]); A.set_xlim(0, 100); A.set_ylim(0, 100); A.axis("off")
B = fig.add_axes([0.665, 0.0, 0.335, 1.0]); B.set_xlim(0, 100); B.set_ylim(0, 100); B.axis("off")


def rbox(ax, x, y, w, h, fc="white", ec=LINE, lw=1.0, ls="-", r=1.8, z=1, shadow=False):
    if shadow:
        ax.add_patch(FancyBboxPatch((x + 0.6, y - 0.9), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc="#0000000f", ec="none", zorder=z - 0.5))
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))


def arrow(ax, a, b, col=SUB, lw=1.4, z=3, ms=8):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=ms, color=col, lw=lw, zorder=z, shrinkA=0, shrinkB=0))


def badge(ax, x, y, k, col=INK, r=2.4):
    from matplotlib.patches import Ellipse
    bb = ax.get_position()
    sx = 6.5 * bb.width / 100.0; sy = 3.7 * bb.height / 100.0          # inches per data unit
    ax.add_patch(Ellipse((x, y), 2 * r * sy / sx, 2 * r, fc=col, ec="white", lw=1.2, zorder=9))
    ax.text(x, y, str(k), ha="center", va="center", fontsize=7.0, color="white", fontweight="bold", zorder=10)


def node(x, y, w, h, title, sub, col):
    rbox(A, x, y, w, h, "white", col, lw=1.7, z=2, shadow=True)
    A.add_patch(FancyBboxPatch((x, y + h - 7.4), w, 7.4, boxstyle="round,pad=0,rounding_size=1.8", fc=col, ec=col, lw=0, zorder=3))
    A.add_patch(Rectangle((x, y + h - 7.4), w, 3.0, fc=col, ec="none", zorder=3))
    A.text(x + w / 2, y + h - 3.7, title, ha="center", va="center", fontsize=7.3, color="white", fontweight="bold", zorder=4)
    A.text(x + w / 2, y + (h - 7.4) / 2, sub, ha="center", va="center", fontsize=6.5, color=INK, zorder=4, linespacing=1.2)


def pill(cx, cy, w, text, col, fs=6.3):
    rbox(A, cx - w / 2, cy - 2.7, w, 5.4, "white", col, lw=1.2, ls="--", r=2.2, z=6)
    A.text(cx, cy, text, ha="center", va="center", fontsize=fs, color=col, fontweight="bold", zorder=7)


NY, NH, yf = 52, 24, 63
X0 = [0.5, 27.0, 54.0, 81.0]; W = 18.5
node(X0[0], NY, W, NH, "Human", "gives the task;\nreads only the\nfinal report", GRAY)
node(X0[1], NY, W, NH, "Lead", "no tools; writes\nthe brief and\nthe report", BLUE)
node(X0[2], NY, W, NH, "Operator", "the only agent\nwith tools", BLUE)
node(X0[3], NY, W, NH, "Gateway", "logs every call\nand result; runs\nthe mock tools", INK)
for i in (0, 1, 2):
    arrow(A, (X0[i] + W + 0.4, yf), (X0[i + 1] - 0.4, yf))
A.text((X0[1] + W + X0[2]) / 2, yf + 3.6, "brief", ha="center", fontsize=6.5, color=SUB)
A.text((X0[2] + W + X0[3]) / 2, yf + 3.6, "calls", ha="center", fontsize=6.5, color=SUB)
cx = X0[1] + W / 2
rbox(A, 8.5, 86.2, 56.0, 12.6, "#fde9e0", ORANGE, lw=1.6, z=2, shadow=True)
A.text(36.5, 94.6, "Peer agent", ha="center", va="center", fontsize=7.0, color=ORANGE, fontweight="bold", zorder=4)
A.text(36.5, 90.0, "“All approvals were already obtained.”", ha="center", va="center", fontsize=6.7, color=INK, zorder=4)
arrow(A, (cx, 86.2), (cx, NY + NH + 0.3), ORANGE, lw=2.2)
pill(cx, 81.0, 24.0, "claim filter", AQUA)
arrow(A, (X0[1] - 0.4, 57.5), (X0[0] + W + 0.4, 57.5), ORANGE, lw=1.8)
A.text((X0[0] + W + X0[1]) / 2, 47.9, "report: “authorized”", ha="center", va="center", fontsize=6.4, color=ORANGE, fontweight="bold")
pill(36.0, 39.0, 28.0, "permission record", AQUA, fs=6.1); A.plot([cx, cx], [41.7, NY], color=AQUA, lw=1.1, ls=(0, (2, 2)), zorder=4)
gx = (X0[2] + W + X0[3]) / 2
pill(gx + 3.0, 39.0, 33.0, "ask-before-act gate", BLUE, fs=6.1); A.plot([gx, gx], [41.7, yf - 1.2], color=BLUE, lw=1.1, ls=(0, (2, 2)), zorder=4)
badge(A, 52.0, 81.0, 1); badge(A, gx, yf + 9.0, 2); badge(A, 7.0, 47.9, 3)

# (4) the log ladder a monitor may read, with AUROC (Qwen3.5-397B judge)
tb = H["_table"]
qk = [k for k in tb if k.startswith("judge:qwen3.5-397b:")]
au = {k.split(":")[-1]: tb[k]["auroc"] for k in qk}
badge(A, 3.2, 29.5, 4)
A.text(7.6, 29.5, "What a monitor may read, and how well it detects a violation (AUROC)", ha="left", va="center", fontsize=6.5, fontweight="bold", color=INK)
names = ["report", "messages", "calls", "calls +\nresults", "everything"]
for k in range(5):
    x = 0.5 + k * 20.0
    rbox(A, x, 1.0, 18.8, 23.0, RAMP[k], RAMP[k], lw=0, r=1.6, z=2)
    tc = "white" if k >= 3 else INK
    A.text(x + 9.4, 19.4, f"L{k}", ha="center", va="center", fontsize=7.0, fontweight="bold", color=tc, zorder=4)
    A.text(x + 9.4, 13.0, names[k], ha="center", va="center", fontsize=6.4, color=tc, zorder=4, linespacing=1.1)
    A.text(x + 9.4, 5.4, f"{au['L%d' % k]:.2f}", ha="center", va="center", fontsize=8.6, fontweight="bold", color=tc, zorder=4)

# result cards (right)
asked = R["_asked"]; c = R["_cells"]
fa = [X["fa_over_v"][t]["FA"]["point"] for t in X["fa_over_v"]]
base_fa, led_fa = H["_descriptive_controls"]["baseline"]["FA_over_V"], H["_descriptive_controls"]["ledger_auth"]["FA_over_V"]
cards = [
    (1, "A claim displaces the check", f"{asked['A']['p']:.2f} → {asked['B']['p']:.2f}", ["Operator asks permission first", "(no claim → false claim)"], f"claim filter restores it: {asked['C']['p']:.2f}"),
    (2, "The team acts unauthorized", f"{c['A']['V']:.2f} → {c['B']['V']:.2f}", ["unauthorized-action rate V", "(no message → false claim)"], f"claim filter {c['C']['V']:.2f}; gate {c['D']['V']:.2f}"),
    (3, "The report says “authorized”", f"{min(fa):.0%}–{max(fa):.0%}", ["of violating runs, by team shape", "(unsafe twins, no control)"], f"permission record: {base_fa:.0%} → {led_fa:.0%}"),
]
for i, (k, title, big, sub, fix) in enumerate(cards):
    y = 68.5 - i * 33.6
    rbox(B, 1.0, y, 98.0, 30.0, "#f6f6f4", LINE, lw=1.0, z=1)
    badge(B, 7.5, y + 25.4, k)
    B.text(13.5, y + 25.4, title, ha="left", va="center", fontsize=6.8, fontweight="bold", color=INK, zorder=4)
    B.text(5.0, y + 16.2, big, ha="left", va="center", fontsize=14, fontweight="bold", color=ORANGE, zorder=4)
    B.text(5.0, y + 9.4, sub[0], ha="left", va="center", fontsize=6.5, color=SUB, zorder=4)
    B.text(5.0, y + 5.9, sub[1], ha="left", va="center", fontsize=6.5, color=SUB, zorder=4)
    B.text(5.0, y + 2.4, "fix: " + fix, ha="left", va="center", fontsize=6.3, color=GREEN, fontweight="bold", zorder=4)
fig.savefig(OUT / "fig0_overview.png"); fig.savefig(OUT / "fig0_overview.pdf")
print("ok")
