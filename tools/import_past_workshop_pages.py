#!/usr/bin/env python3
"""Individual workshop pages for the workshops that have no upcoming date (261009): 20 pages. Stand-alone (never run import_demo.py / import_workshops.py).
Run from the project folder:  python3 tools/import_past_workshop_pages.py
Per workshop: the base text is the most recently modified edition page (brief, section 5). The page's header (dates, place, title, tagline: they belong to the edition,
and are in the schedule) is dropped; the first picture becomes the primary picture, the other pictures the gallery (with their captions), photo credits go under it,
and everything else is the client's text, unchanged (the old page's own SCHEDULE / LOCATION / TUITION blocks stay in the text as they were written).
The tagline is taken from the newest schedule entry that has one. The three held workshops (Pedagogy of Bouffons, Chorus in the City) are not built."""
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
    return subprocess.run([str(NODE), str(ROOT / "tools" / "html_to_md.mjs"), slug], capture_output=True, text=True, check=True).stdout.strip("\n")

# slug -> (base edition page, title, the titles this workshop has on the Workshops list)
PAGES = {
    "20-movements-of-jacques-lecoq": ("the-20-movements-of-jacques-lecoq-la", "The 20 Movements of Jacques Lecoq", ["the 20 movements of jacques lecoq"]),
    "australia-dell-arte": ("australia-dellarte", "Australia dell’Arte", ["australia dell’arte"]),
    "clowns-life": ("clowns-life", "Clown’s Life", ["clown’s life"]),
    "conversations-with-the-fool": ("the-fools-seminars-2026", "Conversations with the Fool", ["conversations with the fools", "conversations with the fool"]),
    "from-the-neutral-mask-to-the-red-nose": ("from-the-neutral-mask-to-the-red-nose-boulder", "From the Neutral Mask to the Red Nose", ["from the neutral mask to the red nose"]),
    "greenhouse-of-bouffons": ("the-greenhouse-of-bouffons-boulder", "The Greenhouse of Bouffons", ["the greenhouse of bouffons"]),
    "greenhouse-of-fools": ("the-greenhouse-of-fools-4", "The Greenhouse of Fools", ["the greenhouse of fools"]),
    "journey-of-the-neutral-mask-in-nature": ("the-journey-of-the-neutral-mask-in-nature-melbourne", "The Journey of the Neutral Mask in Nature", ["the journey of the neutral mask in nature"]),
    "partnerships-in-play": ("partnerships-in-play-boulder-2024", "Partnerships in Play", ["partnerships in play"]),
    "pedagogic-journey": ("pedagogic-journey-2025", "The Pedagogic Journey", ["the pedagogic journey"]),
    "pedagogic-supervision-group": ("supervision", "Pedagogic Supervision Group", ["pedagogic supervision group"]),
    "personality-dell-arte": ("personality-dell-arte-melbourne", "Personality dell’Arte", ["personality dell’arte"]),
    "politics-of-the-fool": ("the-politics-of-the-fool-melbourne", "The Politics of the Fool", ["the politics of the fool"]),
    "post-pandemic-clowns": ("post-pandemic-clowns", "Post-Pandemic Clowns", ["post-pandemic clowns"]),
    "psychopathology-dell-arte": ("psychopathology-dell-arte-melbourne", "Psychopathology dell’Arte", ["psychopathology dell’arte"]),
    "spirit-of-commedia-dell-arte": ("the-spirit-of-commedia-dellarte-philadelphia", "The Spirit of Commedia dell’Arte", ["the spirit of commedia dell’arte"]),
    "storyteller": ("the-storyteller-melbourne", "The Storyteller", ["the storyteller"]),
    "sublime-stupidity": ("the-sublime-stupidity-2-melbourne", "The Sublime Stupidity", ["the sublime stupidity"]),
    "tao-of-clown": ("the-tao-of-clown-wellington-2026", "The Tao of Clown", ["the tao of clown"]),
    "teaching-red-nose-clown": ("teaching-red-nose-clown-boulder", "Teaching Red Nose Clown", ["teaching red nose clown"]),
}
IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")
LINKED_TITLES = {t: slug for slug, (_, _, ts) in PAGES.items() for t in ts}

