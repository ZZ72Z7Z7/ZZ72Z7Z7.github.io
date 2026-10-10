#!/usr/bin/env python3
"""Demo import, part 3: sample schedule entries and events. Dates and names are taken
from text/workshops.md, text/past-workshops.md and text/upcoming-events.md."""
from pathlib import Path
import re
from yamlish import dump

ROOT = Path(__file__).resolve().parent.parent
SCHED = ROOT / "src/content/schedule"
EVENTS = ROOT / "src/content/events"
SCHED.mkdir(parents=True, exist_ok=True)
EVENTS.mkdir(parents=True, exist_ok=True)
for f in list(SCHED.glob("*.yml")) + list(EVENTS.glob("*.md")):
    f.unlink()

def slugify(s):
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

AU = ("Melbourne", "Australia")
S = []
def add(title, start, end, city, country, workshop=None, **kw):
    S.append(dict(title=None if workshop else title, workshop=workshop, start=start, end=end,
                  city=city, country=country, **kw))

# --- upcoming (text/workshops.md)
add("The Language of Gestures", "2026-10-19", "2026-10-24", "Padova", "Italy")
add("Red Nose Intensive", "2026-11-01", "2026-11-28", "Padova", "Italy", workshop="red-nose-intensive", venue="Helikos Studio")
add("Famiglia dell’Arte", "2027-01-18", "2027-01-22", *AU, taught_with="Zsófi Kigyóssy")
add("Bouffon Intensive", "2027-02-08", "2027-03-07", *AU)
add("Bring Your Own Psyche", "2027-03-15", "2027-03-18", *AU, taught_with="Zsófi Kigyóssy")
# --- past (text/past-workshops.md)
add("The Language of Gestures", "2026-08-10", "2026-08-15", "Boulder, Colorado", "USA")
add("Personality dell’Arte", "2026-03-23", "2026-03-27", *AU, taught_with="Zsófi Kigyóssy")
add("The Tao of Clown", "2026-03-11", "2026-03-14", "Wellington", "Aotearoa, New Zealand")
add("The Storyteller", "2026-02-23", "2026-02-28", *AU)
add("The Language of Gestures", "2026-02-16", "2026-02-20", *AU)
add("Conversations with the Fools", "2026-02-09", "2026-02-13", *AU)
add("The Tao of Clown", "2025-09-15", "2025-10-03", "Boulder, Colorado", "USA",
    extra_dates="September 15 → 19, 2025\n&\nSeptember 29 → October 3, 2025")
add("The Greenhouse of Bouffons", "2025-09-01", "2025-09-06", "Boulder, Colorado", "USA")
add("Personality dell’Arte", "2025-08-11", "2025-08-15", "Boulder, Colorado", "USA")
add("The Spirit of Commedia dell’Arte", "2025-07-26", "2025-07-27", "Philadelphia", "USA",
    collaboration_name="PIG IRON SCHOOL",
    collaboration_url="https://pigiron.org/school/workshops/the-spirit-of-commedia-dell-arte/")
add("The Pedagogic Journey", "2025-03-24", "2025-06-14", "Padova", "Italy")
add("Pedagogic Supervision Group", "2025-02-08", "2025-02-09", *AU)
add("Red Nose Intensive", "2024-10-13", "2024-11-09", "Padova", "Italy", workshop="red-nose-intensive")
add("Red Nose Intensive", "2023-10-02", "2023-10-28", "Padova", "Italy", workshop="red-nose-intensive")
add("Red Nose Intensive", "2023-05-14", "2023-06-10", "Padova", "Italy", workshop="red-nose-intensive")
add("Red Nose Intensive", "2022-05-15", "2022-06-10", "Padova", "Italy", workshop="red-nose-intensive")

for e in S:
    name = f"{e['start']}-{slugify(e['title'] or e['workshop'] or 'entry')}"
    if e.get("workshop") is None and e.get("title") is None:
        raise SystemExit("entry without title")
    (SCHED / f"{name}.yml").write_text(dump(e), encoding="utf-8")
print(len(S), "schedule entries")

# ------------------------------------------------------------------ events
def event(name, front, body, body_it=None):
    front = dict(front)
    if body_it:
        front["body_it"] = body_it
    text = "---\n" + dump(front) + "---\n\n" + body.strip("\n") + "\n"
    (EVENTS / f"{name}.md").write_text(text, encoding="utf-8")

BCC = dict(city="Boulder", country="Colorado, USA", venue="Boulder Circus Center",
           address="4747 26th St, Boulder, CO 80301", admission="sliding scale, $10.00 – $20:00")

