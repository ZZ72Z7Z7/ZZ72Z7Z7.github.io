#!/usr/bin/env python3
"""Fills in the PAST workshops of the Workshops list (designer, 261009), from two sources:
  1. the old site's Past Workshops page (giovannifusetti.com/past-workshops/, from the archive): June 2018 to August 2026;
  2. the Helikos workshop history (helikos.com/pages/workshops.php?view=all, saved as tools/data/helikos-workshops_261009.json): 2009 to 2020.
Where both list the same workshop (same start date), the Giovanni page wins. No thumbnails and no individual pages are made for past workshops.
Entries that are not workshops (see EXCLUDE) are left out and reported. Run from the project folder:  python3 tools/import_past_workshops.py [--write]
Without --write it only prints what it would do. With --write it replaces every past schedule entry (the upcoming ones are kept)."""
import csv, json, re, subprocess, sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NODE = ROOT.parent / ".tools" / "node" / "bin" / "node"
SCHED = ROOT / "src" / "content" / "schedule"
WRITE = "--write" in sys.argv
TODAY = date.fromisoformat(__import__("os").environ.get("SITE_TODAY", date.today().isoformat()))

# ------------------------------------------------------------------ parsing the Giovanni page
MONTHS = {m: i + 1 for i, m in enumerate(["january", "february", "march", "april", "may", "june", "july", "august", "september", "october", "november", "december"])}
MONTHS["dicember"] = 12   # his spelling on the old page

def strip_md(s):
    s = s.replace("\\(opens in a new tab\\)", "").replace("\\(opens%20in%20a%20new%20tab\\)", "")
    s = re.sub(r"\[((?:[^\[\]]|\n)*?)\]\((?:<[^>]*>|[^)]*)\)", r"\1", s)
    s = s.replace("\\-", "-").replace("\\*", "*").replace("​", "").replace("\xa0", " ")
    s = re.sub(r"\*+|__", "", s).replace("<br>", "")
    return s

LINK = re.compile(r"(?<!!)\[((?:[^\[\]]|\n)*?)\]\((<[^>]*>|(?:[^()]|\\\(|\\\))*?)\)")
DATE_LINE = re.compile(r"(?:January|February|March|April|May|June|July|August|September|October|November|December|Dicember)\b[^\n]*\d{4}", re.I)

def parse_dates(txt):
    txt = txt.replace("→", "→").replace("–", "→").replace("\xa0", " ")
    txt = re.sub(r"→\s*(?=[A-Za-z]+[, ]*$)", "", txt)           # a trailing place after a dash
    txt = re.sub(r"\s+", " ", txt).strip(" →")
    m = re.fullmatch(r"([A-Za-z]+) (\d+),? (\d{4}) ?→ ?([A-Za-z]+) (\d+),? (\d{4})(?: →.*)?", txt)
    if m:
        return (date(int(m.group(3)), MONTHS[m.group(1).lower()], int(m.group(2))), date(int(m.group(6)), MONTHS[m.group(4).lower()], int(m.group(5))))
    m = re.fullmatch(r"([A-Za-z]+) (\d+)(?:,? (\d{4}))? ?→ ?(?:([A-Za-z]+) )?(\d+),? (\d{4})", txt)
    if m:
        mon1 = MONTHS[m.group(1).lower()]; mon2 = MONTHS[m.group(4).lower()] if m.group(4) else mon1; yr = int(m.group(6))
        return (date(yr, mon1, int(m.group(2))), date(yr, mon2, int(m.group(5))))
    m = re.fullmatch(r"([A-Za-z]+) ([\d, ]+?),? (\d{4})", txt)
    if m:
        days = [int(x) for x in re.findall(r"\d+", m.group(2))]
        mon = MONTHS[m.group(1).lower()]; yr = int(m.group(3))
        return (date(yr, mon, days[0]), date(yr, mon, days[-1]))
    raise ValueError("date? " + txt)

