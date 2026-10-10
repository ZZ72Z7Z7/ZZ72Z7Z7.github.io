#!/usr/bin/env python3
"""Demo import, part 2: one workshop page (Red Nose Intensive) and its schedule entries."""
import re, json, shutil, sys
sys.path.insert(0, str(__import__('pathlib').Path(__file__).parent))
import import_demo as base
from import_demo import read, rewrite, write, fm, CONTENT, ARCHIVE, UPLOADS

# Base text = most recently modified edition page (2026). Header block (dates, place,
# title, subtitle) moves into the schedule entry and the page's title/subtitle fields.
meta, body = read("red-nose-intensive-2026")
i = body.index("poster.2024.web_.jpg")
body = body[body.rfind("\n", 0, i) + 1:]     # start at the poster image; the header above it moves to the schedule entry
write(
    "workshops/red-nose-intensive.md",
    fm(
        title="Red Nose Intensive",
        subtitle="A unique opportunity to train and practice\nAt the essence of Theatre Clown\nand at the roots of Physical Comedy",
    ),
    rewrite(body),
)
