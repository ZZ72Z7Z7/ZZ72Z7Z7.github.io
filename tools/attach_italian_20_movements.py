#!/usr/bin/env python3
"""Attaches the Italian text of "I 20 Movimenti di Jacques Lecoq" (the old Italian page) to the 20 Movements workshop page as body_it and title_it (261009).
Italian part only (the old page also repeats the text in English): the description up to NOTE PRATICHE, then AMMISSIONE (who it is for), LUOGO and ORARIO
(reinstated with SCHEDULE and LOCATION at the designer's word); QUOTA, application, LINGUA and the Covid message are left out like on the English page.
Its six pictures were loaded from helikos.com; they are kept (self-hosted by tools/clean_workshop_leftovers.py).
Run after tools/cut_old_edition_details.py, then tools/clean_workshop_leftovers.py:  python3 tools/attach_italian_20_movements.py"""
import re, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NODE = ROOT.parent / ".tools" / "node" / "bin" / "node"
t = subprocess.run([str(NODE), str(ROOT / "tools" / "html_to_md.mjs"), "i-20-movimenti-di-jacques-lecoq"], capture_output=True, text=True, check=True).stdout
head = t[:t.index("NOTE PRATICHE")]
body = head[head.index("!["):]
body = re.sub(r"\n##\s*\n<br>\s*$", "", body.rstrip())
# the pictures the old page loaded from helikos.com are in the archive (media/_other) and are served from /images/helikos/ by tools/clean_workshop_leftovers.py (run it after this script)
body = re.sub(r"\n{3,}", "\n\n", body).strip()
amm = t[t.index("AMMISSIONE"):]
first = re.search(r"Questo seminario si indirizza[^\n]*", amm).group(0).strip()
luogo = re.search(r"\*\*LUOGO\*\*.*?(?=\n\nUna volta completata)", t, re.S).group(0).strip()
orario = re.search(r"\*\*ORARIO\*\*.*?(?=\n\nPer ulteriori informazioni)", t, re.S).group(0).strip()
body += "\n\n**AMMISSIONE**  \n" + first + "\n\n" + luogo + "\n\n" + orario + "\n"
f = ROOT / "src" / "content" / "workshops" / "20-movements-of-jacques-lecoq.md"
s = f.read_text(encoding="utf-8")
s = re.sub(r"^body_it: \|\n(?:  .*\n|\n)*", "", s, flags=re.M)
s = re.sub(r"^title_it: .*\n", "", s, flags=re.M)
m = re.match(r"(---\n)(title: [^\n]*\n)(.*?)\n---\n", s, re.S)
blk = "body_it: |\n" + "\n".join(("  " + l) if l.strip() else "" for l in body.split("\n")) + "\n"
f.write_text(m.group(1) + m.group(2) + 'title_it: "I 20 Movimenti di Jacques Lecoq"\n' + m.group(3) + "\n" + blk + "---\n" + s[m.end():], encoding="utf-8")
print("attached", len(body.split()), "words")
