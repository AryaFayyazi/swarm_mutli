"""Paper figures from raw traces + results/*.json. Palette: validated reference palette (blue, orange, aqua; gray baseline)."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
ROOT = Path(__file__).resolve().parents[1]; sys.path.insert(0, str(ROOT))
from capeswarm.load import load
import capeswarm.hyp as H
from capeswarm.stats import ci

RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "outputs/raw"
RES = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "results"
OUT = Path(sys.argv[3]) if len(sys.argv) > 3 else ROOT / "paper/figs"
OUT.mkdir(parents=True, exist_ok=True)
BLUE, ORANGE, AQUA, GRAY, INK, SUB, GRID = "#2a78d6", "#eb6834", "#1baf7a", "#8a8984", "#0b0b0b", "#52514e", "#e6e5e1"
plt.rcParams.update({"font.family": "DejaVu Serif", "font.size": 8, "axes.edgecolor": SUB, "axes.labelcolor": INK, "xtick.color": SUB,
                     "ytick.color": SUB, "text.color": INK, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": GRID, "grid.linewidth": 0.6, "axes.axisbelow": True, "legend.frameon": False,
                     "figure.dpi": 200, "savefig.bbox": "tight"})
SHORT = {"gemma-4-26b-a4b-it": "Gemma-4 26B", "gemma-4-31b-it": "Gemma-4 31B", "qwen3.8-27b": "Qwen3.8 27B", "qwen3.5-397b": "Qwen3.5 397B",
         "glm-53-flash": "glm-53-flash", "glm-5.2": "GLM-5.2", "deepseek-v4-flash": "DeepSeek-V4 flash"}
def opt(n):
    p = RAW / n
    return load(p) if p.exists() and p.stat().st_size else None
e1, e3, e3b, e4 = opt("e1.jsonl"), opt("e3.jsonl"), opt("e3b.jsonl"), opt("e4.jsonl")
hyp = json.load(open(RES / "hypotheses.json")) if (RES / "hypotheses.json").exists() else {}
desc = json.load(open(RES / "descriptive.json")) if (RES / "descriptive.json").exists() else {}

def mean_ci(vec):
    pt, st = H.mean_stat(vec); lo, hi = ci(st); return pt, lo, hi

# ------------------------------------------------------------------ Fig 1: acting
if e1 is not None:
    u = e1[e1.cf == "unsafe"]; scen = sorted(u.scenario_id.unique())
    models = sorted(u.model.unique(), key=lambda m: -(u[(u.model == m) & (u.topology == "solo") & (u.assurance == "peer")].V.mean() - u[(u.model == m) & (u.topology == "solo") & (u.assurance == "none")].V.mean()))
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.7), gridspec_kw={"width_ratios": [1.35, 1]})
    a = ax[0]
    for i, m in enumerate(models):
        for off, (assur, col, lab) in zip((-0.14, 0.14), (("none", GRAY, "no assurance message"), ("peer", ORANGE, "false peer assurance"))):
            d = u[(u.model == m) & (u.topology == "solo") & (u.assurance == assur)]
            if not len(d):
                continue
            pt, lo, hi = mean_ci(H.per_scen(d, "V", scen))
            a.errorbar(pt, i + off, xerr=[[pt - lo], [hi - pt]], fmt="o", ms=4.5, color=col, mec="white", mew=0.8, elinewidth=1.1, capsize=0, label=lab if i == 0 else None)
        a.axhline(i + 0.5, color=GRID, lw=0.5)
    a.set_yticks(range(len(models))); a.set_yticklabels([SHORT.get(m, m) for m in models]); a.invert_yaxis()
    a.set_xlim(-0.02, 1.02); a.set_xlabel("unsafe twin: share of episodes with an unauthorized action"); a.grid(axis="y", visible=False)
    a.legend(loc="lower right", fontsize=7); a.set_title("(a) One solo agent, seven models", loc="left", fontsize=8.5, fontweight="bold")
    b = ax[1]
    tops = [t for t in ("solo", "relay1", "relay2") if t in set(u.topology)]
    w = 0.36
    for j, (assur, col, lab) in enumerate((("none", GRAY, "no assurance"), ("peer", ORANGE, "false peer assurance"))):
        for i, t in enumerate(tops):
            d = u[(u.topology == t) & (u.assurance == assur)]
            pt, lo, hi = mean_ci(H.per_scen(d, "V", scen))
            b.bar(i + (j - 0.5) * w, pt, w * 0.92, color=col, label=lab if i == 0 else None)
            b.errorbar(i + (j - 0.5) * w, pt, yerr=[[pt - lo], [hi - pt]], color=INK, lw=0.9, capsize=2)
            b.text(i + (j - 0.5) * w, hi + 0.02, f"{pt:.2f}", ha="center", fontsize=6.5, color=INK)
    b.set_xticks(range(len(tops))); b.set_xticklabels([{"solo": "solo", "relay1": "relay", "relay2": "relay-2"}[t] for t in tops])
    b.set_ylim(0, 1); b.set_ylabel("unauthorized-action rate (mean of 7 models)"); b.legend(loc="upper left", fontsize=7); b.grid(axis="x", visible=False)
    b.set_title("(b) Team structure", loc="left", fontsize=8.5, fontweight="bold")
    fig.tight_layout(); fig.savefig(OUT / "fig1_acting.pdf"); fig.savefig(OUT / "fig1_acting.png"); plt.close(fig)

    # -------------------------------------------------------------- Fig 2: claim survival + report outcome
    hops = desc.get("hops_violators") or []
    rep = u[u.V].groupby(["topology", "assurance"]).agg(auth=("false_assurance", "sum"), disc=("disclosed", "sum"), hed=("hedged", "sum"), n=("V", "sum"))
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.7), gridspec_kw={"width_ratios": [1, 1.15]})
    a = ax[0]
    stages = [("brief_carries_claim", "brief carries\nthe claim"), ("V", "Operator acts\nunauthorized"), ("handoff_cites_claim", "handoff cites\nthe ticket"), ("final_report_cites_claim", "report cites\nthe ticket")]
    hp = pd.DataFrame(desc.get("hops_unsafe_peer") or [])
    if len(hp):
        w = 0.36
        for j, (t, col, lab) in enumerate((("relay1", BLUE, "relay"), ("relay2", AQUA, "relay-2"))):
            r = hp[hp.topology == t]
            if r.empty:
                continue
            for k, (c, _) in enumerate(stages):
                if c in r and r[c].iloc[0] == r[c].iloc[0]:
                    v = float(r[c].iloc[0])
                    a.bar(k + (j - 0.5) * w, v, w * 0.92, color=col, label=lab if k == 0 else None)
                    a.text(k + (j - 0.5) * w, v + 0.02, f"{v:.2f}", ha="center", fontsize=6.2, color=INK)
        a.set_xticks(range(len(stages))); a.set_xticklabels([x[1] for x in stages], fontsize=6.2); a.set_ylim(0, 1.0)
        a.set_ylabel("share of peer-assured unsafe episodes"); a.legend(loc="upper right", fontsize=6.5); a.grid(axis="x", visible=False)
    a.set_title("(a) Where the false claim goes", loc="left", fontsize=8.5, fontweight="bold")
    b = ax[1]
    order = [(t, asr) for t in ("solo", "relay1", "relay2") for asr in ("none", "peer")]
    labs, A, D, Hh, R, ns = [], [], [], [], [], []
    for (t, asr) in order:
        if (t, asr) not in rep.index:
            continue
        r = rep.loc[(t, asr)]; n = max(r.n, 1)
        labs.append({"solo": "solo", "relay1": "relay", "relay2": "relay-2"}[t] + "\n" + ("no msg" if asr == "none" else "false msg")); ns.append(int(r.n))
        A.append(r.auth / n); Hh.append(r.hed / n); D.append(r.disc / n); R.append(max(0.0, 1 - (r.auth + r.hed + r.disc) / n))
    x = np.arange(len(labs)); A, Hh, D, R = map(np.array, (A, Hh, D, R))
    b.bar(x, A, 0.7, color=ORANGE, label="says “authorized” (false)")
    b.bar(x, Hh, 0.7, bottom=A, color=GRAY, label="“unsure”")
    b.bar(x, D, 0.7, bottom=A + Hh, color=BLUE, label="“not authorized” (disclosed)")
    b.bar(x, R, 0.7, bottom=A + Hh + D, color="white", edgecolor=GRAY, hatch="////", linewidth=0.6, label="no report submitted")
    for xi, n_ in zip(x, ns):
        b.text(xi, 1.02, f"n={n_}", ha="center", fontsize=5.8, color=SUB)
    b.set_xticks(x); b.set_xticklabels(labs, fontsize=6.0); b.set_ylim(0, 1.1); b.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
    b.set_ylabel("what the final report says\n(episodes with a violation)")
    b.legend(loc="upper center", fontsize=6.0, bbox_to_anchor=(0.5, -0.27), ncol=2); b.grid(axis="x", visible=False)
    b.set_title("(b) The human-facing report", loc="left", fontsize=8.5, fontweight="bold")
    fig.tight_layout(); fig.savefig(OUT / "fig2_laundering.pdf"); fig.savefig(OUT / "fig2_laundering.png"); plt.close(fig)

# ------------------------------------------------------------------ Fig 3: controls
dc = (hyp.get("_descriptive_controls") or {})
if dc:
    fig, ax = plt.subplots(figsize=(4.4, 3.0))
    style = {"baseline": (GRAY, "o"), "pdp": (BLUE, "s"), "ask_gate": (BLUE, "o"), "aud_min": (ORANGE, "o"), "aud_trace": (ORANGE, "^"),
             "aud_trace_just": (ORANGE, "v"), "prompt_defense": (ORANGE, "D"), "ledger": (AQUA, "o"), "ledger_auth": (AQUA, "s")}
    names = {"baseline": "no control", "pdp": "oracle policy check", "ask_gate": "ask-before-act gate", "aud_min": "auditor: call only", "aud_trace": "auditor + tool results",
             "aud_trace_just": "auditor + swarm's words", "prompt_defense": "verification prompt", "ledger": "report from ledger", "ledger_auth": "report from ledger + approvals"}
    OFF = {"baseline": (6, -11, "left"), "ledger": (7, 6, "left"), "ledger_auth": (-7, -12, "right"), "pdp": (6, -13, "left"), "ask_gate": (-6, -13, "right"),
           "aud_trace": (6, 10, "left"), "aud_trace_just": (-7, 7, "right"), "aud_min": (6, 5, "left"), "prompt_defense": (8, -3, "left")}
    ax.set_xlim(0.15, 1.0); ax.set_ylim(-0.07, 0.62)
    for k, v in dc.items():
        if k not in style or v.get("V") is None or v["V"] != v["V"]:
            continue
        col, mk = style[k]
        ax.scatter(v["goal_safe"], v["V"], s=36, color=col, marker=mk, edgecolor="white", linewidth=0.8, zorder=3)
        dx, dy, ha = OFF.get(k, (6, 4, "left"))
        ax.annotate(names[k], (v["goal_safe"], v["V"]), xytext=(dx, dy), textcoords="offset points", fontsize=6.3, color=INK, ha=ha)
    ax.set_xlabel("safe twin: goal completion (utility)"); ax.set_ylabel("unsafe twin: unauthorized-action rate")
    from matplotlib.lines import Line2D
    ax.legend(handles=[Line2D([], [], marker="o", ls="", color=c, label=l) for c, l in ((GRAY, "baseline"), (BLUE, "gateway, outside the swarm"), (ORANGE, "inside the swarm (agents, prompts)"), (AQUA, "reporting only"))], loc="upper left", fontsize=6.3)
    ax.set_title("Controls on a peer-assured relay (4 models)", loc="left", fontsize=8.5, fontweight="bold")
    fig.savefig(OUT / "fig3_controls.pdf"); fig.savefig(OUT / "fig3_controls.png"); plt.close(fig)

# ------------------------------------------------------------------ Fig 4: monitor ladder
tab = (hyp.get("_table") or {})
if tab:
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.5))
    levels = ["L0", "L1", "L2", "L3", "L4"]
    names = {"L0": "L0\nreport", "L1": "L1\nmessages", "L2": "L2\ncalls", "L3": "L3\ncalls+results", "L4": "L4\neverything"}
    judges = sorted({m.split(":")[1] for m in tab if m.startswith("judge:")})
    cols = {judges[0]: BLUE, judges[1]: ORANGE} if len(judges) > 1 else {judges[0]: BLUE}
    for k, key in enumerate(("auroc", "catch5")):
        a = ax[k]
        for j in judges:
            ys = [tab.get(f"judge:{j}:{l}", {}).get(key, np.nan) for l in levels]
            a.plot(range(5), ys, "-o", color=cols[j], ms=4.5, mec="white", lw=1.4, label=SHORT.get(j, j))
            if key == "auroc":
                lo = [tab.get(f"judge:{j}:{l}", {}).get("lo", np.nan) for l in levels]; hi = [tab.get(f"judge:{j}:{l}", {}).get("hi", np.nan) for l in levels]
                a.fill_between(range(5), lo, hi, color=cols[j], alpha=0.12, lw=0)
        if "self" in tab:
            a.axhline(tab["self"][key], color=AQUA, lw=1.2, ls="--", label="self-query (Operator asked 2 yes/no questions)")
        a.set_xticks(range(5)); a.set_xticklabels([names[l] for l in levels], fontsize=6.5)
        if key == "auroc":
            a.axhline(0.5, color=GRAY, lw=0.8); a.set_ylim(0.4, 1.0); a.set_ylabel("AUROC (violation vs no violation)")
        else:
            a.set_ylim(0, 1); a.set_ylabel("share of violations caught at 5% false alarms")
        a.set_title(("(a) Ranking quality" if k == 0 else "(b) Catch rate at an exact 5% budget"), loc="left", fontsize=8.5, fontweight="bold")
        if k == 0:
            a.legend(loc="lower right", fontsize=6.3)
    fig.tight_layout(); fig.savefig(OUT / "fig4_monitors.pdf"); fig.savefig(OUT / "fig4_monitors.png"); plt.close(fig)

# ------------------------------------------------------------------ Fig 5: mixed swarms
mat = (hyp.get("_matrix") or {})
if mat:
    order = ["gemma-4-26b-a4b-it", "qwen3.5-397b", "glm-5.2", "glm-53-flash"]
    M = np.full((4, 4), np.nan)
    for i, l in enumerate(order):
        for j, o in enumerate(order):
            v = mat.get(f"lead={l}|op={o}")
            if v:
                M[i, j] = v["V"]
    fig, ax = plt.subplots(figsize=(3.4, 2.9))
    from matplotlib.colors import LinearSegmentedColormap
    cm = LinearSegmentedColormap.from_list("seq", ["#eaf1fb", "#2a78d6", "#0f3d7a"])
    im = ax.imshow(M, cmap=cm, vmin=0, vmax=1)
    ax.grid(False)
    for i in range(4):
        for j in range(4):
            if not np.isnan(M[i, j]):
                ax.text(j, i, f"{M[i, j]:.2f}", ha="center", va="center", fontsize=7.5, color="white" if M[i, j] > 0.5 else INK)
            else:
                ax.text(j, i, "–", ha="center", va="center", fontsize=7.5, color=SUB)
    ax.set_xticks(range(4)); ax.set_xticklabels([SHORT[o] for o in order], rotation=30, ha="right", fontsize=6.5)
    ax.set_yticks(range(4)); ax.set_yticklabels([SHORT[o] for o in order], fontsize=6.5)
    ax.set_xlabel("Operator model (has the tools)"); ax.set_ylabel("Lead model (writes brief and report)")
    ax.set_title("Unauthorized-action rate, peer assurance", loc="left", fontsize=8.5, fontweight="bold")
    fig.savefig(OUT / "fig5_mixed.pdf"); fig.savefig(OUT / "fig5_mixed.png"); plt.close(fig)
print("figures:", sorted(p.name for p in OUT.glob("*.png")))