def is_img(l):
    s = l.strip()
    return s.startswith("![") or s.startswith("[![") or s in ("!", "")

def split_entries(md):
    out = []
    for block in md.split("\n---\n"):
        lines = block.split("\n")
        idx = [i for i, l in enumerate(lines) if DATE_LINE.search(strip_md(l)) and "](" not in l and not l.strip().startswith("![")]
        if not idx:
            continue
        # date lines that follow each other (only blanks or '&' between) belong to one entry
        groups = [[idx[0]]]
        for i in idx[1:]:
            between = [strip_md(l).strip() for l in lines[groups[-1][-1] + 1:i]]
            if all(b in ("", "&") for b in between):
                groups[-1].append(i)
            else:
                groups.append([i])
        pre = [strip_md(l).strip() for l in lines[:groups[0][0]] if not is_img(l) and strip_md(l).strip()]
        for k, g in enumerate(groups):
            end = groups[k + 1][0] if k + 1 < len(groups) else len(lines)
            out.append({"pre": pre if k == 0 else [], "date_lines": [lines[i] for i in g], "body": "\n".join(lines[g[-1] + 1:end])})
    return out

def parse_entry(e):
    body = e["body"]
    ms = [m for m in LINK.finditer(body) if m.group(1).strip() and "uploads" not in m.group(2)]
    title_raw, end, href = "", 0, None
    if ms:
        first = ms[0]; start = first.start(); end = first.end(); href = re.sub(r"\\\(.*?\\\)", "", first.group(2).strip("<>")).strip()
        for m in ms[1:]:
            if re.fullmatch(r"[\s*]*", body[end:m.start()]):
                end = m.end()
            else:
                break
        title_raw = body[start:end]
        before = strip_md(body[:start]); after = strip_md(body[end:])
    else:
        before = strip_md(body); after = ""
    return {"pre": e["pre"], "dates_text": [strip_md(l).strip() for l in e["date_lines"]], "before": before, "title": strip_md(title_raw), "after": after, "href": href, "raw": body}

# ------------------------------------------------------------------ normalising
SMALL = {"of", "and", "the", "to", "in", "for", "with", "on", "a", "an", "at", "by", "from", "or"}
def title_case(s):
    s = re.sub(r"\s+", " ", s.replace("\xa0", " ")).strip().replace("'", "’")
    s = re.sub(r"\bDELL\s*[’'‘]?\s*ARTE\b", "dell’Arte", s, flags=re.I)
    words = s.split(" ")
    out = []
    for i, w in enumerate(words):
        letters = re.sub(r"[^A-Za-z]", "", w)
        if letters and letters.isupper() and len(letters) > 1 and w != "dell’Arte" and not re.fullmatch(r"I{1,3}|IV|V", letters) and not re.fullmatch(r"\d+(ND|RD|TH|ST)", letters + ""):
            lw = w.lower()
            lw = re.sub(r"(^|[-:(])([a-z])", lambda m: m.group(1) + m.group(2).upper(), lw)
            if re.sub(r"[^a-z]", "", lw.lower()) in SMALL and i > 0 and not words[i - 1].endswith((":", ".", "!", "?")):
                lw = lw.lower()
            w = lw
        out.append(w)
    return " ".join(out)

COUNTRIES = {"italy": "Italy", "australia": "Australia", "usa": "USA", "new zealand": "Aotearoa, New Zealand", "aotearoa": "Aotearoa, New Zealand", "new zealand-aotearoa": "Aotearoa, New Zealand",
             "aotearoa-new zealand": "Aotearoa, New Zealand", "aotearoa – new zealand": "Aotearoa, New Zealand", "uk": "UK", "germany": "Germany", "slovenia": "Slovenia", "slovenja": "Slovenia",
             "france": "France", "finland": "Finland", "south africa": "South Africa", "norway": "Norway", "united states": "USA"}
REGIONS = {"colorado": "Colorado", "oregon": "Oregon", "maine": "Maine", "vermont": "Vermont", "tasmania": "Tasmania", "tuscany": "Tuscany", "veneto region": "Veneto Region", "pa": "PA",
           "california": "California", "lucca": "Lucca"}

