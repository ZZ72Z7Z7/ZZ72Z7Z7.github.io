#!/usr/bin/env python3
"""Leftovers on the 20 workshop pages built on 261009 (read-through, designer's order):
 - pictures the old pages loaded from helikos.com (via i0.wp.com) are copied from the archive (media/_other) and served from /images/helikos/;
 - the caption numbers the old editor left after pictures, "(2)", are removed;
 - heading marks around a picture ("### ![](...)") or on their own line are removed;
 - a line that is only an email link or a phone number (a contact leftover), a caption number on its own line, and a <br> at the very end are removed.
The client's words are not touched. Run after tools/cut_old_edition_details.py:  python3 tools/clean_workshop_leftovers.py"""
import re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ARCH = ROOT.parent.parent / "WORDPRESS" / "site-archive" / "media" / "_other" / "www.helikos.com" / "public" / "image"
OUT = ROOT / "public" / "images" / "helikos"
OUT.mkdir(parents=True, exist_ok=True)
SLUGS = "20-movements-of-jacques-lecoq australia-dell-arte clowns-life conversations-with-the-fool from-the-neutral-mask-to-the-red-nose greenhouse-of-bouffons greenhouse-of-fools journey-of-the-neutral-mask-in-nature partnerships-in-play pedagogic-journey pedagogic-supervision-group personality-dell-arte politics-of-the-fool post-pandemic-clowns psychopathology-dell-arte spirit-of-commedia-dell-arte storyteller sublime-stupidity tao-of-clown teaching-red-nose-clown".split()

def hosted(m):
    name = m.group(1)
    src = ARCH / name
    if src.exists():
        shutil.copy2(src, OUT / name)
        return f"/images/helikos/{name}"
    print("  missing in the archive:", name)
    return m.group(0)

# edition booking text found on the read-through: whole blocks (paragraphs) that start with these words are removed
EXTRA_CUTS = {
    "australia-dell-arte": ["**SOME SPOTS ARE STILL AVAILABLE**", "Before the beginning of the workshop the participants will receive"],
    "conversations-with-the-fool": ["**BOOKINGS ARE ESSENTIAL VIA THIS LINK**", "[**https://www.trybooking.com", "Please note that the contributions are strictly non-refundable", "Before enrolling, please read", "For any question regarding the pedagogical content", "**Enrollment Deadline for all the panels"],
}

for slug in SLUGS:
    f = ROOT / "src" / "content" / "workshops" / f"{slug}.md"
    t = f.read_text(encoding="utf-8")
    n0 = len(t)
    t = re.sub(r"https://i0\.wp\.com/www\.helikos\.com/public/image/([^)\s\"]+)", hosted, t)
    t = re.sub(r"(!\[[^\]]*\]\([^)]*\))[ \t]*\(\d\)[ \t]*(?=\n|$)", r"\1", t)
    t = re.sub(r"^#{1,6}[ \t]+(?=!\[)", "", t, flags=re.M)
    t = re.sub(r"^#{1,6}[ \t]*\n(?=!\[)", "", t, flags=re.M)
    t = re.sub(r"^\*{0,2}\[[^\]]*@[^\]]*\]\(mailto:[^)]*\)\*{0,2}[ \t]*\n(\n)?", "", t, flags=re.M)
    t = re.sub(r"^\*?\(\d\)\*?[ \t]*\n?", "", t, flags=re.M)                  # a caption number on its own line, "(6)" or "*(6)*"
    t = re.sub(r"^\*\*Tel: [^\n]*\*\*[ \t]*\n?", "", t, flags=re.M)               # a phone number left over from the contact block
    t = re.sub(r"(\n<br>[ \t]*)+\s*$", "\n", t)                                     # <br> at the very end
    t = t.replace("Bruswick", "Brunswick").replace("July 202*2", "July 2022*")      # typos fixed at the designer's word, 261009
    if slug == "conversations-with-the-fool":      # lines that point to the removed booking section or give the old deadline
        t = re.sub(r"^(Scroll down to the \*\*practicalities\*\* session to find out about the \*\*booking process\*\*\.|\*\*Enrollment Deadline : [^\n]*\*\*)[ \t]*\n", "", t, flags=re.M)
        t = re.sub(r"\n{3,}", "\n\n", t)
    if slug in EXTRA_CUTS:
        head, sep, body = t.partition("\n---\n")
        head2, sep2, body2 = body.partition("\n---\n") if body.startswith("title") else ("", "", body)
        blocks = re.split(r"(\n\s*\n)", t)
        t = "".join(b for b in blocks if not any(b.lstrip().startswith(c) for c in EXTRA_CUTS[slug]))
        t = re.sub(r"\n{3,}", "\n\n", t)
    f.write_text(t, encoding="utf-8")
print("cleaned", len(SLUGS), "pages")
