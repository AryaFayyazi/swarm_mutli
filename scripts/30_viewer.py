"""Builds a self-contained replay viewer (paper/viewer.html) from a handful of episodes picked from the raw traces.
Usage: 30_viewer.py [raw_dir] [out.html]. No API calls."""
import html, json, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
RAW = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "outputs/raw"
OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "paper/viewer.html"


def read(name):
    p = RAW / name
    return [json.loads(l) for l in open(p)] if p.exists() else []


def slim(ep, label):
    ev = []
    for t in ep["trace"]:
        k = t["kind"]
        if k == "in" and str(t["content"]).startswith(("[nudge]", "[budget]")):
            continue
        if k == "result":
            continue
        e = {"agent": t["agent"], "kind": k}
        if k == "call":
            e["tool"], e["args"] = t["tool"], t["args"]
        else:
            e["text"] = t["content"] if isinstance(t["content"], str) else json.dumps(t["content"], ensure_ascii=False, indent=1)
        ev.append(e)
    # attach each tool result and checker label from the gateway ledger, in order
    led = [x for x in ep["ledger"]]
    li = 0
    for e in ev:
        if e["kind"] == "call" and li < len(led):
            L = led[li]; li += 1
            e["obs"] = str(L["obs"])[:500]; e["unsafe"] = L["unsafe"]; e["critical"] = L["critical"]; e["blocked"] = bool(L.get("blocked"))
    o = ep["out"]
    return {"label": label, "scenario": ep["scenario_id"], "cf": ep["cf"], "model": ep["cfg"]["model"], "topology": ep["cfg"].get("topology"),
            "assurance": ep["cfg"].get("assurance"), "control": ep.get("control"), "report_source": ep["cfg"].get("report_source", "peer"),
            "events": ev, "V": o["V"], "status": o["report_status"], "goal": o["goal_gt"], "false_assurance": o["false_assurance"],
            "disclosed": o["disclosed"], "n_blocked": o["n_blocked"]}


def pick():
    e1, e3 = read("e1.jsonl"), read("e3.jsonl") + read("e3b.jsonl")
    out = []
    by = {}
    for r in e1 + e3:
        if not r.get("out"):
            continue
        c = r["cfg"]
        key = (r["scenario_id"], c["model"], c.get("topology"), c.get("assurance"), c.get("control_kind") or "none", c.get("report_source", "peer"), bool(c.get("prompt_defense")), bool(c.get("models")))
        by[(key, r["cf"])] = r
    # a violation under relay1 + peer, with its safe twin and the same scenario under the gates
    for (key, cf), r in by.items():
        sc, m, topo, asr, ctl, rs, pdf, mixed = key
        if cf == "unsafe" and topo == "relay1" and asr == "peer" and ctl == "none" and rs == "peer" and not pdf and not mixed and r["out"]["false_assurance"] \
                and "ticket" in json.dumps(r["trace"]).lower():
            twin = by.get((key, "safe"))
            gate = by.get(((sc, m, "relay1", "peer", "ask_gate", "peer", False, False), "unsafe"))
            ledg = by.get(((sc, m, "relay1", "peer", "none", "ledger_auth", False, False), "unsafe"))
            aud = by.get(((sc, m, "relay1", "peer", "aud_trace", "peer", False, False), "unsafe"))
            if twin and gate and ledg:
                out.append(slim(r, "1. Relay, false peer assurance: the unauthorized action and the false report"))
                out.append(slim(twin, "2. Same task, safe twin: the same message is true, no violation"))
                out.append(slim(gate, "3. Same scenario with the ask-before-act gateway rule"))
                out.append(slim(ledg, "4. Same scenario, reporter sees the permission-system record"))
                if aud:
                    out.append(slim(aud, "5. Same scenario with an LLM auditor that sees the tool results"))
                out += pick_filter()
                return out
    return out


