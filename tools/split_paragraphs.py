#!/usr/bin/env python3
"""Paragraph breaks (designer, 261009). The old WordPress pages often ran several paragraphs together with a plain line break between them (a <br>), so they show with no gap.
This finds a line break that sits after a long, complete sentence-line (80+ characters, ending in . ! ? : … or a closing quote/bracket) and turns it into a paragraph break
(a blank line). The blog posts are not touched (deliberate line breaks). Short lines (verse, lists, addresses, credits, schedules) are never touched, nor are list items. Only whitespace changes: no word is touched.
Run from the project folder:  python3 tools/split_paragraphs.py            (report only)
                              python3 tools/split_paragraphs.py --write    (changes the files; a copy of src/content goes to archive/before-paragraph-breaks_261009/)"""
import re, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "src" / "content"
WRITE = "--write" in sys.argv
MIN_LEN = 80
END = re.compile(r"""[.!?:…][\s*_"”’)\]]*$|[”"’)\]][\s*_]*$""")
LIST = re.compile(r"^\s*([-–•*]\s|\d+[.)]\s|\\?[-–]\s)")

def visible(line):
    return re.sub(r"!\[[^\]]*\]\([^)]*\)|\[([^\]]*)\]\([^)]*\)|[*_`#>\\]|<[^>]+>|&nbsp;| ", lambda m: m.group(1) or "", line).strip()

def fix_block(block):
    lines = block.split("\n")
    if len(lines) < 2:
        return block, 0
    out, n = [lines[0]], 0
    for prev, cur in zip(lines, lines[1:]):
        v = visible(prev)
        starts_new = bool(visible(cur)) and not cur.strip().startswith(("<br>", "<", "!["))
        if len(v) >= MIN_LEN and END.search(v) and starts_new and not LIST.match(prev) and not LIST.match(cur) and visible(cur)[:1] not in ",;)]":
            out[-1] = prev.rstrip()          # drop the two trailing spaces: the break becomes a paragraph break
            out.append("")                   # blank line
            n += 1
        out.append(cur)
    return "\n".join(out), n

def fix_text(text):
    if text.startswith("---\n"):                     # leave the front matter alone here (long text fields are handled below)
        end = text.index("\n---\n", 4) + 5
        front, body = text[:end], text[end:]
    else:
        front, body = "", text
    fenced = re.split(r"(\n\s*\n)", body)
    total = 0
    for i in range(0, len(fenced), 2):
        fenced[i], n = fix_block(fenced[i]); total += n
    return front + "".join(fenced), total

def fix_yaml_blocks(text):
    """long text fields written as  key: |  blocks inside the front matter (schedule entries, workshop program, credits, body_it)"""
    total = 0
    def blk(m):
        nonlocal total
        key, content = m.group(1), m.group(2)
        raw = "\n".join(l[2:] if l.startswith("  ") else l for l in content.split("\n"))
        parts = re.split(r"(\n\s*\n)", raw)
        for i in range(0, len(parts), 2):
            parts[i], n = fix_block(parts[i]); total += n
        new = "\n".join(("  " + l) if l.strip() else "" for l in "".join(parts).split("\n"))
        return f"{key}: |\n{new}\n"
    text = re.sub(r"^((?:\w+)): \|\n((?:  .*\n|\n)*)", lambda m: blk(re.match(r"(.*?): \|\n((?:.|\n)*)", m.group(0).rstrip("\n") + "\n")) if False else blk(m), text, flags=re.M)
    return text, total

# the blog is left alone: its line breaks are often deliberate (poems, lists of questions) and the posts were not part of the complaint; ask the designer
files = sorted(p for p in CONTENT.rglob("*") if p.suffix in (".md", ".yml") and p.relative_to(CONTENT).parts[0] != "blog")
grand, changed = 0, []
for f in files:
    t = f.read_text(encoding="utf-8")
    new, n1 = fix_text(t) if f.suffix == ".md" else (t, 0)
    new, n2 = fix_yaml_blocks(new)
    if n1 + n2:
        changed.append((f.relative_to(CONTENT), n1 + n2))
        grand += n1 + n2
        if WRITE:
            f.write_text(new, encoding="utf-8")
if WRITE:
    bk = ROOT / "archive" / "before-paragraph-breaks_261009"
    if not bk.exists():
        shutil.copytree(CONTENT, bk)
for rel, n in changed:
    print(f"{n:4}  {rel}")
print(f"{grand} paragraph breaks in {len(changed)} files" + ("" if WRITE else " (report only)"))
