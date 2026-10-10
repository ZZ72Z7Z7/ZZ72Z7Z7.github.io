#!/usr/bin/env python3
"""Cuts the old edition details (TUITION, ENROLLMENT, HOW TO APPLY and the like, written for a past edition; SCHEDULE and LOCATION were reinstated at the designer's word, 261009) from the 20 workshop pages built on 261009
(designer's order). The description stays exactly as written. The originals are saved in archive/past-workshop-pages-before-cut_261009/.
Run from the project folder:  python3 tools/cut_old_edition_details.py [--write]   (without --write it only reports)"""
import re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
WS = ROOT / "src" / "content" / "workshops"
BACKUP = ROOT / "archive" / "past-workshop-pages-before-cut_261009"
WRITE = "--write" in sys.argv
SLUGS = ["20-movements-of-jacques-lecoq", "australia-dell-arte", "clowns-life", "conversations-with-the-fool", "from-the-neutral-mask-to-the-red-nose", "greenhouse-of-bouffons",
         "greenhouse-of-fools", "journey-of-the-neutral-mask-in-nature", "partnerships-in-play", "pedagogic-journey", "pedagogic-supervision-group", "personality-dell-arte",
         "politics-of-the-fool", "post-pandemic-clowns", "psychopathology-dell-arte", "spirit-of-commedia-dell-arte", "storyteller", "sublime-stupidity", "tao-of-clown", "teaching-red-nose-clown"]
PRACTICAL = [r"^LANGUAGE\b", r"^(TUITION|EARLY BIRD|FULL PRICE|DEPOSIT)\b", r"^ENROLL?MENT\b", r"^ENROLMENT\b",
             r"^(HOW TO APPLY|APPLICATIONS?|APPLICATION)\b", r"^(INFORMATION AND APPLICATIONS|VISA)\b", r"^PRACTICALITIES\b", r"^(FEES?|COST)\b",
             r"^(COVID PROTOCOL|ASSISTING PARTICIPANTS|DEVISING ASSISTANTS|EXTRA REHEARSAL TIME|A SAFETY MESSAGE|PERFORMING PARTICIPANTS)\b"]
LABEL = re.compile(r"^(?:#+\s*)?\*\*\s*([A-Z0-9][A-Z0-9 ’'&/,.:?!…–-]{2,70}?)\s*\*\*\s*(.*)$", re.S)
CONTACT = re.compile(r"^\*\*[A-Z][A-Z ’'.-]{3,40}\*\*")

APPLY_TEXT = re.compile(r"^(For enrollment and practical enquiries|Once the (seminar|workshop|class) (will be|is) confirmed|To apply|Please include in your letter|[–-]\s*\**\s*\**a (short bio|letter of motivation))")   # application instructions that sit under ADMISSION
KEEP_ALWAYS = re.compile(r"^This workshop is a collaboration between")                                                          # a credit that sits after the practical blocks

PRACTICAL_KEEP = [r"^SCHEDULE\b", r"^LOCATION\b"]   # reinstated at the designer's word
NOT_SCHEDULE = re.compile(r"(apply|application|enrol|deposit|tuition|early bird|full price|registration|letter of motivation|places will|confirmed as soon|giovanni will|once accepted|once the (workshop|seminar|class)|learning continuum|please note the)", re.I)   # application or fee text that sits under a SCHEDULE or LOCATION label

def lead(first):
    """the capitals a block opens with, whatever follows them on the line: '**SCHEDULE   September 25th**' -> 'SCHEDULE'"""
    t = re.sub(r"^[#\s]*\**\s*", "", first)
    m = re.match(r"[A-Z][A-Z0-9’'&/,.:?! –-]*", t)
    return m.group(0).strip() if m else ""

def is_practical(label):
    return any(re.search(p, label) for p in PRACTICAL)

def is_contact(block):
    """an organiser's name with an email address or phone number (a contact block): short, bold capitals, then mailto: or Tel:"""
    return bool(CONTACT.match(block.strip())) and ("mailto:" in block or "Tel:" in block) and len(block.split()) < 40

def cut(body):
    blocks = [b for b in re.split(r"\n\s*\n", body.strip("\n")) if b.strip()]
    merged = []
    for b in blocks:
        if b.strip() == "<br>" and merged:
            merged[-1] += "\n<br>"
        else:
            merged.append(b)
    # a block can hold several labelled parts joined by <br> lines: split them
    parts = []
    for b in merged:
        parts += [x for x in re.split(r"\n(?:<br>\n)?(?=(?:#+\s*)?\*\*[A-Z][A-Z0-9 ’'&/,.:?!…–-]{3,}\*\*)", b) if x.strip()]
    merged = parts
    keep, dropped, practical, keep_sl = [], [], False, False
    for b in merged:
        first = b.split("\n", 1)[0]
        L = lead(first)
        if len(L) >= 4 and re.match(r"^[#\s]*\*", first):          # a bold (or heading) line that opens with capitals is a label
            practical = is_practical(L)
            keep_sl = any(re.search(k, L) for k in PRACTICAL_KEEP)
            if keep_sl:
                (keep).append(b)
                continue
            if not practical and not any(re.search(k, L) for k in PRACTICAL_KEEP):
                keep_sl = False
        elif keep_sl and NOT_SCHEDULE.search(b):
            dropped.append(b)
            continue
        if is_contact(b) or APPLY_TEXT.match(b.strip()):
            dropped.append(b)
            continue
        (keep if KEEP_ALWAYS.match(b.strip()) or not practical else dropped).append(b)
    return "\n\n".join(keep).strip() + "\n", dropped

if WRITE:
    BACKUP.mkdir(parents=True, exist_ok=True)
for slug in SLUGS:
    f = WS / f"{slug}.md"
    text = f.read_text(encoding="utf-8")
    m = re.match(r"(---\n.*?\n---\n)\n(.*)", text, re.S)
    front, body = m.group(1), m.group(2)
    new, dropped = cut(body)
    words_before, words_after = len(body.split()), len(new.split())
    first_lines = [d.split("\n", 1)[0][:30] for d in dropped]
    print(f"{slug:40} {words_before:5} -> {words_after:5} words ({len(dropped):2} blocks cut)  last kept: {new.strip().splitlines()[-1][:60]!r}")
    if '--v' in sys.argv: print('    CUT:', first_lines)
    if WRITE:
        shutil.copy2(f, BACKUP / f.name)
        f.write_text(front + "\n" + new, encoding="utf-8")