def norm_place(raw):
    """-> dict(city, region, country, venue) from the several ways the old pages write a place."""
    s = re.sub(r"\s+", " ", raw.replace("\n", " ").replace("\xa0", " ")).strip(" -–")
    s = re.sub(r"\s*[–-]\s*", " - ", s) if re.search(r"[A-Za-z]-[A-Z]{3,}", s) or " - " in s or " – " in s else s
    parts = [p.strip() for p in re.split(r",| - | – |(?<=[a-z])-(?=[A-Z])", s) if p.strip()]
    res = {"city": None, "region": None, "country": None, "venue": None}
    for p in parts:
        key = p.lower().replace("’", "'")
        if key in COUNTRIES and not res["country"]:
            res["country"] = COUNTRIES[key]
        elif key in REGIONS and not res["region"]:
            res["region"] = REGIONS[key]
        elif not res["city"]:
            res["city"] = title_case(p) if p.isupper() or p.islower() else p
        elif not res["venue"]:
            res["venue"] = title_case(p) if p.isupper() or p.islower() else p
    return res

# ------------------------------------------------------------------ the five workshops that have pages (editions link to them)
WORKSHOP_OF = {}
NAMES = {"The Language of Gestures": "language-of-gestures", "Red Nose Intensive": "red-nose-intensive", "Famiglia dell’Arte": "famiglia-dell-arte",
         "Bouffon Intensive": "bouffon-intensive", "Bring Your Own Psyche": "bring-your-own-psyche"}
for r in csv.DictReader(open(ROOT / "migration-map.csv", encoding="utf-8-sig")):
    if r["workshop"] in NAMES:
        WORKSHOP_OF[r["old_url"].strip("/")] = NAMES[r["workshop"]]

EXCLUDE = {"ONLINE TRAINING?": "an essay (\"Why I don't teach online\"), not a workshop", "CLIMATE CHANGE COMEDY VIDEOS": "a video campaign in Auckland, not a workshop"}
DROP_PRE = {"PAST WORKSHOPS", "Boulder International Summer Program 2018"}

def lines_of(txt):
    return [re.sub(r"\s+", " ", l).strip() for l in txt.split("\n") if l.strip() and l.strip() not in ("!", "Details")]

def is_upper_line(l):
    letters = re.sub(r"[^A-Za-z]", "", l)
    return bool(letters) and sum(c.isupper() for c in letters) / len(letters) > 0.7

def parse_with(lines):
    """-> (tagline_lines, teachers, collab, collab_url, language)"""
    tagline, teachers, collab, language = [], None, None, None
    i = 0
    while i < len(lines):
        l = lines[i]
        low = l.lower()
        if low == "with" and i + 1 < len(lines):
            teachers = lines[i + 1]; i += 2; continue
        if low.startswith("with ") and not tagline_is_sentence(l):
            teachers = l[5:]; i += 1; continue
        if low.startswith("in collaboration with"):
            collab = l[len("in collaboration with"):].strip() or (lines[i + 1] if i + 1 < len(lines) else None)
            i += 1 if l[len("in collaboration with"):].strip() else 2; continue
        if low.startswith("within the eu project"):
            collab = lines[i + 1] if i + 1 < len(lines) else None; i += 2; continue
        if low in ("in english", "in italian", "in english and italian"):
            language = l; i += 1; continue
        tagline.append(l); i += 1
    return tagline, teachers, collab, language

def tagline_is_sentence(l):
    return False

def clean_names(t):
    """'Zsófi Kigyóssy and Giovanni Fusetti' -> 'Zsófi Kigyóssy' (Giovanni teaches every workshop, so he is not listed)."""
    if not t:
        return None
    names = [n.strip() for n in re.split(r",| and ", t) if n.strip() and "giovanni fusetti" not in n.lower()]
    return ", ".join(names) or None