def newest_tagline(titles):
    best = None
    for f in (CONTENT / "schedule").glob("*.yml"):
        t = f.read_text(encoding="utf-8")
        m = re.search(r'^title: "([^"]+)"', t, re.M)
        d = re.search(r'^description: "(.*)"$', t, re.M)
        s = re.search(r"^start: (\S+)", t, re.M)
        if m and d and m.group(1).lower() in titles:
            if not best or s.group(1) > best[0]:
                best = (s.group(1), json.loads('"' + d.group(1) + '"'))
    return best[1] if best else None

def norm(s):
    return re.sub(r"[^a-z0-9]", "", s.lower())

def yaml_block(key, text):
    return f"{key}: |\n" + "\n".join(("  " + l) if l.strip() else "" for l in text.strip("\n").split("\n")) + "\n"

report = []
used = set()
for slug, (base, title, titles) in PAGES.items():
    body = rewrite(body_of(base))
    i = body.index("![](")
    body = body[i:]
    blocks = [b.strip("\n") for b in re.split(r"\n\s*\n", body.strip()) if b.strip()]
    merged = []
    for b in blocks:
        if b.strip() == "<br>" and merged:
            merged[-1] += "\n<br>"
        else:
            merged.append(b)
    blocks = merged
    images, desc, credits = [], [], []
    in_credits = False
    k = 0
    while k < len(blocks):
        b = blocks[k]
        if IMG.search(b) and not re.sub(r"\s*\.?\s*", "", IMG.sub("", b)):
            srcs = IMG.findall(b)
            cap = None
            if k + 1 < len(blocks):
                nb = blocks[k + 1]
                one = "\n" not in nb.strip("\n").replace("  \n", " ").replace("\n<br>", "")
                if one and len(nb) <= 160 and not nb.startswith(("-", "–", "#", "!", "**")) and not IMG.search(nb) or re.fullmatch(r"\(\d+\)", nb.strip()):
                    cap = nb.strip()
                    k += 1
            for s in srcs:
                images.append([s, cap if s == srcs[-1] else None])
            k += 1
            continue
        if re.match(r"^\*{2,3}\s*PHOTO CREDITS", b):
            in_credits = True
        (credits if in_credits else desc).append(b)
        k += 1
    desc = [d for d in desc if not re.fullmatch(r"\(\d+\)", d.strip())]
    subtitle = newest_tagline(titles)
    if subtitle and desc and norm(re.sub(r"[*_#]", "", desc[0])) == norm(subtitle):
        desc.pop(0)
    primary, gallery = images[0], images[1:]
    cap0 = primary[1] if primary[1] and not re.fullmatch(r"\(\d+\)", primary[1]) else None
    fm = ["---", f"title: {json.dumps(title, ensure_ascii=False)}"]
    if subtitle:
        fm.append(f"subtitle: {json.dumps(subtitle, ensure_ascii=False)}")
    fm.append(f"image: {json.dumps(primary[0])}")
    if cap0:
        fm.append(f"image_caption: {json.dumps(cap0, ensure_ascii=False)}")
    real = [(s, c) for s, c in gallery if c is None or not re.fullmatch(r"\(\d+\)", c)]
    if real:
        fm.append("gallery:")
        for s, c in real:
            fm.append(f"  - src: {json.dumps(s)}")
            if c:
                fm.append(f"    caption: {json.dumps(c, ensure_ascii=False)}")
    if credits:
        fm.append(yaml_block("credits", "\n\n".join(credits)).rstrip("\n"))
    fm.append("---")
    text = "\n".join(fm) + "\n\n" + "\n\n".join(desc).strip() + "\n"
    (CONTENT / "workshops" / f"{slug}.md").write_text(text, encoding="utf-8")
    used |= set(re.findall(r"/wp-content/uploads/([^\s)\"']+)", text))
    flags = [w for w in ("TUITION", "SCHEDULE", "LOCATION", "ENROLL", "APPLY", "DEPOSIT", "EARLY BIRD") if re.search(w, text)]
    report.append((slug, len(" ".join(desc).split()), len(real), bool(subtitle), flags))

missing = []
for ref in sorted(used):
    src = ARCHIVE / "media" / ref
    if src.exists():
        (UPLOADS / ref).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, UPLOADS / ref)
    else:
        missing.append(ref)
for r in report:
    print(f"{r[0]:42} {r[1]:5} words  gallery {r[2]:2}  tagline {'yes' if r[3] else 'NO ':3}  old edition details: {', '.join(r[4]) or '-'}")
print(len(PAGES), "pages;", len(used) - len(missing), "media files; missing:", missing or "none")
