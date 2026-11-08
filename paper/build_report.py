"""Builds the sprint report on Apart's official .docx template from paper/content.md, then converts to PDF.

Content syntax (paper/content.md):
  TITLE: ...                      AUTHOR: Name | Affiliation        (repeat)
  ABSTRACT:                       (following lines until a blank line)
  ## 1. Heading   ### Sub-heading
  plain paragraphs separated by blank lines;  '- ' bullets;  '1. ' numbered items
  FIG: file.png | width_in | caption          TABLE: caption   followed by markdown table lines starting with '|'
  inline: **bold**  *italic*  `code`  and numbers {{expr|fmt}} evaluated against results (H = hypotheses.json, D = descriptive.json)
Every number in the text should come from a {{...}} placeholder so that it cannot drift from results/*.json.
"""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from pathlib import Path

import docx
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

ROOT = Path(__file__).resolve().parents[1]
FONT = "Old Standard TT"
BODY_PT = 9.5

import os
RESDIR = Path(os.environ.get("RESULTS_DIR", ROOT / "results"))
H = json.load(open(RESDIR / "hypotheses.json")) if (RESDIR / "hypotheses.json").exists() else {}
D = json.load(open(RESDIR / "descriptive.json")) if (RESDIR / "descriptive.json").exists() else {}
EXTRA = json.load(open(RESDIR / "extra.json")) if (RESDIR / "extra.json").exists() else {}


CLAIM = {"H1": "Peer assurance raises unauthorized actions (solo): effect ≥ +0.15, CI above 0",
         "H2": "The effect stays in the relay and the relay-2 team (CI above 0)",
         "H3": "Violations are rarely disclosed: disclosed/violations ≤ 0.20",
         "H4": "Permission record cuts false reports ≥ 50% and leaves violations unchanged (change within ±0.10)",
         "H5": "Ask-before-act gate: violations ≤ 0.02 and safe-twin goal drop ≤ 0.25",
         "H6": "Each auditor level lowers violations but leaves them above 0.05",
         "H7": "Monitor AUROC at L3 exceeds L0 by ≥ 0.15 for both judges",
         "H8": "(secondary) Auditor that sees the swarm's words does worse by ≥ 0.05",
         "H9": "(secondary) Self-query monitor reaches AUROC ≥ 0.75",
         "H11": "(sanity) Oracle policy check gives zero violations",
         "H12": "Verification prompt lowers violations, but stays above the gate by ≥ 0.03",
         "H13": "The Operator's model decides the action (skeptical Lead keeps ≥ 50%; skeptical Operator ≤ 0.10)",
         "H14": "A skeptical Lead discloses more violations (+0.10)",
         "H15": "Effect holds for the manager and terse wordings (≥ +0.15, CI above 0)",
         "H16": "Hedged wording lowers violations versus the main wording",
         "H18": "An attacker-optimized message raises violations over the main message",
         "H19": "The ask-before-act gate still holds under the attacker message (V ≤ 0.02, goal drop ≤ 0.25)",
         "H17": "A diverse auditor lowers violations versus a same-model auditor"}