def giovanni_entries():
    md = subprocess.run([str(NODE), str(ROOT / "tools" / "html_to_md.mjs"), "past-workshops"], capture_output=True, text=True, check=True).stdout
    out = []
    for e in split_entries(md):
        p = parse_entry(e)
        raw_dates = p["dates_text"]
        # two cities in one entry (The Tao of Clown, September 2019): one entry per city
        if len(raw_dates) == 2 and all(re.search(r"[–-]\s*[A-Za-z]+", re.sub(r"\d{4}", "", d.split("→")[-1])) and "," in d for d in raw_dates) and "TAO OF CLOWN" in e["body"].upper():
            for d in raw_dates:
                m = re.match(r"(.*?\d{4})\s*[–-]\s*(.*)$", d.replace("\xa0", " "))
                a, b = parse_dates(m.group(1))
                out.append({"src": "giovanni", "start": a, "end": b, "extra": None, "place": norm_place(m.group(2)), "title": "The Tao of Clown", "tagline": ["A Poetic Journey of Awareness through Laughter"], "teachers": None, "collab": None, "language": None, "href": None})
            continue
        ranges = [parse_dates(d) for d in raw_dates]
        title_lines = [l for l in re.split(r"\n+", p["title"]) if l.strip()]
        title_lines = [re.sub(r"\s+", " ", l).strip() for l in title_lines if l.strip() not in ("Details",)]
        # a link text that carries its own tagline (the Helikos-style entries): capitals are the title, the rest is the tagline
        t_title, t_tag = [], []
        for l in title_lines:
            if not t_tag and (is_upper_line(l) or not t_title or l.split()[0].isupper() and len(l.split()) <= 2):
                t_title.append(l)
            else:
                t_tag.append(l)
        title = " ".join(t_title)
        before = lines_of(p["before"])
        after = lines_of(p["after"])
        tagline, teachers, collab, language = parse_with(t_tag + after)
        place_lines = [l for l in before if not l.lower().startswith("in collaboration")] or [l for l in p["pre"] if l not in DROP_PRE]
        for l in before:
            if l.lower().startswith("in collaboration"):
                collab = l[len("in collaboration with"):].strip()
        if not place_lines and p["pre"]:
            place_lines = [l for l in p["pre"] if l not in DROP_PRE]
        title = re.sub(r"\s+", " ", title)
        out.append({"src": "giovanni", "start": ranges[0][0], "end": ranges[-1][1], "ranges": ranges, "place": norm_place(" ".join(place_lines)), "title": title, "tagline": tagline,
                    "teachers": clean_names(teachers), "collab": collab, "language": language, "href": p["href"]})
    return out

def helikos_entries():
    data = json.load(open(ROOT / "tools" / "data" / "helikos-workshops_261009.json", encoding="utf-8"))
    out = []
    for d in data:
        place_raw = d["place"]
        if not re.search(r"[A-Za-z]", place_raw) or len(place_raw.split()) > 6 and "," not in place_raw:
            place_raw = ""
        start = date.fromisoformat(d["start"]); end = date.fromisoformat(d["end"]) if d["end"] else start
        out.append({"src": "helikos", "start": start, "end": end, "ranges": [(start, end)], "place": norm_place(place_raw), "place_raw": d["place"], "title": d["title"], "tagline": [d["description"]] if d["description"] else [],
                    "teachers": None, "collab": None, "language": None, "href": None})
    return out


# ------------------------------------------------------------------ cleaning, merging, writing
sys.path.insert(0, str(ROOT / "tools"))
from yamlish import dump

