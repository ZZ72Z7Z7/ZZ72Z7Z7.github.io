#!/usr/bin/env python3
"""Puts the five existing workshop pages into the standard format (designer, 261009) and moves each page's per-edition practical text
into the schedule entry of its next upcoming edition.

Standard page: title, tagline (subtitle), dates and location (from the schedule), primary image (same as the Workshops-list thumbnail),
course description (first paragraph, then "Read more"), Schedule / Location / Tuition / Applications (per edition, in the schedule entry),
image gallery (every other image, with its caption) and photo credits.

Run once from the project folder:  python3 tools/standardize_workshops.py     (the originals are kept in the scratchpad copy of this session)
The client's words are moved, not changed: only the section labels that became headings (SCHEDULE, LOCATION, TUITION, ...) are dropped."""
import re, json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WS = ROOT / "src" / "content" / "workshops"
SCHED = ROOT / "src" / "content" / "schedule"

# the next upcoming edition of each workshop (the page text was written for it) and the tagline where the page has none
TARGET = {
    "language-of-gestures": "2026-10-19-the-language-of-gestures.yml",
    "red-nose-intensive": "2026-11-01-red-nose-intensive.yml",
    "famiglia-dell-arte": "2027-01-18-famiglia-dell-arte.yml",
    "bouffon-intensive": "2027-02-08-bouffon-intensive.yml",
    "bring-your-own-psyche": "2027-03-15-bring-your-own-psyche.yml",
}
BUCKET_OF = [  # label -> (bucket, dropped as a heading?)
    (r"^SCHEDULE$", "schedule", True),
    (r"^LANGUAGE$", "schedule", False),
    (r"^LOCATION\b", "location", True),
    (r"^(TUITION|EARLY BIRD|FULL PRICE|DEPOSIT)", "tuition", None),
    (r"^ENROLL?MENT$", "applications", True),
    (r"^(HOW TO APPLY|APPLICATIONS|APPLICATION PROCESS)$", "applications", True),
    (r"^(INFORMATION AND APPLICATIONS|VISA)$", "applications", False),
    (r"^PRACTICALITIES$", None, True),
]
LABEL = re.compile(r"^(?:#+\s*)?\*\*\s*([A-Z0-9][A-Z0-9 ’'&/,.:?!…–-]{2,70}?)\s*\*\*\s*(.*)$", re.S)

def classify(label):
    for pat, bucket, drop in BUCKET_OF:
        if re.search(pat, label):
            return bucket, drop
    return "description", False

def split_front(text):
    m = re.match(r"---\n(.*?)\n---\n(.*)", text, re.S)
    return m.group(1), m.group(2)

def get_yaml_str(front, key):
    m = re.search(rf'^{key}: "(.*)"$', front, re.M)
    return json.loads('"' + m.group(1) + '"') if m else None

def yaml_block(key, text):
    return f"{key}: |\n" + "\n".join(("  " + l) if l.strip() else "" for l in text.strip("\n").split("\n")) + "\n"

IMG = re.compile(r"!\[[^\]]*\]\(([^)\s]+)\)")