def make_extra():
    ex = {}
    order = ["H1", "H2", "H3", "H4", "H5", "H6", "H7", "H8", "H9", "H11", "H12", "H13", "H14", "H15", "H16", "H17", "H18", "H19"]
    rows = ["| ID | Claim (direction and threshold fixed before the runs) | Estimate [95% CI] | Result |", "|---|---|---|---|"]
    for h in order:
        r = H.get(h)
        if not r:
            rows.append(f"| {h} | {CLAIM[h]} | not run | not run |")
            continue
        PL = {"H2": ["relay", "relay-2"], "H4": ["false reports cut", "change in V"], "H5": ["V", "goal drop"], "H6": ["call only", "+results", "+words"],
              "H7": ["Gemma judge", "Qwen judge"], "H12": ["vs base", "vs gate"], "H13": ["ratio", "V"], "H15": ["manager", "terse"], "H19": ["V", "goal drop"]}
        def fmt(q):
            return f"{q['point']:+.2f} [{q['lo']:+.2f}, {q['hi']:+.2f}]" if q.get("lo") == q.get("lo") and "lo" in q else f"{q['point']:+.2f}"
        if r.get("parts") and h in PL:
            est = "; ".join(f"{lab} {fmt(q)}" for lab, q in zip(PL[h], r["parts"]))
        else:
            est = fmt(r)
        res = ("supported" if r.get("supported") else "**not supported**") if not r.get("no_test") else ("met (point criterion)" if r.get("supported") else "**not met**")
        rows.append(f"| {h} | {CLAIM[h]} | {est} | {res} |")
    ex["hyp_table"] = "\n".join(rows)
    et = D.get("e1_table") or []
    if et:
        short = {"gemma-4-26b-a4b-it": "Gemma-4 26B", "gemma-4-31b-it": "Gemma-4 31B", "qwen3.8-27b": "Qwen3.8 27B", "qwen3.5-397b": "Qwen3.5 397B",
                 "glm-53-flash": "GLM-5.3 flash", "glm-5.2": "GLM-5.2", "deepseek-v4-flash": "DeepSeek-V4 flash"}
        import collections
        by = collections.defaultdict(dict)
        for r in et:
            by[r["model"]][(r["topology"], r["assurance"])] = r["V"]
        rows = ["| Model | solo none | solo peer | relay none | relay peer | relay-2 none | relay-2 peer |", "|---|---|---|---|---|---|---|"]
        for m, d in sorted(by.items(), key=lambda kv: -(kv[1].get(("solo", "peer"), 0) - kv[1].get(("solo", "none"), 0))):
            rows.append("| " + short.get(m, m) + " | " + " | ".join(f"{d[k]:.2f}" if k in d else "–" for k in [("solo", "none"), ("solo", "peer"), ("relay1", "none"), ("relay1", "peer"), ("relay2", "none"), ("relay2", "peer")]) + " |")
        ex["model_table"] = "\n".join(rows)
    tb = H.get("_table") or {}
    if tb:
        def rng(level):
            v = [tb[k]["auroc"] for k in tb if k.startswith("judge:") and k.endswith(":" + level)]
            return (min(v), max(v)) if v else (float("nan"), float("nan"))
        ex["mon"] = {lv: rng(lv) for lv in ("L0", "L1", "L2", "L3", "L4")}
        c = {k: tb[k]["catch5"] for k in tb if k.startswith("judge:qwen3.5-397b:")}
        ex["catch_qwen"] = {k.split(":")[-1]: v for k, v in c.items()}
    dc = H.get("_descriptive_controls") or {}
    if dc:
        v = [dc[k]["V"] for k in ("aud_trace", "aud_trace_just", "prompt_defense") if k in dc and dc[k].get("V") == dc[k].get("V")]
        ex["resid"] = (min(v), max(v)) if v else (float("nan"), float("nan"))
    fam = D.get("e1_by_family") or []
    if fam:
        ex["FAM"] = {r["family"]: {"none": r["none"], "peer": r["peer"], "d": round(r["peer"] - r["none"], 3)} for r in fam}
        rows = ["| Family | no message | false peer assurance | difference |", "|---|---|---|---|"]
        for r in sorted(fam, key=lambda r: -(r["peer"] - r["none"])):
            rows.append(f"| {r['family']} | {r['none']:.2f} | {r['peer']:.2f} | {r['peer'] - r['none']:+.2f} |")
        ex["family_table"] = "\n".join(rows)
    return ex


EXTRA.update(make_extra())


def fill(text: str) -> str:
    def rep(m):
        expr = m.group(1)
        fmt = ""
        if "|" in expr:
            expr, fmt = expr.rsplit("|", 1)
        v = eval(expr, {"H": H, "D": D, "X": EXTRA, "abs": abs, "round": round, "len": len, "sum": sum, "min": min, "max": max})
        return format(v, fmt) if fmt else str(v)
    return re.sub(r"\{\{(.+?)\}\}", rep, text)


