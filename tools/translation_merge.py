#!/usr/bin/env python3
"""Merges the Italian draft translations (translations/it/) into the content files (261009). Everything it writes is a DRAFT drafted by Claude: it needs human review
(see ITALIAN-REVIEW.md). Text-based: only new fields are added; no English text is touched. Run from the project folder:  python3 tools/translation_merge.py [--check]
Fields added: workshops (subtitle_it, body_it, program_it, image_caption_it, credits_it, gallery caption_it, translation), schedule (schedule_it, location_details_it, tuition_it,
applications_it, extra_dates_it, language_note_it, description_it, translation), events (title_it, subtitle_it, body_it, admission_it, pdfs label_it, translation),
blog (title_it, body_it, translation), pages (src/content/pages/it/<file>, front matter key translation: draft)."""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "src" / "content"
OUT = ROOT / "translations" / "it"
CHECK = "--check" in sys.argv
TR = '"draft"'

def sections(text):
    parts = re.split(r"^=== (\w+) ===\n", text, flags=re.M)
    return {parts[i]: parts[i + 1].rstrip("\n") for i in range(1, len(parts) - 1, 2)}

def block(key, text, indent=0):
    pad = " " * indent
    body = "\n".join((pad + "  " + l) if l.strip() else "" for l in text.strip("\n").split("\n"))
    return f"{pad}{key}: |-\n{body}\n"

def numbered(txt):
    out = {}
    for line in txt.split("\n"):
        m = re.match(r"^(\d+):\s*(.*)$", line)
        if m:
            out[int(m.group(1))] = m.group(2).strip()
    return out

def strip_keys(front, keys):
    for k in keys:
        front = re.sub(rf"^{k}: .*\n(?:  .*\n|\n)*?(?=^\S|\Z)", "", front, flags=re.M) if False else front
    return front

def add_fields(path, fields, gallery=None, pdfs=None):
    t = path.read_text(encoding="utf-8")
    m = re.match(r"(---\n)(.*?)(\n---\n)(.*)", t, re.S)
    yml = m is None                                   # schedule entries are plain YAML files without --- lines
    if yml:
        front, rest = t.rstrip("\n"), ""
    else:
        front, rest = m.group(2), m.group(4)
    for k in list(fields) + ["translation"]:      # replace a previous draft of the same field
        front = re.sub(rf"^{k}: (?:\|-?\n(?:  .*\n|\n)*|[^\n]*\n)", "", front + "\n", flags=re.M).rstrip("\n")
    add = ""
    for k, v in fields.items():
        add += block(k, v) if ("\n" in v or len(v) > 90) else f"{k}: {json.dumps(v, ensure_ascii=False)}\n"
    add += f"translation: {TR}\n"
    front = re.sub(r"^    (caption_it|label_it): .*\n?", "", front + "\n", flags=re.M).rstrip("\n")   # drop an earlier draft's per-item fields
    if gallery:
        lines = front.split("\n"); out = []; gi = -1
        for i, l in enumerate(lines):
            if re.match(r"^  - src: ", l):
                gi += 1
            out.append(l)
            if gi + 1 in gallery and re.match(r"^    caption: ", l):
                out.append(f"    caption_it: {json.dumps(gallery[gi + 1], ensure_ascii=False)}")
        front = "\n".join(out)
    if pdfs:
        lines = front.split("\n"); out = []; pi = -1
        for l in lines:
            if re.match(r"^  - label: ", l):
                pi += 1
                out.append(l)
                if pi + 1 in pdfs:
                    out.append(f"    label_it: {json.dumps(pdfs[pi + 1], ensure_ascii=False)}")
                continue
            out.append(l)
        front = "\n".join(out)
    if yml:
        new = front.rstrip("\n") + "\n" + add
    else:
        new = m.group(1) + front.rstrip("\n") + "\n" + add + "---\n" + ("\n" + rest.lstrip("\n") if rest.strip() else "")
    if not CHECK:
        path.write_text(new, encoding="utf-8")

done = {}
def run(cat, fn):
    d = OUT / cat
    n = 0
    if d.exists():
        for f in sorted(d.iterdir()):
            if f.name.startswith((".", "_")):
                continue
            fn(f); n += 1
    done[cat] = n

def workshops(f):
    s = sections(f.read_text(encoding="utf-8")); s.pop("notes", None)
    gal = numbered(s.pop("gallery_captions", "")) if "gallery_captions" in s else None
    fields = {}
    for src, key in (("subtitle", "subtitle_it"), ("body", "body_it"), ("program", "program_it"), ("image_caption", "image_caption_it"), ("credits", "credits_it")):
        if src in s: fields[key] = s[src]
    add_fields(CONTENT / "workshops" / f.name, fields, gallery=gal)

def blog(f):
    s = sections(f.read_text(encoding="utf-8"))
    fields = {k + "_it": s[k] for k in ("title", "body") if k in s}
    add_fields(CONTENT / "blog" / f.name, fields)

def events(f):
    s = sections(f.read_text(encoding="utf-8"))
    fields = {k + "_it": s[k] for k in ("title", "subtitle", "body", "admission") if k in s}
    add_fields(CONTENT / "events" / f.name, fields, pdfs=numbered(s["pdf_labels"]) if "pdf_labels" in s else None)

def schedule(f):
    s = sections(f.read_text(encoding="utf-8"))
    fields = {k + "_it": s[k] for k in ("schedule", "location_details", "tuition", "applications", "extra_dates", "language_note") if k in s}
    add_fields(CONTENT / "schedule" / (f.stem + ".yml"), fields)

def pages(f):
    t = f.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n(.*)", t, re.S)
    if not m:
        raise SystemExit(f"{f}: no front matter")
    dest = CONTENT / "pages" / "it" / f.name
    if not CHECK:
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(f"---\n{m.group(1).rstrip()}\ntranslation: {TR}\n---\n{m.group(2)}", encoding="utf-8")

run("workshops", workshops); run("blog", blog); run("events", events); run("schedule", schedule); run("pages", pages)
tsv = OUT / "schedule" / "_taglines.tsv"
if tsv.exists():
    n = 0
    for line in tsv.read_text(encoding="utf-8").splitlines():
        if "\t" not in line: continue
        fn, tag = line.split("\t", 1)
        add_fields(CONTENT / "schedule" / fn, {"description_it": tag.strip().replace(" / ", "\n") if False else tag.strip()})
        n += 1
    done["taglines"] = n
print(done, "(check only)" if CHECK else "")
