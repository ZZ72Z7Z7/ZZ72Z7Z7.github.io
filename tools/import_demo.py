#!/usr/bin/env python3
"""
Demo import: copies a first sample of real content from the site archive into
src/content/, rewrites links and image paths, and copies the media the content uses.

Run from the project folder:  python3 tools/import_demo.py
The archive location is read from ARCHIVE below (never committed to the site repo).
"""
import csv, json, os, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCHIVE = ROOT.parent.parent / "WORDPRESS" / "site-archive"
MAP = ROOT / "migration-map.csv"
CONTENT = ROOT / "src" / "content"
UPLOADS = ROOT / "public" / "wp-content" / "uploads"

# ---------------------------------------------------------------- helpers

url_map = {}
for row in csv.DictReader(open(MAP, encoding="utf-8-sig")):
    if row["new_url"]:
        url_map[row["old_url"]] = row["new_url"]

titles = {}
for row in csv.DictReader(open(ARCHIVE / "pages.csv", encoding="utf-8-sig")):
    path = re.sub(r"^https?://[^/]+", "", row["url"])
    titles[path] = row["title"].replace(" ", " ")


def read(slug):
    """Return (meta, body) for an archived page. Meta (dates) comes from the archive's text
    file; the body is converted from the original HTML (tools/html_to_md.mjs), which keeps
    emphasis, line breaks and verse layout exactly."""
    import subprocess
    raw = (ARCHIVE / "text" / f"{slug}.md").read_text(encoding="utf-8")
    head, _, _text_body = raw.partition("\n---\n")
    meta = {"Title": head.splitlines()[0].lstrip("# ").strip()}
    for line in head.splitlines():
        m = re.match(r"(Source|Section|Published|Last modified): (.*)", line)
        if m:
            meta[m.group(1)] = m.group(2).strip()
    node = ROOT.parent / ".tools" / "node" / "bin" / "node"
    body = subprocess.run([str(node), str(ROOT / "tools" / "html_to_md.mjs"), slug],
                          capture_output=True, text=True, check=True).stdout
    lines = body.split("\n")
    if lines and lines[0].strip().lower() == meta["Title"].lower():   # page title repeated inside the content
        lines = lines[1:]
    return meta, "\n".join(lines).strip("\n")


HOST = r"https?://(?:www\.)?(?:giovannifusetti\.com|helikos737982018\.wordpress\.com)"


def rewrite(text):
    text = text.replace("../media/", "/wp-content/uploads/")

    def link(m):
        path = m.group(1) or "/"
        path = path.split("#")[0]
        if path.startswith("/category/") or path.startswith("/author/"):
            return "/blog/"
        if not path.endswith("/") and "." not in path.rsplit("/", 1)[-1]:
            path += "/"
        return url_map.get(path, path)

    return re.sub(HOST + r"(/[^\s)\]\"']*)?", link, text)