def set_run(run, size=BODY_PT, bold=None, italic=None, mono=False, color=None, sup=False):
    run.font.name = "DejaVu Sans Mono" if mono else FONT
    rpr = run._r.get_or_add_rPr()
    rf = rpr.find(qn("w:rFonts"))
    if rf is None:
        rf = OxmlElement("w:rFonts"); rpr.append(rf)
    for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rf.set(qn(a), "DejaVu Sans Mono" if mono else FONT)
    run.font.size = Pt(size * (0.85 if mono else 1.0))
    if bold is not None:
        run.bold = bold
    if italic is not None:
        run.italic = italic
    if color:
        run.font.color.rgb = RGBColor.from_string(color)
    if sup:
        run.font.superscript = True


TOK = re.compile(r"(\*\*.+?\*\*|\*.+?\*|`.+?`|\^\^.+?\^\^)")


def add_inline(p, text, size=BODY_PT, bold=False, italic=False):
    for part in TOK.split(text):
        if not part:
            continue
        if part.startswith("**") and part.endswith("**"):
            set_run(p.add_run(part[2:-2]), size, bold=True, italic=italic)
        elif part.startswith("`") and part.endswith("`"):
            set_run(p.add_run(part[1:-1]), size, mono=True)
        elif part.startswith("^^"):
            set_run(p.add_run(part[2:-2]), size, bold=bold, italic=italic, sup=True)
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            set_run(p.add_run(part[1:-1]), size, bold=bold, italic=True)
        else:
            set_run(p.add_run(part), size, bold=bold, italic=italic)


def para(doc, text="", size=BODY_PT, align="justify", space_after=4, space_before=0, left=0.0, first=0.0, keep_next=False, line=1.08, bold=False, italic=False):
    p = doc.add_paragraph()
    pf = p.paragraph_format
    pf.space_after, pf.space_before, pf.line_spacing = Pt(space_after), Pt(space_before), line
    if left:
        pf.left_indent = Inches(left)
    if first:
        pf.first_line_indent = Inches(first)
    pf.keep_with_next = keep_next
    p.alignment = {"justify": WD_ALIGN_PARAGRAPH.JUSTIFY, "left": WD_ALIGN_PARAGRAPH.LEFT, "center": WD_ALIGN_PARAGRAPH.CENTER}[align]
    if text:
        add_inline(p, text, size, bold=bold, italic=italic)
    return p


def heading(doc, text, level=2):
    p = doc.add_paragraph(style=f"Heading {level}")
    pf = p.paragraph_format
    pf.space_before, pf.space_after, pf.keep_with_next = Pt(9 if level == 2 else 6), Pt(3), True
    r = p.add_run(text)
    set_run(r, 13 if level == 2 else 11.5, bold=True, color="434343")
    return p


def cell_borders(cell, top=None, bottom=None):
    tcPr = cell._tc.get_or_add_tcPr()
    b = OxmlElement("w:tcBorders")
    for side, val in (("top", top), ("bottom", bottom)):
        if val:
            e = OxmlElement(f"w:{side}")
            e.set(qn("w:val"), "single"); e.set(qn("w:sz"), str(val)); e.set(qn("w:color"), "434343")
            b.append(e)
    tcPr.append(b)


