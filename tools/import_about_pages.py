#!/usr/bin/env python3
"""The four About-menu text pages (261009): The Pedagogy, The Pedagogy of the Red Nose Clown, The Roots, Helikos School.

Stand-alone (never run import_demo.py / import_workshops.py: they overwrite hand-edited pages). Run from the project folder:  python3 tools/import_about_pages.py
Words are the client's, unchanged. Only changes: the page's own first line when it just repeats the title (THE PEDAGOGY, THE ROOTS) is dropped because the page title says it,
every heading becomes a level-2 heading (the old pages jump to h3 and h4 under the title), internal links are rewritten, and the images/PDFs used are copied."""
import csv, json, re, shutil, subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT.parent.parent / "WORDPRESS" / "site-archive"
CONTENT = ROOT / "src" / "content" / "pages"
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

PAGES = {"the-pedagogy": "The Pedagogy", "pedagogy-of-the-red-nose-clown": "The Pedagogy of the Red Nose Clown", "the-roots": "The Roots", "helikos-school": "Helikos School"}
used = set()
for slug, title in PAGES.items():
    body = subprocess.run([str(NODE), str(ROOT / "tools" / "html_to_md.mjs"), slug], capture_output=True, text=True, check=True).stdout.strip("\n")
    lines = body.split("\n")
    if lines and lines[0].strip().lower() == title.lower():
        body = "\n".join(lines[1:]).lstrip("\n")
    body = re.sub(r"^#{2,6} ", "## ", body, flags=re.M)
    body = rewrite(body)
    used |= set(re.findall(r"/wp-content/uploads/([^\s)\"']+)", body))
    (CONTENT / f"{slug}.md").write_text("---\n" + f"title: {json.dumps(title)}\n" + "---\n\n" + body + "\n", encoding="utf-8")

missing = []
for ref in sorted(used):
    src = ARCHIVE / "media" / ref
    if src.exists():
        (UPLOADS / ref).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, UPLOADS / ref)
    else:
        missing.append(ref)
print(len(PAGES), "pages;", len(used) - len(missing), "media files;", "missing:", missing or "none")
