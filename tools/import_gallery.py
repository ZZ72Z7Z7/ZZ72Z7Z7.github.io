#!/usr/bin/env python3
"""Photo galleries and the video page (261009): Photo Galleries (the landing page with four tiles), the four gallery pages
(Pedagogic Journey, Bouffons Gallery, Melbourne Red Nose Intensive, Boulder Programs) and Video Gallery.

Stand-alone on purpose (never run import_demo.py / import_workshops.py: they overwrite hand-edited pages). Run from the project folder:
    python3 tools/import_gallery.py
The text is the client's, unchanged. The photos on the gallery pages are put in a grid (`<div class="gallery-grid">`); they have no
descriptions in the archive, so their alt text is empty. The WordPress "Discover more from ... Subscribe" block at the end of the old
pages is left out. On the landing page, the old link behind the Bouffons tile pointed to a page that never existed
(/portfolio/photo-gallery/); it now points to the Bouffons Gallery page."""
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
    text = text.replace("/portfolio/photo-gallery/", "/portfolio/bouffons-gallery/")
    def link(m):
        path = (m.group(1) or "/").split("#")[0]
        if path.startswith(("/category/", "/author/")):
            return "/blog/"
        if not path.endswith("/") and "." not in path.rsplit("/", 1)[-1]:
            path += "/"
        return url_map.get(path, path)
    return re.sub(HOST + r"(/[^\s)\]\"']*)?", link, text.replace("../media/", "/wp-content/uploads/"))

def body_of(slug):
    b = subprocess.run([str(NODE), str(ROOT / "tools" / "html_to_md.mjs"), slug], capture_output=True, text=True, check=True).stdout.strip("\n")
    return re.split(r"\n+---\n+### Discover more from", b)[0].strip("\n")

def grid(body):
    """Consecutive bare images become one grid."""
    out, run = [], []
    def flush():
        if run:
            out.append('<div class="gallery-grid">\n' + "\n".join(f'<img src="{u}" alt="" loading="lazy">' for u in run) + "\n</div>")
            run.clear()
    for block in re.split(r"\n\n+", body):
        m = re.fullmatch(r"!\[\]\(([^)\s]+)\)", block.strip())
        if m:
            run.append(m.group(1))
        else:
            flush(); out.append(block)
    flush()
    return "\n\n".join(out)

PAGES = [
    ("photo-galleries.md", "photo-galleries", "Photo Galleries", False),
    ("galleries/the-pedagogic-journey.md", "portfolio__the-pedagogic-journey", "The Pedagogic Journey", True),
    ("galleries/bouffons-gallery.md", "portfolio__bouffons-gallery", "Bouffons Gallery", True),
    ("galleries/melbourne-red-nose-intensive.md", "portfolio__melbourne-red-nose-intensive", "Melbourne Red Nose Intensive", True),
    ("galleries/boulder-programs-2004-2018.md", "portfolio__boulder-programs-2004-2018", "Boulder Programs 2004-2018", True),
    ("videos.md", "videos", "Video Gallery", False),
]
(CONTENT / "galleries").mkdir(exist_ok=True)
used = set()
for fname, slug, title, as_grid in PAGES:
    body = rewrite(body_of(slug))
    if as_grid:
        body = grid(body)
    used |= set(re.findall(r"/wp-content/uploads/([^\s)\"']+)", body))
    (CONTENT / fname).write_text("---\n" + f"title: {json.dumps(title)}\n" + "---\n\n" + body + "\n", encoding="utf-8")

missing = []
for ref in sorted(used):
    src = ARCHIVE / "media" / ref
    if src.exists():
        (UPLOADS / ref).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, UPLOADS / ref)
    else:
        missing.append(ref)
print(len(PAGES), "pages;", len(used) - len(missing), "media files;", "missing:", missing or "none")
