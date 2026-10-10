#!/usr/bin/env python3
"""Writings, Lectures and Shows pages (261009), from the archive's original HTML.

Stand-alone on purpose (never run import_demo.py / import_workshops.py: they overwrite hand-edited pages). Run from the project folder:
    python3 tools/import_creations.py
The text is the client's, unchanged, except that the Shows page's own first heading "SHOWS" (a bold line and a rule) is left out because
the page title already says Shows. Images and PDFs the pages use are copied to public/wp-content/uploads at their original addresses."""
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

def body_of(slug):
    return subprocess.run([str(NODE), str(ROOT / "tools" / "html_to_md.mjs"), slug], capture_output=True, text=True, check=True).stdout.strip("\n")

PAGES = {"writings": ("writings", "Writings"), "lectures": ("lectures", "Lectures"), "shows": ("performances", "Shows")}
used = set()
for name, (slug, title) in PAGES.items():
    body = body_of(slug)
    if name == "shows":
        body = re.sub(r"^\*\*SHOWS\*\*\s*\n+---\s*\n+", "", body)
    body = rewrite(body)
    used |= set(re.findall(r"/wp-content/uploads/([^\s)\"']+)", body))
    (CONTENT / f"{name}.md").write_text("---\n" + f"title: {json.dumps(title)}\n" + "---\n\n" + body + "\n", encoding="utf-8")

missing = []
for ref in sorted(used):
    src = ARCHIVE / "media" / ref
    if src.exists():
        (UPLOADS / ref).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, UPLOADS / ref)
    else:
        missing.append(ref)
print(len(PAGES), "pages;", len(used) - len(missing), "media files;", "missing:", missing or "none")