COUNTRY_OF_REGION = {"Colorado": "USA", "Oregon": "USA", "Vermont": "USA", "Maine": "USA", "California": "USA", "PA": "USA", "Tasmania": "Australia", "Tuscany": "Italy", "Lucca": "Italy", "Veneto Region": "Italy"}
LINKED = {"the language of gestures": "language-of-gestures", "red nose intensive": "red-nose-intensive", "bouffon intensive": "bouffon-intensive",
          "famiglia dell’arte": "famiglia-dell-arte", "bring your own psyche": "bring-your-own-psyche",
          # the pages built 261009 (tools/import_past_workshop_pages.py)
          "the 20 movements of jacques lecoq": "20-movements-of-jacques-lecoq",
          "australia dell’arte": "australia-dell-arte",
          "clown’s life": "clowns-life",
          "conversations with the fools": "conversations-with-the-fool",
          "conversations with the fool": "conversations-with-the-fool",
          "from the neutral mask to the red nose": "from-the-neutral-mask-to-the-red-nose",
          "the greenhouse of bouffons": "greenhouse-of-bouffons",
          "the greenhouse of fools": "greenhouse-of-fools",
          "the journey of the neutral mask in nature": "journey-of-the-neutral-mask-in-nature",
          "partnerships in play": "partnerships-in-play",
          "the pedagogic journey": "pedagogic-journey",
          "pedagogic supervision group": "pedagogic-supervision-group",
          "personality dell’arte": "personality-dell-arte",
          "the politics of the fool": "politics-of-the-fool",
          "post-pandemic clowns": "post-pandemic-clowns",
          "psychopathology dell’arte": "psychopathology-dell-arte",
          "the spirit of commedia dell’arte": "spirit-of-commedia-dell-arte",
          "the storyteller": "storyteller",
          "the sublime stupidity": "sublime-stupidity",
          "the tao of clown": "tao-of-clown",
          "teaching red nose clown": "teaching-red-nose-clown"}
TITLE_FIX = {"He Greenhouse of Fools": "The Greenhouse of Fools", "The Mimodynamic of the land": "The Mimodynamic of the Land", "Il Guerriero E Il Clown": "Il Guerriero e il Clown", "Dreambody Theatre II : Grotesque and Bouffons": "Dreambody Theatre II : Grotesque and Bouffons"}
# places the generic parser cannot read: raw text -> (city, region, country, venue)
PLACE_FIX = {"MELBOURNE-Australia": ("Melbourne", None, "Australia", None), "PADOVA- Italy": ("Padova", None, "Italy", None),
             "Celebration Barn Theater, MAINE": (None, "Maine", "USA", "Celebration Barn Theater"), "Celebration Barn Theatre, Maine, USA": (None, "Maine", "USA", "Celebration Barn Theatre"),
             "Welcome Bay, Tauranga, New Zealand-Aotearoa": ("Welcome Bay, Tauranga", None, "Aotearoa, New Zealand", None), "Florence": ("Florence", None, None, None),
             "The Journey of the Poetic Body and the essence of Physical Comedy": ("Boulder", "Colorado", "USA", None)}

def sentence_if_caps(t):
    letters = re.sub(r"[^A-Za-z]", "", t)
    if letters and letters.isupper():
        t = t.lower(); t = t[0].upper() + t[1:]
    return t

def fix_place(e):
    pl = dict(e["place"])
    raw = e.get("place_raw")
    if raw in PLACE_FIX:
        c, r, co, v = PLACE_FIX[raw]; pl = {"city": c, "region": r, "country": co, "venue": v}
    elif e["src"] == "helikos" and raw:
        pl = norm_place(re.sub(r"\s*-\s*", " - ", raw))
    # leftovers on the Giovanni page
    city = pl["city"] or ""
    city = re.sub(r"\s+(Aotearoa|GERMANY)$", "", city)
    if pl["city"] and pl["city"].endswith("GERMANY"): pl["country"] = "Germany"
    if city == "Ljubliana": pass                       # his spelling on Helikos; reported, not fixed
    city = {"Padua": "Padova", "PADOVA": "Padova", "Ljubliana": "Ljubljana"}.get(city, city)   # client preference (261011): "Padova" in every language
    pl["city"] = city or None
    v = pl["venue"] or ""
    m = re.fullmatch(r"(Colorado) USA", v)
    if m: pl["region"], pl["country"], pl["venue"] = "Colorado", "USA", None
    if v in ("Italy T",): pl["country"], pl["venue"] = "Italy", None
    if v in ("Aotearoa", "New Zealand", "Tauranga") and pl["country"] == "Aotearoa, New Zealand" and v != "Tauranga": pl["venue"] = None
    if not pl["country"] and pl["region"] in COUNTRY_OF_REGION: pl["country"] = COUNTRY_OF_REGION[pl["region"]]
    if pl["city"] in ("Boulder",) and not pl["country"]: pl["country"] = "USA"
    if pl["city"] == "Firenze" and not pl["country"]: pl["country"] = "Italy"
    if pl["city"] == "Florence" and not pl["country"]: pl["country"] = "Italy"
    if pl["city"] == "Auckland" and not pl["country"]: pl["country"] = "Aotearoa, New Zealand"
    return pl