event("2026-08-22-mimi",
      dict(title="MIMI", subtitle="created and performed by Joshua Kilcoyne", start="2026-08-22", time="19:00",
           image="/wp-content/uploads/2026/08/mimi_boulder_1x1.jpg",
           booking_link="https://events.humanitix.com/mimi-bcc", **BCC),
      """After the two **Bouffon Intensive Training*s*** in ***2022*** and ***2024***, a group of players has returned to Boulder to develop their work during a devising week, ***[The Greenhouse of Bouffons](/workshops/greenhouse-of-bouffons/),*** in September 2025. Two of the pieces presented at the end of the week have developed further into two full shows. Giovanni Fusetti is involved in the development of these pieces in the role of a devising consultant  
The two shows have already been presented in various venues and are returning to Boulder for a further work of refining with Giovanni and will be presented in two public performances.

*MIMI is a strange and enchanting birdlike creature with an insatiable appetite for the beautiful, exceptional, and rare. Each performance serves as an elaborate mating ritual between audience and performer as MIMI struts and serenades through a virtuosic demonstration of why nothing in life is more important than being special.*

**Duration**: approximately 90 min

Given the limited seats available, it is necessary to book your seat in advance on [**https://events.humanitix.com/mimi-bcc**](https://events.humanitix.com/mimi-bcc)

All contribution will go to the artist as a funding towards the production of the show.

ALERT ! The performance contains adult language, explicit sexual material, and provocative subjects, so it is not suitable for a young audience.""")

event("2026-08-29-make-a-mega-fun-again",
      dict(title="MAKE A MEGA FUN AGAIN", subtitle="a psycho-sexual Bouffon Fever Dream", start="2026-08-29", time="19:30",
           booking_email="giovanni.fusetti@helikos.com", **BCC),
      """created and performed by  
Lia Tamborra & Eric Davis

*Join our Bouffons Eric Davis and Lia Tamborra as they suck the ooze of tyranny,  
and secrete the glory drunk goo of populism.*

**Duration**: approximately 90 min

It is possible to pay via **VENMO** to **[LIA TAMBORRA](https://venmo.com/u/Lia-Tamborra)**, or in cash at the venue.

Given the limited seats available, it is necessary to book your seat in advance sending an email to [**giovanni.fusetti@helikos.com**](mailto:giovanni.fusetti@helikos.com)

All contribution will go to the artists as a funding towards the production of the show.

ALERT ! The performance contains adult language, explicit sexual material, and provocative subjects, so it is not suitable for a young audience.

**WHO ARE THE BOUFFONS ?**  
The essence of Bouffon is to mock: it’s a specific role, existing in all human societies.  
Bouffons will mock the world in which we live, with their ruthless and ecstatic instinct to expose the collective games that humans like to play.  
Bouffons represent elements of the society in an amplified, exaggerated, ecstatic way, therefore provoking laughter and outrage. Their essence is in being an amplified mirror of the society, revealing its complexity, its contradictions, its shadows and, ultimately, its underlying folly, made of an ever-shifting combination of the many facets of the human condition.""")