for slug, sched_file in TARGET.items():
    front, body = split_front((WS / f"{slug}.md").read_text(encoding="utf-8"))
    title = get_yaml_str(front, "title")
    subtitle = get_yaml_str(front, "subtitle")
    sched = (SCHED / sched_file).read_text(encoding="utf-8")
    primary = re.search(r'^image: "(.*)"$', sched, re.M).group(1)

    blocks = [b.strip("\n") for b in re.split(r"\n\s*\n", body.strip()) if b.strip()]
    # glue "<br>" separators back to the paragraph before them
    merged = []
    for b in blocks:
        if b.strip() == "<br>" and merged:
            merged[-1] += "\n<br>"
        else:
            merged.append(b)
    blocks = merged

    buckets = {"description": [], "schedule": [], "location": [], "tuition": [], "applications": []}
    images = []          # [src, caption]
    credits = []
    bucket = "description"
    in_credits = False
    i = 0
    while i < len(blocks):
        b = blocks[i]
        # images (one block can hold several images joined by " . ")
        if IMG.search(b) and not re.sub(r"\s*\.?\s*", "", IMG.sub("", b)):
            srcs = IMG.findall(b)
            cap = None
            if i + 1 < len(blocks):
                nb = blocks[i + 1]
                one = "\n" not in nb.strip("\n").replace("  \n", " ").replace("\n<br>", "")
                if (re.fullmatch(r"\(\d+\)", nb.strip()) or (one and len(nb) <= 160 and not LABEL.match(nb) and not nb.startswith(("-", "–", "#", "!", "**")) and not IMG.search(nb))) and nb != "<br>":
                    cap = nb.strip()
                    i += 1
            for s in srcs:
                images.append([s, cap if s == srcs[-1] else None])  # a caption under a row of pictures goes with the last one
            i += 1
            continue
        if re.match(r"^\*{2,3}\s*PHOTO CREDITS", b):
            in_credits = True
        if in_credits:
            credits.append(b)
            i += 1
            continue
        m = LABEL.match(b.replace("\n", " ", 1) if False else b)
        # a label is a whole bold upper-case line; the rest of its block (if any) is text of the same section
        first, _, rest = b.partition("\n")
        m = LABEL.match(first)
        if m and not re.search(r"[a-z]{3}", m.group(1)):
            label = m.group(1).strip()
            tail = (m.group(2) or "").strip()
            bucket_new, drop = classify(label)
            if bucket_new is None:        # PRACTICALITIES: a divider only
                i += 1
                continue
            bucket = bucket_new
            keep_label = (drop is False) or (drop is None and not (re.match(r"^TUITION$", label)))
            out = []
            if keep_label:
                out.append(f"**{label}**" + ("  " if (tail or rest.strip()) else ""))  # two spaces: a line break, as on the old page
            if tail:
                out.append(tail)
            if rest.strip():
                out.append(rest)
            if out:
                buckets[bucket].append("\n".join(out))
            i += 1
            continue
        buckets[bucket].append(b)
        i += 1

    # the tagline: bold line at the top of the description when the page has no subtitle
    desc = [d for d in buckets["description"] if not re.fullmatch(r"\(\d+\)", d.strip())]
    if slug == "language-of-gestures":
        # "*HELIKOS school, 2013*" was the caption of the first picture (now handled as a caption); the tagline is the next line
        pass
    host_line = None
    if slug == "bouffon-intensive" and desc and desc[0].strip().startswith("**Helikos Downunder"):
        host_line = desc.pop(0)
    if not subtitle:
        if slug == "language-of-gestures":
            for k, d in enumerate(desc):
                if d.strip().startswith("**From Pantomime"):
                    subtitle = "From Pantomime to Bandes Mimées"
                    desc.pop(k)
                    break
        elif slug == "bouffon-intensive":
            subtitle = "A journey in the world of Bouffons\nand Grotesque Theatre"

    # primary image caption, gallery without the primary
    primary_caption = None
    gallery = []
    for src, cap in images:
        if src == primary:
            if cap and not re.fullmatch(r"\(\d+\)", cap):
                primary_caption = cap
            continue
        gallery.append((src, cap))
    # the first body picture of Language of Gestures and Red Nose Intensive IS the primary; others differ
    # write the workshop file
    fm = ["---", f"title: {json.dumps(title, ensure_ascii=False)}"]
    if subtitle:
        fm.append(f"subtitle: {json.dumps(subtitle, ensure_ascii=False)}")
    fm.append(f"image: {json.dumps(primary)}")
    if primary_caption:
        fm.append(f"image_caption: {json.dumps(primary_caption, ensure_ascii=False)}")
    if gallery:
        fm.append("gallery:")
        for src, cap in gallery:
            fm.append(f"  - src: {json.dumps(src)}")
            if cap:
                fm.append(f"    caption: {json.dumps(cap, ensure_ascii=False)}")
    if credits:
        fm.append(yaml_block("credits", "\n\n".join(credits)).rstrip("\n"))
    fm.append("---")
    (WS / f"{slug}.md").write_text("\n".join(fm) + "\n\n" + "\n\n".join(desc).strip() + "\n", encoding="utf-8")

    # the schedule entry
    if host_line:
        buckets["location"].insert(0, host_line)
    add = ""
    for key in ("schedule", "location", "tuition", "applications"):
        txt = "\n\n".join(buckets[key]).strip()
        if txt:
            name = {"location": "location_details"}.get(key, key)
            add += yaml_block(name, txt)
    sched = re.sub(r"^(schedule|location_details|tuition|applications): \|\n(?:  .*\n|\n)*", "", sched, flags=re.M)
    (SCHED / sched_file).write_text(sched.rstrip("\n") + "\n" + add, encoding="utf-8")
    print(slug, "| description blocks", len(desc), "| gallery", len(gallery), "| credits", bool(credits), "|", {k: len(v) for k, v in buckets.items() if k != "description"})
