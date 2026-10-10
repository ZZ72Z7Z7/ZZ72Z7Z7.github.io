# Demo draft (build 261007): what was built and what needs a decision

## Built
Home, About, Creations (landing text only), Workshops (schedule), one workshop page (Red Nose Intensive),
Events, Blog index + all 17 posts, Contact (with placeholder forms), 404 page. Each in English and Italian
(`/it/`), 50 pages + 404. Neutral styling, mobile-friendly. Both language versions have a toggle on every page.

Sample content: 21 workshop dates (5 upcoming, 16 past), 4 events, 17 posts, all real text from the archive.

## Not built yet (links to these go to the 404 page)
Pedagogy, The Roots, Writings, Lectures, Shows, Photos (4 galleries), Videos, the other 25 workshop pages,
Helikos School. Contact and mailing-list forms are placeholders (do not send).

## Decisions recorded
Password-protected pages, Italian text, Pedagogy of Bouffons, Bibliographic References, The Chorus in the City
as per your answers. Photos: four galleries. Forms: Web3Forms (contact) and Mailchimp (signup), placeholders for now.

## Content problems found (not fixed; the client's words are untouched)
- Probable typos in the source: "$20:00" (MIMI admission); "Giovann Fusetti" (Depressed Clown PDF label);
  "Phisiosophy" (old category name; the site uses "Philosophy" as in the brief); "Flue" (Spanish Flu, blog post
  On Contact and Contagion); "my been pedagogic work ... the the most" (Creations); "get in touch out via email" (Contact);
  "MAKE A MEGA FUN AGAIN" looks like a deliberate play on words and is kept.
- A blog post links to `/2020/03/31/why/`, an address that does not exist (the post is `/2020/05/31/why/`). Same on the old site.
- Blog tagline "...in order to surviv|e": the final "e" sits outside the italics in the original; copied as is.
- Several post and page titles are typed in capitals in WordPress (e.g. THE PEDAGOGY OF THE POETIC BODY); kept as typed.
- The old meta descriptions are auto-generated excerpts (e.g. "November, 1→ 28, 2026Padova, ITALY RED NOSE..."),
  not written by hand. Not used in the demo: needs a decision (write short ones, or use each page's first sentence).

## Where the model does not fit the old pages
- Red Nose Intensive page still contains per-edition details (selection date June 15, deposit EURO 700, tuition,
  enrolment status as of September 1st 2026, weekly schedule). The brief says these belong with the dated entry; the
  schedule entry has no field for them. Needs a decision: a "practical information" field on the schedule entry,
  or keep them in the workshop text.
- Upcoming workshops without a page yet show only their title; their subtitles (e.g. "From Pantomime to Bandes Mimées")
  will appear once their workshop pages are built.
- The MIMI event carries the introduction that actually covers both Boulder shows (MIMI and MAKE A MEGA FUN AGAIN).
- Events: the "Depressed Clown" PDF labels exist only in Italian, so they show in Italian on both sides.
- Home: the splash "Enter" button and the Italian flag block were dropped (replaced by the language toggle). The old
  flag linked to a separate Italian site (helikos.com/index.php?lang=it) that has not been archived. The sentence
  "Scrolling down this home page you will find a map of the site" is kept, so a simple list of links stands in for the old map.
- Heading levels: the old pages use small headings (h4) straight under the page title. Left as is; to tidy later.

## Italian
Everything on the Italian side currently shows English text, marked "Questo testo è in inglese…", except: the menu and
interface words (my Italian, for review), The Holy Fool and The Depressed Clown (Italian text taken from the old event pages).
List of pages awaiting Italian = every page except those two events.

## Hosting note
For the demo, use a GitHub repository named `<your-username>.github.io` (the site is built for the root of its address).
A repo with another name would put the site under `/<repo-name>/` and break links.