event("2026-06-20-the-holy-fool",
      dict(title="THE HOLY FOOL", title_it="IL SANTO FOLLE",
           subtitle="A spiritual physical-comedy about a Fool who ended up becoming a Saint.",
           subtitle_it="Una commedia fisica e spirituale sulla storia di un Folle che si è ritrovato Santo.",
           start="2026-06-20", time="19:30", city="Padova", country="Italy", venue="HELIKOS STUDIO",
           address="Via Monte Solarolo 16/A, 35141 PADOVA – ITALY",
           image="/wp-content/uploads/2026/06/holy.fool_.1.png",
           admission="Regular: 10 Euro\nSupporter: you choose the amount",
           admission_it="Intero: 10 Euro\nSostenitore: scegli l’ammontare",
           booking_email="scuola@helikos.com"),
      """with  
**FABIO MOTTA**

Direction  
**GIOVANNI FUSETTI**

*In 2026, chaos reigns! Battles boom, pockets deepen, and Mother Nature feels forgotten.  
What if we already KNEW the secret to attaining world harmony but somehow have forgotten?  
Inspired by the story of Saint Francis of Assisi, The Holy Fool leaps between the divine and the ridiculous, exploring how foolishness can conjure the greatest of all miracles…  
Blending physical comedy, spiritual longing, and joyful absurdity, this show follows one naïve seeker determined to live with purpose, love boldly, and question everything — even holiness itself.  
A playful pilgrimage through fear, belonging, and the urge to matter in a fractured world. A sacred comedic journey towards meaning, compassion, and the courage to be unapologetically human.*

*The show is in English*

**Duration**: 80 minutes, followed by a conversation with the artists

Places are limited and **reservations via email are necessary**  
In the reply to your reservation email you will receive a link to send the donation to Helikos-APS.""",
      """con  
**FABIO MOTTA**

Regia  
**GIOVANNI FUSETTI**

E’ il 2026, regna il caos! Le battaglie esplodono, le tasche si riempiono, e Madre Natura sembra dimenticata.  
E se già CONOSCESSIMO il segreto per raggiungere l’armonia mondiale ma in qualche modo lo avessimo dimenticato?  
Ispirato dalla storia di San Francesco d’Assisi, *Il Santo Folle* e’ un viaggio tra il divino e il ridicolo, esplorando come la follia possa evocare il più grande di tutti i miracoli…  
Unendo comicità fisica, desiderio spirituale e gioiosa assurdità, questo spettacolo segue l’itinerario di un cercatore, inspirato e naive, determinato a vivere con uno scopo, amare con coraggio e mettere in discussione tutto — persino la santità stessa.  
Un pellegrinaggio giocoso attraverso la paura, l’appartenenza e l’urgenza di agire in un mondo frammentato. Un viaggio comico e sacro alla ricerca di significato, di compassione e del coraggio di essere radicalmente umani.

Lo spettacolo è in lingua Inglese.

**Durata**: 80 minuti, seguiti da una conversazione con l’attore e il regista.

I posti sono limitati ed **è necessario prenotarsi via email.**  
Al momento della prenotazione verrà inviato il link per effettuare il pagamento del Contributo all’Associazione Helikos-APS.""")

event("2026-05-14-the-depressed-clown",
      dict(title="THE DEPRESSED CLOWN", title_it="IL CLOWN IN DEPRESSIONE", start="2026-05-14", end="2026-05-16",
           city="Padova", country="Italy", image="/wp-content/uploads/2026/05/depression_a3_2026.jpg",
           pdfs=[dict(label="LIBRETTO DI SALA (in Inglese)", file="/wp-content/uploads/2026/05/depression.programme.2026.pdf"),
                 dict(label="Note di Regia di Giovann Fusetti (In Italiano)", file="/wp-content/uploads/2026/05/note-diregia.pdf")]),
      """with  
**KNUT OSTRADAL & GIOVANNI FUSETTI**

*A clown and ten puppets  
in the journey to the dark land of depression and beyond  
Based on the true story of the author  
The theatrical story of a journey at the edge between tragedy and comedy  
Following the archetypal figure of the Fool  
on the footsteps of these questions…*

*Is there music in the land of depression?  
Can we sing while we are drowning in sadness?  
Can we laugh at the edge of the abyss?  
Or at least smile ?*

*The show will be followed by a conversation with the authors/players  
about the relationship between humor and healing  
and the role of comic archetypes in the world of mental health.*

*The show is in English*

Script: **KNUT OSTRADAL**  
Devised by: **KNUT OSTRADAL** and **GIOVANNI FUSETTI**  
Director: **GIOVANNI FUSETTI**  
Scenography: **GABRIELA MELO LARSEN**  
Puppets: **TATJANA ZAITZOW**  
Actor: **KNUT OSTRADAL**  
Puppeteer: **GIOVANNI FUSETTI**""",
      """con  
**KNUT OSTRADAL & GIOVANNI FUSETTI**

Un clown e dieci burattini  
in un viaggio nella terra oscura della depressione e al di là.  
Tratto dalla storia vera dell’autore  
il racconto teatrale di un viaggio al confine tra il tragico e il comico.  
Seguendo la figura archetipica del Folle  
sulle tracce di queste domande…

Ci può essere musica nel mondo della depressione?  
Possiamo cantare mentre anneghiamo nella tristezza?  
Possiamo ridere al limite dell’abisso?  
O almeno sorridere?

Lo spettacolo sarà seguito da una conversazione con gli autori/attori  
sul tema della relazione tra umorismo e guarigione  
e sul ruolo degli archetipi comici nei percorsi della salute mentale.

Lo spettacolo è in lingua Inglese.

Soggetto: **KNUT OSTRADAL**  
Creazione di: **KNUT OSTRADAL** and **GIOVANNI FUSETTI**  
Regia: **GIOVANNI FUSETTI**  
Scenografia: **GABRIELA MELO LARSEN**  
Burattini: **TATJANA ZAITZOW**  
Attore: **KNUT OSTRADAL**  
Burattinaio: **GIOVANNI FUSETTI**""")
print("4 events")