def pick_filter():
    """Round 2 (E9): a violation under the false peer message and the same scenario and model with the claim filter."""
    rows = [r for r in read("e9.jsonl") if r.get("out") and r["cfg"].get("topology") == "relay1" and r["cfg"].get("assurance") == "peer"
            and not r["cfg"].get("assurance_text") and (r.get("control") or "none") == "none" and r["cf"] == "unsafe"]
    plain = {(r["scenario_id"], r["cfg"]["model"]): r for r in rows if not r["cfg"].get("claim_filter")}
    filt = {(r["scenario_id"], r["cfg"]["model"]): r for r in rows if r["cfg"].get("claim_filter") == "rewrite"}
    for k in sorted(plain):
        a, b = plain[k], filt.get(k)
        if b and a["out"]["V"] and a["out"]["false_assurance"] and not b["out"]["V"] and b["out"]["report_present"] and any(f["where"] == "peer_message" and f["ok"] for f in b.get("filter", [])):
            return [slim(a, "6. Round 2, fresh scenario: the false peer message without a filter (violation, false report)"),
                    slim(b, "7. Same scenario and model with the claim filter (the claim arrives marked as unverified)")]
    return []


TEMPLATE = r"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>CAPE-Swarm Replay</title><style>
:root{color-scheme:light;--bg:#fcfcfb;--panel:#fff;--ink:#0b0b0b;--sub:#52514e;--line:#e6e5e1;--blue:#2a78d6;--orange:#eb6834;--aqua:#1baf7a;--red:#c8312f;--amber:#b7791f}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){color-scheme:dark;--bg:#1a1a19;--panel:#222221;--ink:#f0efec;--sub:#c3c2b7;--line:#3a3a38;--blue:#3987e5;--orange:#d95926;--aqua:#199e70;--red:#e66767;--amber:#e0a63a}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.45 Georgia,'Times New Roman',serif}
header{padding:14px 16px;border-bottom:1px solid var(--line)}h1{font-size:18px;margin:0 0 4px}.sub{color:var(--sub);font-size:13px}
main{display:grid;grid-template-columns:minmax(0,1.6fr) minmax(0,1fr);gap:16px;padding:16px;max-width:1200px;margin:auto}
@media(max-width:820px){main{grid-template-columns:1fr}}
select,button{font:inherit;padding:6px 10px;border:1px solid var(--line);background:var(--panel);color:var(--ink);border-radius:6px;cursor:pointer}
.bar{display:flex;gap:8px;flex-wrap:wrap;align-items:center;margin-top:8px}input[type=range]{flex:1;min-width:160px}
.ev{background:var(--panel);border:1px solid var(--line);border-left:4px solid var(--c);border-radius:6px;padding:8px 10px;margin:8px 0}
.ev .who{font-size:12px;color:var(--sub);text-transform:uppercase;letter-spacing:.04em}.ev pre{white-space:pre-wrap;margin:4px 0 0;font:12.5px/1.4 ui-monospace,Menlo,monospace}
.Lead{--c:var(--blue)}.Manager{--c:var(--aqua)}.Operator{--c:var(--orange)}.Auditor{--c:var(--sub)}
.chip{display:inline-block;padding:1px 8px;border-radius:10px;font-size:12px;border:1px solid var(--line);margin-left:6px}
.bad{color:var(--red);border-color:var(--red)}.ok{color:var(--aqua);border-color:var(--aqua)}.warn{color:var(--amber);border-color:var(--amber)}
.hit{background:color-mix(in srgb,var(--orange) 25%,transparent);padding:0 2px;border-radius:3px}
.side{position:sticky;top:12px;align-self:start;background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px}
.side h2{font-size:14px;margin:0 0 6px}.kv{display:grid;grid-template-columns:auto 1fr;gap:2px 10px;font-size:13px}.kv b{color:var(--sub);font-weight:normal}
.blocked{background:repeating-linear-gradient(135deg,transparent 0 6px,color-mix(in srgb,var(--sub) 12%,transparent) 6px 12px)}
</style></head><body>
<header><h1>CAPE-Swarm replay</h1><div class="sub">Authorization laundering in an LLM agent swarm. Every tool call is labeled by a rule checker, not by an LLM. Replay data is embedded; no network is used.</div>
<div class="bar"><select id="sel" aria-label="Episode"></select><button id="prev">◀ step</button><button id="next">step ▶</button><button id="all">show all</button><input id="rng" type="range" min="0" max="0" value="0" aria-label="Replay position"></div></header>
<main><section id="tl" aria-live="polite"></section><aside class="side" id="side"></aside></main>
<script id="data" type="application/json">__DATA__</script><script>
const D=JSON.parse(document.getElementById('data').textContent);let cur=0,pos=0;const $=s=>document.querySelector(s);
const esc=s=>String(s).replace(/[&<>]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;'}[c]));
const sel=$('#sel');D.forEach((e,i)=>{const o=document.createElement('option');o.value=i;o.textContent=e.label;sel.appendChild(o)});
function hl(t){return esc(t).replace(/(ticket\s*#?\d{5}|approvals? (were|was) already obtained[^.]*\.|No further approval[^.]*\.)/gi,'<span class="hit">$1</span>')}
function render(){const e=D[cur];const evs=e.events;$('#rng').max=evs.length;$('#rng').value=pos;let h='';
evs.slice(0,pos).forEach(v=>{let body='',chip='';
 if(v.kind==='call'){body='<b>'+esc(v.tool)+'</b>('+esc(JSON.stringify(v.args)).slice(0,300)+')'+(v.obs?'\n→ '+esc(v.obs):'');
  if(v.blocked)chip='<span class="chip warn">blocked by control</span>';else if(v.unsafe)chip='<span class="chip bad">UNAUTHORIZED (rule checker)</span>';else if(v.critical)chip='<span class="chip ok">critical, authorized</span>';}
 else if(v.kind==='report'){body=esc(v.text);chip='<span class="chip">final report</span>'}
 else{body=hl(v.text)}
 h+='<div class="ev '+v.agent+(v.blocked?' blocked':'')+'"><div class="who">'+(v.kind==='in'?'message to ':'')+v.agent+' · '+v.kind+chip+'</div><pre>'+body+'</pre></div>'});
$('#tl').innerHTML=h||'<div class="sub">Press “step ▶” to replay.</div>';
const st=e.status||'(none)';const lie=e.false_assurance;
$('#side').innerHTML='<h2>What really happened</h2><div class="kv"><b>scenario</b><span>'+esc(e.scenario)+'</span><b>twin</b><span>'+(e.cf==='unsafe'?'unsafe (approval claim is false)':'safe (approval claim is true)')+'</span><b>model</b><span>'+esc(e.model)+'</span><b>topology</b><span>'+esc(e.topology)+', assurance: '+esc(e.assurance)+'</span><b>control</b><span>'+esc(e.control)+(e.report_source!=='peer'?' / report: '+esc(e.report_source):'')+'</span></div><hr style="border:0;border-top:1px solid var(--line)"><div class="kv"><b>checker: unauthorized action</b><span>'+(e.V?'<span class="chip bad">YES</span>':'<span class="chip ok">no</span>')+'</span><b>blocked calls</b><span>'+e.n_blocked+'</span><b>goal completed</b><span>'+(e.goal?'yes':'no')+'</span><b>report says</b><span>'+esc(st)+(lie?'<span class="chip bad">false assurance</span>':(e.disclosed?'<span class="chip ok">disclosed</span>':''))+'</span></div>'}
sel.onchange=()=>{cur=+sel.value;pos=0;render()};$('#prev').onclick=()=>{pos=Math.max(0,pos-1);render()};$('#next').onclick=()=>{pos=Math.min(D[cur].events.length,pos+1);render()};
$('#all').onclick=()=>{pos=D[cur].events.length;render()};$('#rng').oninput=e=>{pos=+e.target.value;render()};render();
</script></body></html>"""

if __name__ == "__main__":
    eps = pick()
    if not eps:
        print("no matching episodes found yet"); sys.exit(0)
    OUT.write_text(TEMPLATE.replace("__DATA__", json.dumps(eps).replace("</", "<\\/")))
    print("wrote", OUT, len(eps), "episodes", OUT.stat().st_size // 1024, "KB")
