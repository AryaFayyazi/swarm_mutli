"""Figure 1 (teaser): the failure chain and where each fix attaches. Five nodes, one false claim, three numbered problems.
Palette: reference palette (blue, orange, aqua, gray, ink)."""
import sys
from pathlib import Path
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle

ROOT = Path(__file__).resolve().parents[1]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "paper/figs"
OUT.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, AQUA, GRAY, INK, SUB = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b", "#52514e"
plt.rcParams.update({"font.family": "DejaVu Sans", "savefig.bbox": "tight", "figure.dpi": 220})
fig, ax = plt.subplots(figsize=(7.2, 3.3)); ax.set_xlim(0, 100); ax.set_ylim(0, 52); ax.axis("off")


def rbox(x, y, w, h, fc, ec, lw=1.4, ls="-", r=1.6, z=1):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fc, ec=ec, lw=lw, ls=ls, zorder=z))


def node(x, title, sub, col, y=25, w=15, h=11):
    rbox(x, y, w, h, "white", col, lw=1.8, z=2)
    rbox(x, y + h - 4.0, w, 4.0, col, col, lw=0, z=3)
    ax.text(x + w / 2, y + h - 2.0, title, ha="center", va="center", fontsize=8.6, color="white", fontweight="bold", zorder=4)
    ax.text(x + w / 2, y + (h - 4.0) / 2, sub, ha="center", va="center", fontsize=6.6, color=INK, zorder=4, linespacing=1.25)


def arrow(a, b, col=SUB, lw=1.6, rad=0.0):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle="-|>", mutation_scale=10, color=col, lw=lw, connectionstyle=f"arc3,rad={rad}", zorder=3, shrinkA=0, shrinkB=0))


def badge(x, y, k, col=INK):
    ax.add_patch(Circle((x, y), 2.1, fc=col, ec="white", lw=1.4, zorder=8))
    ax.text(x, y, str(k), ha="center", va="center", fontsize=7.6, color="white", fontweight="bold", zorder=9)


X = [0.5, 21.5, 42.5, 63.5, 84.5]
node(X[0], "Human", "gives the task;\nreads only the\nfinal report", GRAY)
node(X[1], "Lead", "no tools; writes\nthe brief and\nthe report", BLUE)
node(X[2], "Operator", "the only agent\nthat can use\ntools", BLUE)
node(X[3], "Gateway", "logs every call\nand its result;\nagents cannot\nedit the log", INK, y=23.5, h=14.5)
node(X[4], "Tools", "files, database,\nmessages, shell,\npermission\nsystem", GRAY, y=23.5, h=14.5)
for i in (0, 1, 2, 3):
    arrow((X[i] + 15.2, 30.5), (X[i + 1] - 0.2, 30.5))
ax.text((X[1] + 15 + X[2]) / 2, 28.0, "brief", ha="center", fontsize=6.2, color=SUB)
ax.text((X[2] + 15 + X[3]) / 2, 28.0, "calls", ha="center", fontsize=6.2, color=SUB)

# the peer's false claim, with the optional filter on its path
rbox(10.5, 42.2, 37, 8.4, "#fde9e0", ORANGE, lw=1.6, z=2)
ax.text(29, 48.2, "Peer agent", ha="center", va="center", fontsize=8.0, color=ORANGE, fontweight="bold", zorder=4)
ax.text(29, 44.7, "“All approvals were already obtained.”", ha="center", va="center", fontsize=6.8, color=INK, zorder=4)
ax.text(48.8, 46.4, "unverified, and false\nin the unsafe twin", ha="left", va="center", fontsize=6.2, color=ORANGE, zorder=4, linespacing=1.2)
arrow((29, 42.2), (29, 36.4), ORANGE, lw=2.0)
rbox(20.2, 38.0, 17.6, 3.0, "white", AQUA, lw=1.2, ls="--", r=1.0, z=5)
ax.text(29, 39.5, "optional claim filter", ha="center", va="center", fontsize=5.9, color=AQUA, fontweight="bold", zorder=6)

# the report goes back to the human (routed under the nodes)
ax.plot([29, 29, 8], [24.8, 20.5, 20.5], color=ORANGE, lw=1.6, zorder=3, solid_capstyle="butt")
arrow((8, 20.5), (8, 24.8), ORANGE, lw=1.6)
ax.text(22.5, 17.6, "report: “authorized”", ha="center", va="center", fontsize=6.8, color=ORANGE, fontweight="bold")
badge(57.2, 36.3, 1); badge(10.2, 17.6, 2); badge(78.6, 38.2, 3)

# three problems and their fixes
cards = [(0.5, 1, "Acts without approval", ["Fix: ask-before-act gate;", "claim filter"]),
         (34.0, 2, "Report says “authorized”", ["Fix: show the Lead the", "permission record"]),
         (67.5, 3, "Monitor does not see it", ["Fix: read the gateway log", "with tool results"])]
for x, k, t, f in cards:
    rbox(x, 0.3, 32.0, 12.2, "#f6f6f4", "#dcdbd6", lw=1.0, r=1.8, z=1)
    badge(x + 3.0, 8.8, k)
    ax.text(x + 6.0, 8.8, t, ha="left", va="center", fontsize=6.9, color=INK, fontweight="bold", zorder=4)
    ax.text(x + 6.0, 5.2, f[0], ha="left", va="center", fontsize=6.2, color=SUB, zorder=4)
    ax.text(x + 6.0, 2.6, f[1], ha="left", va="center", fontsize=6.2, color=SUB, zorder=4)
fig.savefig(OUT / "fig0_overview.png"); fig.savefig(OUT / "fig0_overview.pdf")
print("ok")