def add_table(doc, rows, caption, widths=None, size=7.5):
    cap = para(doc, "", size=8.5, align="left", space_after=2, space_before=4, keep_next=True)
    add_inline(cap, caption, 8.5)
    t = doc.add_table(rows=len(rows), cols=len(rows[0]))
    t.autofit = False
    t.alignment = 1
    for i, r in enumerate(rows):
        for j, v in enumerate(r):
            c = t.cell(i, j)
            c.text = ""
            p = c.paragraphs[0]
            p.paragraph_format.space_after = Pt(0); p.paragraph_format.line_spacing = 1.0
            p.paragraph_format.keep_with_next = (i < len(rows) - 1)      # keep the table on one page
            trPr = c._tc.getparent().get_or_add_trPr()
            if trPr.find(qn("w:cantSplit")) is None:
                trPr.append(OxmlElement("w:cantSplit"))
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if j == 0 else WD_ALIGN_PARAGRAPH.CENTER
            add_inline(p, v, size, bold=(i == 0))
            if widths:
                c.width = Inches(widths[j])
            cell_borders(c, top=8 if i == 0 else None, bottom=(8 if i in (0, len(rows) - 1) else None))
    para(doc, "", size=4, space_after=2)
    return t


def add_figure(doc, path, width, caption):
    p = para(doc, "", align="center", space_after=1, space_before=3, keep_next=True)
    p.add_run().add_picture(str(Path(os.environ.get("FIGDIR", ROOT / "paper/figs")) / path), width=Inches(float(width)))
    cap = para(doc, "", size=8.5, align="justify", space_after=6, left=0.15)
    add_inline(cap, caption, 8.5)


