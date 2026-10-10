#!/usr/bin/env python3
"""Moves the "THE PROGRAM" section of a workshop description into its own `program` field (designer, 261009), for the workshops that have one.
The section runs from the bold line THE PROGRAM up to the bold line ADMISSION (or the end); the heading line itself is dropped because the page
shows it as the accordion heading. Run once from the project folder:  python3 tools/split_program.py"""
import re, json
from pathlib import Path

WS = Path(__file__).resolve().parent.parent / "src" / "content" / "workshops"

def yaml_block(key, text):
    return f"{key}: |\n" + "\n".join(("  " + l) if l.strip() else "" for l in text.strip("\n").split("\n")) + "\n"

for f in sorted(WS.glob("*.md")):
    text = f.read_text(encoding="utf-8")
    m = re.match(r"---\n(.*?)\n---\n\n?(.*)", text, re.S)
    front, body = m.group(1), m.group(2)
    if re.search(r"^program: ", front, re.M):
        continue
    blocks = [b for b in re.split(r"\n\s*\n", body.strip()) if b.strip()]
    start = next((i for i, b in enumerate(blocks) if re.match(r"^(?:#+\s*)?\*\*\s*THE PROGRAM\s*\*\*\s*$", b.strip())), None)
    if start is None:
        print(f.name, "- no program section")
        continue
    end = next((i for i in range(start + 1, len(blocks)) if re.match(r"^(?:#+\s*)?\*\*\s*ADMISSION\s*\*\*", blocks[i].strip())), len(blocks))
    program = "\n\n".join(blocks[start + 1:end]).strip()
    rest = blocks[:start] + blocks[end:]
    front = front.rstrip("\n") + "\n" + yaml_block("program", program).rstrip("\n")
    f.write_text("---\n" + front + "\n---\n\n" + "\n\n".join(rest).strip() + "\n", encoding="utf-8")
    print(f.name, "- program moved:", len(program.split()), "words; description now", len("\n\n".join(rest).split()), "words")