def fm(**fields):
    lines = ["---"]
    for k, v in fields.items():
        if v is None:
            continue
        lines.append(f"{k}: {json.dumps(v, ensure_ascii=False)}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def write(rel, front, body=""):
    p = CONTENT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(front + ("\n" + body.strip("\n") + "\n" if body else ""), encoding="utf-8")


# ---------------------------------------------------------------- pages

# Home = splash page + Welcome page, combined (migration map rows 1-2).
# The splash text is rebuilt from the original HTML (html/index.html): the exported Markdown
# lost its structure here (nested italics, line breaks). Words and line breaks are unchanged.
splash = """<div class="splash">

<p class="splash-lead"><em><strong>I practice the freedom to be</strong></em></p>

<p class="splash-word"><em><strong>stupidus</strong></em></p>

<p><strong><em>Stupefied by life, nature, beauty </em><br><em>and the mystery of the human condition </em></strong></p>

<p><strong><em>I celebrate the sublime stupidity of Clowns</em><br><em>I long for the crazy wisdom of The Fool</em></strong></p>

<p><strong><em>Intelligence is limited</em><br><em>Stupidity is infinite </em></strong></p>

<p><strong><em>Clowning is a very serious work</em> <em>on how to be stupid</em></strong></p>

<p><em><strong>To the delusional quest for a mechanical artificial intelligence <br>I will respond with the daily practice of  embodied natural stupidity</strong></em></p>

</div>"""
_, welcome = read("home-2")
welcome = welcome.split("-----\n\nFor the ITALIAN site")[0]                      # toggle replaces the flag
welcome = re.sub(r"\n## \n", "\n", welcome)
site_map = """
**ABOUT GIOVANNI FUSETTI**: [What has happened till now](https://giovannifusetti.com/giovanni-fusetti/)

**[THE PEDAGOGY](https://giovannifusetti.com/the-pedagogy/)**: The Journey of Initiation of the Actor Creator

Explore the Calendar of the **[UPCOMING WORKSHOPS](https://giovannifusetti.com/workshops/)** & **[PAST WORKSHOPS](https://giovannifusetti.com/past-workshops/)**

**[UPCOMING EVENTS](https://giovannifusetti.com/upcoming-events/)**

**CREATIONS**: [WRITINGS](https://giovannifusetti.com/writings/) · [THEATRICAL LECTURES](https://giovannifusetti.com/lectures/) · [SHOWS](https://giovannifusetti.com/performances/) · [PHOTO GALLERIES](https://giovannifusetti.com/photo-galleries/) · [VIDEOS](https://giovannifusetti.com/videos/)

**MEDIA**: **[BLOG](https://giovannifusetti.com/blog/)**

**[CONTACT](https://giovannifusetti.com/contact/)** · **[JOIN GIOVANNI FUSETTI’S & HELIKOS MAILING LIST](https://giovannifusetti.com/contact/)**

Winter sky over the Cansiglio Forest, Italy
"""
home_body = splash + "\n\n" + welcome.strip() + "\n\n-----\n" + site_map
write("pages/home.md", fm(title="Home", description=None), rewrite(home_body))

# About = the Bio page (URL unchanged).
meta, body = read("giovanni-fusetti")
write("pages/giovanni-fusetti.md", fm(title="Giovanni Fusetti"), rewrite(body))

# Creations landing page.
meta, body = read("creations")
write("pages/creations.md", fm(title="Creations"), rewrite(body))

# ---------------------------------------------------------------- blog

blog_listing = (ARCHIVE / "text" / "blog.md").read_text(encoding="utf-8")
categories = {}
for m in re.finditer(r"\[(\w+)\]\(https://giovannifusetti\.com/category/\w+/\)\n\n## \[.*?\]\((https://giovannifusetti\.com[^)]+)\)", blog_listing):
    categories[re.sub(r"^https?://[^/]+", "", m.group(2))] = m.group(1)
CAT_FIX = {"Phisiosophy": "Philosophy"}     # spelling in the old category name; brief lists "Philosophy"

for f in sorted((ARCHIVE / "text").glob("20??__*__*__*.md")):
    slug = f.stem
    y, mo, d, name = slug.split("__", 3)
    path = f"/{y}/{mo}/{d}/{name}/"
    meta, body = read(slug)
    cat = CAT_FIX.get(categories[path], categories[path])
    write(
        f"blog/{y}-{mo}-{d}-{name}.md",
        fm(title=titles[path], date=f"{y}-{mo}-{d}", category=cat),
        rewrite(body),
    )

# ---------------------------------------------------------------- media

used = set()
for md in CONTENT.rglob("*.md"):
    for ref in re.findall(r"/wp-content/uploads/([^\s)\"']+)", md.read_text(encoding="utf-8")):
        used.add(ref)
for yml in CONTENT.rglob("*.yml"):
    for ref in re.findall(r"/wp-content/uploads/([^\s)\"']+)", yml.read_text(encoding="utf-8")):
        used.add(ref)

missing = []
for ref in sorted(used):
    src = ARCHIVE / "media" / ref
    dst = UPLOADS / ref
    if src.exists():
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    else:
        missing.append(ref)

print(f"content written; {len(used) - len(missing)} media files copied")
if missing:
    print("MISSING in archive:", *missing, sep="\n  ")
