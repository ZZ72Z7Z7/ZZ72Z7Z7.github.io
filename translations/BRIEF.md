# Italian draft translation of giovannifusetti.com (brief for translators)

**What this is.** The English text of Giovanni Fusetti's website, to be translated into Italian as a **draft that a human will review before launch**. Giovanni is a theatre pedagogue
(clown, bouffon, mask, movement theatre) who teaches internationally. His writing is deliberate: it keeps its capitalisation, line breaks and verse layout. Translate; do not improve,
shorten, explain or add. If the English is odd or looks like a typo, translate the intended meaning and list the doubt under `=== notes ===`.

**Where things are.** English sources: `translations/source/<category>/<file>`. You write Italian outputs to `translations/it/<category>/<same file name>` (create the folder if missing).
Never edit anything else. The file list for your job is in your instructions.

## Voice
- First-person pages stay first person ("I practice the freedom to be stupid" -> "Pratico la libertà di essere stupido"). Warm, direct, poetic where the English is; never bureaucratic.
- Address the reader with the plural imperative ("voi") as on his existing Italian pages ("Inviate una lettera di motivazione", "potete contattare"). Never "Lei".
- Natural, idiomatic Italian, not word for word. Keep the register (a joke stays a joke, a solemn line solemn).
- Poems: keep every line break and stanza break; translate for meaning and rhythm; rhyme only if the English clearly rhymes and Italian allows it naturally.

## Keep exactly as in the source
- All Markdown and HTML: `**bold**`, `*italic*`, `#` headings, `<br>`, tags and their attributes, blank lines, **two trailing spaces at line ends (a line break)**, list markers, image lines `![](...)`.
- URLs, email addresses, phone numbers, file names, prices and currency signs, numbers, times ("9:30 – 17:30").
- Link text: translate it, except proper names. Link addresses never change.
- Proper names: people, organisations, venues, schools (Helikos, Pig Iron School, Naropa University...), titles of workshops, shows, books, articles, films and festivals (translate nothing inside titles), quoted passages already in French or Italian.
- Place names take the Italian form where one exists (Padua -> Padova, Florence -> Firenze, Venice -> Venezia, New Zealand -> Nuova Zelanda, Slovenia, Finland -> Finlandia, Norway -> Norvegia, Germany -> Germania, Australia, USA); others stay (Melbourne, Boulder, Philadelphia, Auckland).
- Dates in running text use Italian style ("11 giugno 2026", "dal 23 al 28 febbraio"); weekday and month names in Italian.
- Typographic quotes “ ” and the apostrophe ’ as in the source.

## Glossary (use consistently)
| English | Italian |
|---|---|
| Red Nose (the mask) / Red Nose Clown | Naso Rosso / il Clown del Naso Rosso |
| Clown, Clown State | Clown, Stato del Clown |
| Bouffon / Bouffons | Bouffon (invariable plural: i Bouffon) |
| Fool | Folle |
| Neutral Mask | Maschera Neutra |
| Commedia dell’Arte, Zanni, lazzi, half-masks | unchanged; mezze maschere |
| movement theatre / movement-based theatre | teatro di movimento |
| Actor-Creator | Attore-Creatore |
| pedagogy / pedagogue | pedagogia / pedagogo |
| devising / to devise | creazione collettiva / ideare (use "devising" in italics only if no natural Italian fits) |
| workshop, masterclass, seminar | workshop, masterclass, seminario |
| training | formazione (or "training" when it is the standing term) |
| play / state of play(ing) | gioco / stato di gioco |
| awareness | consapevolezza |
| poetic body | corpo poetico |
| Lecoq pedagogy | pedagogia di Jacques Lecoq |
| mimodynamic | mimodinamico |
| Process Work, Gestalt, Reichian Analysis, Bioenergetics, Taoism | unchanged / Analisi Reichiana, Bioenergetica, Taoismo |
| participants | partecipanti |
| the page "Details", "Tickets" etc. | (interface labels are done elsewhere; do not translate them) |

## Output format (sectioned files)
A file is a list of sections. A section starts with a line exactly `=== name ===` and runs to the next one. Write only the sections present in the source, in the same order, plus a final `=== notes ===`.
- `=== notes ===`: short bullet lines (`- ...`) for the human reviewer: unsure passages, wordplay you could not keep, terms you chose, suspected typos in the English. If none: `- none`.
- Numbered sections (`gallery_captions`, `pdf_labels`): keep the numbers, one item per line, `1: text`.
- Blog posts and workshops: `body` is the whole body, Markdown intact.
- Pages: the output is the **whole Markdown file** including the front matter (translate `title`; keep `description` translated if present; no other keys).
- `schedule/_taglines.tsv`: tab-separated, `file<TAB>Italian tagline`; same file names, same order, one per line.
Do not wrap lines, do not add commentary outside `=== notes ===`.
