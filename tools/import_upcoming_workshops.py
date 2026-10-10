#!/usr/bin/env python3
"""Workshop pages for the workshops that have upcoming dates (261008): The Language of Gestures,
Famiglia dell'Arte, Bouffon Intensive, Bring Your Own Psyche.

Stand-alone on purpose: tools/import_demo.py rewrites home.md, About and the blog when imported,
which would overwrite later hand edits. Run from the project folder:  python3 tools/import_upcoming_workshops.py
Base text = the most recently modified edition page (brief, section 5). Per-edition details at the top
(dates, place, "with ...") live in the schedule entries; everything else is the client's text, unchanged."""
import csv, json, re, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT.parent.parent / "WORDPRESS" / "site-archive"
CONTENT = ROOT / "src" / "content"
UPLOADS = ROOT / "public" / "wp-content" / "uploads"
NODE = ROOT.parent / ".tools" / "node" / "bin" / "node"

url_map = {r["old_url"]: r["new_url"] for r in csv.DictReader(open(ROOT / "migration-map.csv", encoding="utf-8-sig")) if r["new_url"]}
HOST = r"https?://(?:www\.)?(?:giovannifusetti\.com|helikos737982018\.wordpress\.com)"

def rewrite(text):
    def link(m):
        path = (m.group(1) or "/").split("#")[0]
        if path.startswith(("/category/", "/author/")):
            return "/blog/"
        if not path.endswith("/") and "." not in path.rsplit("/", 1)[-1]:
            path += "/"
        return url_map.get(path, path)
    return re.sub(HOST + r"(/[^\s)\]\"']*)?", link, text.replace("../media/", "/wp-content/uploads/"))

def body_of(slug):
    out = subprocess.run([str(NODE), str(ROOT / "tools" / "html_to_md.mjs"), slug], capture_output=True, text=True, check=True).stdout
    return out.strip("\n")

def from_first_image(text, keep_before=""):
    i = text.index("![](")
    return (keep_before + text[i:]).strip("\n")

def fm(**f):
    return "---\n" + "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in f.items() if v) + "\n---\n"

PAGES = {
    "language-of-gestures": dict(slug="the-language-of-gestures-padova", title="The Language of Gestures"),
    "famiglia-dell-arte": dict(slug="famiglia-dell-arte-melbourne", title="Famiglia dell’Arte",
        subtitle="EXPLORING FAMILY STORIES, ROLES, DYNAMICS, PATTERNS AND SCRIPTS\nthrough Psychodrama and Physical Theatre"),
    "bouffon-intensive": dict(slug="bouffon-intensive-2027", title="Bouffon Intensive",
        keep_before="**Helikos Downunder Summer School 2027**\n\n"),
    "bring-your-own-psyche": dict(slug="bring-your-own-psyche-melbourne", title="Bring Your Own Psyche",
        subtitle="An advanced Psychodrama and Physical Theatre workshop\n“a la carte”"),
}
for name, p in PAGES.items():
    body = rewrite(from_first_image(body_of(p["slug"]), p.get("keep_before", "")))
    (CONTENT / "workshops" / f"{name}.md").write_text(fm(title=p["title"], subtitle=p.get("subtitle")) + "\n" + body + "\n", encoding="utf-8")

# media the new pages use
used = set()
for name in PAGES:
    used |= set(re.findall(r"/wp-content/uploads/([^\s)\"']+)", (CONTENT / "workshops" / f"{name}.md").read_text(encoding="utf-8")))
missing = []
for ref in sorted(used):
    src = ARCHIVE / "media" / ref
    if src.exists():
        (UPLOADS / ref).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, UPLOADS / ref)
    else:
        missing.append(ref)
print(len(PAGES), "pages;", len(used) - len(missing), "media files;", "missing:", missing or "none")

# link the schedule entries to their pages (the title then comes from the page)
SCHED = CONTENT / "schedule"
link = {"The Language of Gestures": "language-of-gestures", "Famiglia dell’Arte": "famiglia-dell-arte",
        "Bouffon Intensive": "bouffon-intensive", "Bring Your Own Psyche": "bring-your-own-psyche"}
for f in sorted(SCHED.glob("*.yml")):
    t = f.read_text(encoding="utf-8")
    m = re.match(r'title: "([^"]+)"\n', t)
    if m and m.group(1) in link:
        f.write_text(f'workshop: "{link[m.group(1)]}"\n' + t[m.end():], encoding="utf-8")
        print("linked", f.name)