def build_tagline(e):
    lines = [l for l in e["tagline"] if not re.fullmatch(r"\[!\]\(.*\)", l.strip())]
    lines = [re.sub(r"\\\.", ".", l) for l in lines]
    numbered = [l for l in lines if re.match(r"\d\.", l)]
    if numbered:
        head = [l for l in lines if l not in numbered]
        lines = [" ".join(head) + ": " + "; ".join(title_case(n) for n in numbered)]
    t = re.sub(r"\s+", " ", " ".join(lines)).strip()
    t = t.replace("Govanni", "Giovanni").replace("A introductory", "An introductory").replace("rnPIG IRON", "PIG IRON")   # typos corrected at the designer's word, 261009
    return sentence_if_caps(t) if t else None

def finish(e):
    title = title_case(e["title"])
    title = TITLE_FIX.get(title, title)
    if e["start"].year == 2009 and "2008" in title: title = title.replace("2008", "2009")   # designer, 261009
    pl = fix_place(e)
    tag = build_tagline(e)
    teachers = e["teachers"]
    if tag and tag.lower().startswith("with ") and not teachers:
        teachers = title_case(tag[5:]); tag = None
    collab = title_case(e["collab"]) if e["collab"] else None
    ranges = e.get("ranges") or [(e["start"], e["end"])]
    out = {"start": e["start"], "end": e["end"], "title": title, "tag": tag, "place": pl, "teachers": teachers, "collab": collab, "collab_url": None,
           "language": e["language"], "ranges": ranges, "src": e["src"]}
    h = e.get("href") or ""
    if collab and h and "giovannifusetti.com" not in h and "helikos.com" not in h:
        out["collab_url"] = h
    elif h and "giovannifusetti.com" not in h and "helikos.com" not in h and not collab and e["src"] == "giovanni":
        out["collab_url"] = None
    if out["start"] == date(2025, 7, 26): out["collab_url"] = "https://pigiron.org/school/workshops/the-spirit-of-commedia-dell-arte/"   # kept from the earlier hand-made entry
    return out

def norm_title(t):
    return re.sub(r"[^a-z]", "", t.lower().replace("’", "").replace("'", ""))

def merge():
    gio = [finish(e) for e in giovanni_entries()]
    hel_raw = helikos_entries()
    excluded, notes = [], []
    gkeys = {g["start"]: g for g in gio}
    hel, seen = [], {}
    for e in hel_raw:
        if e["title"].upper() in EXCLUDE:
            excluded.append((e["start"], e["title"], EXCLUDE[e["title"].upper()])); continue
        f = finish(e)
        if f["start"] in gkeys:
            g = gkeys[f["start"]]
            diffs = [n for n, a, b in (("title", norm_title(g["title"]), norm_title(f["title"])), ("end", g["end"], f["end"]), ("city", (g["place"]["city"] or "").lower(), (f["place"]["city"] or "").lower())) if a != b]
            notes.append(f"{f['start']} {g['title']}: both lists have it" + (f"; differ in {', '.join(diffs)}" if diffs else "; same"))
            continue
        inside = [g for g in gio if norm_title(g["title"]) == norm_title(f["title"]) and g["start"] <= f["start"] <= g["end"]]
        if inside:
            notes.append(f"{f['start']} {f['title']}: Helikos date range lies inside the Giovanni entry of {inside[0]['start']}; Helikos one left out"); continue
        if e["title"].startswith("Boulder International Clown School 2012"):
            notes.append(f"{f['start']} {f['title']}: duplicate inside Helikos (same dates and place as the \"Helikos International Summer School 2012\" entry); left out"); continue
        hel.append(f)
    return sorted(gio + hel, key=lambda x: (x["start"], x["title"]), reverse=True), excluded, notes