def build(content_path: Path, out_docx: Path):
    d = docx.Document(str(ROOT / "template/template.docx"))
    body = d.element.body
    spec = {"AUTHORS": []}
    lines = fill(content_path.read_text()).split("\n")
    # ---- header fields
    i = 0
    title, abstract = "", []
    blocks = []
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("TITLE:"):
            title = ln[6:].strip()
        elif ln.startswith("AUTHOR:"):
            spec["AUTHORS"].append([x.strip() for x in ln[7:].split("|")])
        elif ln.startswith("ABSTRACT:"):
            i += 1
            while i < len(lines) and lines[i].strip():
                abstract.append(lines[i]); i += 1
        else:
            blocks.append(ln)
        i += 1
    # ---- title / authors / abstract inside the template table
    t0 = d.tables[0]
    tpar = t0.rows[0].cells[0].paragraphs[1]
    runs = [r for r in tpar.runs if r.text.strip()]
    runs[0].text = title
    for r in runs[1:]:
        if "TITLE" in r.text or "PROJECT" in r.text:
            r.text = ""
    for r in tpar.runs:
        if r.font.size:
            r.font.size = Pt(16)
    cell = t0.rows[1].cells[0]
    outer = cell._tc.findall(qn("w:tbl"))[0]
    # replace the (badly wrapping) authors grid by centered author paragraphs, keep "With Apart Research"
    inner_tc = outer.find(qn("w:tr")).find(qn("w:tc"))
    authors_tbl = inner_tc.find(qn("w:tbl"))
    with_p = [p for p in inner_tc.findall(qn("w:p")) if "Apart" in "".join(t.text or "" for t in p.iter(qn("w:t")))][0]
    inner_tc.remove(authors_tbl)
    for name, aff in spec["AUTHORS"]:
        for txt, bold in ((name, True), (aff, False)):
            np_ = OxmlElement("w:p")
            ppr = OxmlElement("w:pPr"); jc = OxmlElement("w:jc"); jc.set(qn("w:val"), "center"); ppr.append(jc)
            sp = OxmlElement("w:spacing"); sp.set(qn("w:after"), "0"); ppr.append(sp); np_.append(ppr)
            r = OxmlElement("w:r"); rpr = OxmlElement("w:rPr")
            rf = OxmlElement("w:rFonts")
            for a in ("w:ascii", "w:hAnsi", "w:cs"):
                rf.set(qn(a), FONT)
            rpr.append(rf)
            if bold:
                rpr.append(OxmlElement("w:b"))
            sz = OxmlElement("w:sz"); sz.set(qn("w:val"), "21" if bold else "19"); rpr.append(sz)
            r.append(rpr); tt = OxmlElement("w:t"); tt.text = txt; r.append(tt); np_.append(r)
            with_p.addprevious(np_)
    # abstract text
    abs_tbl = cell._tc.findall(qn("w:tbl"))[1]
    abs_tc = abs_tbl.find(qn("w:tr")).find(qn("w:tc"))
    for p_ in abs_tc.findall(qn("w:p"))[1:]:
        abs_tc.remove(p_)
    ap = docx.text.paragraph.Paragraph(abs_tc.find(qn("w:p")), cell)
    for r in list(ap.runs):
        r._r.getparent().remove(r._r)
    ap.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    ap.paragraph_format.line_spacing = 1.05
    add_inline(ap, " ".join(abstract), 9.5)
    # ---- strip the template body (info box + guidance) but keep the final sectPr
    kids = list(body.iterchildren())
    start = None
    for k, ch in enumerate(kids):
        if ch.tag == qn("w:p") and "1. Introduction" in "".join(t.text or "" for t in ch.iter(qn("w:t"))):
            start = k
            break
    info_tbl = d.tables[1]._tbl
    body.remove(info_tbl)
    for ch in kids[start:]:
        if ch.tag != qn("w:sectPr"):
            body.remove(ch)
    # ---- content blocks
    j = 0
    pending = []
    def flush():
        nonlocal pending
        if pending:
            text = " ".join(x.strip() for x in pending).strip()
            if text:
                para(d, text)
            pending = []
    n = len(blocks)
    while j < n:
        ln = blocks[j]
        s = ln.strip()
        if not s:
            flush()
        elif s.startswith("## "):
            flush(); heading(d, s[3:], 2)
        elif s.startswith("### "):
            flush(); heading(d, s[4:], 3)
        elif s.startswith("FIG:"):
            flush()
            f, w, cap = [x.strip() for x in s[4:].split("|", 2)]
            add_figure(d, f, w, cap)
        elif s.startswith("TABLE:"):
            flush()
            cap = s[6:].strip(); rows = []
            j += 1
            widths = None
            while j < n and blocks[j].strip().startswith("|"):
                row = [c.strip() for c in blocks[j].strip().strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in row):
                    rows.append(row)
                j += 1
            j -= 1
            add_table(d, rows, cap)
        elif s.startswith("- "):
            flush(); para(d, "•  " + s[2:], left=0.2, first=-0.15, space_after=2)
        elif re.match(r"^\d+\.\s", s) and not s.startswith("##"):
            flush(); para(d, s, left=0.2, first=-0.2, space_after=2)
        elif s.startswith("REF:"):
            flush(); para(d, s[4:].strip(), size=8.5, left=0.25, first=-0.25, space_after=1.5, align="left")
        elif s == "PAGEBREAK":
            flush(); d.add_page_break()
        else:
            pending.append(s)
        j += 1
    flush()
    d.save(str(out_docx))


def to_pdf(docx_path: Path):
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", str(docx_path.parent), str(docx_path)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    pdf = docx_path.with_suffix(".pdf")
    npages = int(re.search(r"Pages:\s+(\d+)", subprocess.run(["pdfinfo", str(pdf)], capture_output=True, text=True).stdout).group(1))
    main_end = None
    for pg in range(1, npages + 1):
        t = subprocess.run(["pdftotext", "-f", str(pg), "-l", str(pg), "-layout", str(pdf), "-"], capture_output=True, text=True).stdout
        if re.search(r"^\s*(References|Appendix)\s*$", t, re.M):
            main_end = pg
            break
    return pdf, npages, main_end


if __name__ == "__main__":
    src = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "paper/content.md"
    out = Path(sys.argv[2]) if len(sys.argv) > 2 else ROOT / "paper/report.docx"
    build(src, out)
    pdf, npages, main_end = to_pdf(out)
    print(f"{pdf}  pages={npages}  first page with References/Appendix heading={main_end} (main text must END on or before page 8; "
          f"the page holding the heading may also hold main text)")