def slugify(t):
    t = t.lower().replace("’", "").replace("'", "")
    return re.sub(r"[^a-z0-9]+", "-", t).strip("-")[:60]

MON = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
def en_range(a, b):
    if a == b: return f"{MON[a.month-1]} {a.day}, {a.year}"
    if a.year != b.year: return f"{MON[a.month-1]} {a.day}, {a.year} - {MON[b.month-1]} {b.day}, {b.year}"
    if a.month != b.month: return f"{MON[a.month-1]} {a.day} - {MON[b.month-1]} {b.day}, {b.year}"
    return f"{MON[a.month-1]} {a.day} - {b.day}, {b.year}"

def to_yaml(e):
    d = {}
    wk = LINKED.get(e["title"].lower())
    if wk: d["workshop"] = wk
    else: d["title"] = e["title"]
    d["start"] = e["start"].isoformat()
    d["end"] = e["end"].isoformat()
    if len(e["ranges"]) > 1: d["extra_dates"] = "\n&\n".join(en_range(a, b) for a, b in e["ranges"])
    pl = e["place"]
    for k in ("city", "region", "country", "venue"):
        d[k] = pl[k]
    if e["teachers"]: d["taught_with"] = e["teachers"]
    if e["collab"]: d["collaboration_name"] = e["collab"]
    if e["collab_url"]: d["collaboration_url"] = e["collab_url"]
    if e["language"]: d["language_note"] = e["language"]
    if e["tag"] and not wk: d["description"] = e["tag"]
    return d

if __name__ == "__main__":
    entries, excluded, notes = merge()
    past = [e for e in entries if e["end"] < TODAY]
    print(f"{len(entries)} entries ({sum(e['src']=='giovanni' for e in entries)} from the Giovanni page, {sum(e['src']=='helikos' for e in entries)} Helikos only); {len(past)} are past")
    for e in entries:
        d = to_yaml(e)
        print(f"{d['start']} | {d.get('workshop') or d['title']} | {d.get('city')}/{d.get('region')}/{d.get('country')}/{d.get('venue')} | {d.get('description')} | with={d.get('taught_with')} collab={d.get('collaboration_name')} lang={d.get('language_note')}" + (" | EXTRA" if 'extra_dates' in d else ""))
    print("\nEXCLUDED:"); [print(" ", x) for x in excluded]
    print("\nNOTES:"); [print(" ", x) for x in notes]
    if WRITE:
        import shutil
        back = ROOT / "tools" / "data" / "schedule-backup_261009"
        back.mkdir(exist_ok=True)
        for f in SCHED.glob("*.yml"):
            m = re.search(r"end: (\d{4}-\d\d-\d\d)", f.read_text()) or re.search(r"start: (\d{4}-\d\d-\d\d)", f.read_text())
            if date.fromisoformat(m.group(1)) < TODAY:
                shutil.copy(f, back / f.name); f.unlink()
        names = set()
        for e in past:
            d = to_yaml(e)
            n = f"{d['start']}-{slugify(e['title'])}"
            if n in names: n += "-" + e["place"]["city"].lower().replace(" ", "-") if e["place"]["city"] else "-b"
            names.add(n)
            (SCHED / f"{n}.yml").write_text(dump(d), encoding="utf-8")
        print(f"\nwrote {len(past)} files")
