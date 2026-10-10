# Build brief: giovannifusetti.com rebuild

Prepared 7 October 2026. Read this whole file before writing any code. A companion file,
`migration-map.csv`, lists every page of the current site and where it goes in the new one.

## 1. What this project is

Giovanni Fusetti is a theatre pedagogue (clown, bouffon, mask, movement theatre) who teaches
workshops internationally. His current website runs on WordPress.com and has grown to 108 pages,
most of them near-duplicate workshop pages. A professional designer is rebuilding it. You are
working with the designer, who directs the design and makes the decisions; the designer is not a
programmer, so explain choices in plain language and keep the setup easy to maintain.

The goals, in priority order:

1. **The client can update three things himself, and nothing else:** the workshop schedule, the
   events schedule, and the blog. He is not technical and does not want to change design, layout
   or structure. Editing must happen in a browser through simple forms.
2. **Lowest possible running cost.** Free hosting and free tools wherever they are good enough.
3. **A simpler structure:** 108 pages become 66 (section 5).
4. **Fully bilingual, English and Italian,** with a language toggle on every page (section 6).
5. **Nothing is lost.** All existing text and media carry over, and old web addresses keep working.

## 2. Source material: the site archive

Everything on the current site was downloaded on 6 October 2026 into a folder called
`site-archive`. Ask the designer for its location. It is the only content source: the live site
may change or go offline, so do not fetch from it.

| In the archive | What it is |
|---|---|
| `INDEX.html` | Human-readable list of every page |
| `pages.csv` | Inventory: title, URL, section, published and modified dates, word count, image and PDF counts |
| `text/<slug>.md` | Each page's text as Markdown, with image links pointing into `media/` |
| `pages/<slug>.html` | Clean offline copy of each page (text plus images) |
| `html/<slug>.html` | Original HTML exactly as downloaded. Use it when the Markdown lost structure (galleries, columns, captions) |
| `media/YYYY/MM/…` | 463 files: 412 images, 48 PDFs, 2 videos, 1 audio file |
| `media/_other/…` | 32 images the old pages loaded from another site (helikos.com), and one video |
| `media-list.csv` | Every media file and the pages that use it |
| `video-links.csv` | Videos embedded from YouTube, Vimeo and VideoPress (links only) |
| `pdf-text/` | Text of each PDF |

`<slug>` is the page's URL path with slashes replaced by double underscores, for example
`/2020/05/31/why/` is `2020__05__31__why`, and the front page is `index`.

Rules for using it:

- **Copy the client's words exactly.** His writing is deliberate, including capitalisation, line
  breaks and verse layout (several pages and blog posts are poems). Do not rewrite, shorten,
  "improve" or correct it. If something looks like a typo, list it for the designer instead of
  fixing it.
- **Never invent content.** If something is missing, leave a clearly marked placeholder and report it.
- Do not commit the whole archive to the site repository. Copy in only the media the new site uses.

Known gaps in the archive:

- **Italian text.** The archive is the English site. It contains Italian only in two workshop pages
  and in some event descriptions written in both languages. The Italian version of everything else
  must come from another source; see section 6 and open decision 2.
- Two password-protected pages (Bibliography, Video Resources) were not captured; see open decisions.
- One PDF linked from The Storyteller page (`rules-of-engagement-2.pdf`) is missing on the live site itself.
- One PDF (`tao.du_.clown_.pdf`) is a scan with no extractable text. The file is present.
- A few links on the old Past Events and Past Workshops pages are malformed in the original. Fix or drop them and report which.

## 3. Recommended technical approach

These are defaults chosen for cost and simplicity. The designer may override them. Check each
tool's current documentation before relying on details below, because they change.

- **Static site in a GitHub repository.** A static site generator builds plain HTML from content
  files. Recommended default: Astro, with its content collections (each collection has a schema,
  which maps cleanly onto the editing forms). Eleventy is an acceptable alternative. No client-side
  framework and no database. Plain CSS.
- **Hosting: GitHub Pages**, deployed by a GitHub Actions workflow. Free for public repositories.
  Limits checked on 7 October 2026: published site up to 1 GB, repository recommended under 1 GB,
  100 GB per month soft bandwidth limit. The archive's media is about 230 MB, so it fits.
- **Editing: Pages CMS** (pagescms.org), free and open source. It gives the client a form-based
  editor in the browser and saves each change as a commit to the repository, which triggers a
  rebuild. Configuration lives in one file, `.pages.yml`, at the repository root. Editors can be
  invited by email without needing a GitHub account. Read the current Pages CMS documentation
  before writing the configuration.
- **Automatic republishing.** Each save by the client must rebuild and publish the site with no
  further step. Also schedule one rebuild per day, so that workshops and events move from
  "upcoming" to "past" on their own (see section 7).

## 4. What the client edits

Expose exactly these four forms in the editor, with plain-language labels and help text. Hide
everything else. Each entry is entered once and holds both languages: text fields come in pairs
(English, Italian), while dates, places, images and links are shared.

1. **Workshop schedule entry** (one scheduled run of a workshop)
   - Workshop (choose from the list of workshops; optional, because some old entries have no page)
   - Title, used only when no workshop is chosen
   - Start date and end date
   - Extra dates text, for entries with two date ranges
   - City, country, venue
   - Taught with (co-teachers), in collaboration with (partner name and link)
   - Language note (for example "in Italian")
   - External link, when registration or details live on another site
   - Image
2. **Workshop** (the description page for a workshop; needed only when he offers a new one)
   - Title, subtitle, description (rich text), images, practical information
3. **Event** (performances, lectures, showings)
   - Title, subtitle, start date and time, end date, city, venue and address
   - Description (rich text). Many old events mix Italian and English in one text; separate them into the two language fields
   - Poster image, admission, booking link or email, attached PDFs
4. **Blog post**
   - Title, date, category (existing categories: Pedagogy, Poetry, Philosophy), body, image, audio file

Field lists are a starting point. Confirm them against the real content while migrating, and tell
the designer about anything on the old pages that does not fit.

## 5. Structure

Current site: 108 pages, 10 menu items. New site: 66 pages, each in English and Italian, with
7 menu items (Home, About, Workshops, Events, Creations, Blog, Contact) and a language toggle.

```
Home                                  front page and Welcome page combined
├─ About                              the Bio page
│   ├─ Pedagogy
│   ├─ The Pedagogy of the Red Nose Clown
│   ├─ Pedagogy of Bouffons           (open decision 3)
│   ├─ The Roots
│   └─ Bibliographic References       (open decision 3)
├─ Workshops                          schedule: upcoming first, archive below   [client edits]
│   ├─ 27 workshop pages              one per workshop                          [client edits]
│   └─ Helikos School
├─ Events                             upcoming first, past below                [client edits]
├─ Creations                          existing page, used as the menu landing page
│   ├─ Writings                       12 PDFs
│   ├─ Lectures                       8 PDFs
│   ├─ Shows
│   ├─ Photos                         4 gallery pages (open decision 5)
│   └─ Videos
├─ Blog                               17 posts                                  [client edits]
└─ Contact

Language toggle (English / Italian) on every page. It replaces the old "Italiano" menu link.
```

Page counts by section: Home 1, About 6, Workshops 29, Events 1, Creations 10, Blog 18, Contact 1.

**`migration-map.csv` is the page-by-page authority.** It has one row for each of the 108 old
pages: old URL and title, action, new URL, new page, workshop and edition, the archive files to
read, and notes. Actions:

| Action | Rows | Meaning |
|---|---|---|
| `keep` | 36 | Same URL, content carried over |
| `move` | 17 | One old page becomes one new page at a new URL |
| `merge` | 50 | Several old pages combine into one new page |
| `retire` | 3 | Page removed; old URL redirects to the stated page |
| `hold` | 2 | Waiting on a decision; do not build yet |

### The main consolidation: workshops

Today each run of a workshop has its own page: 61 pages for 27 workshops (The 20 Movements of
Jacques Lecoq has 6, Red Nose Intensive, The Tao of Clown and The Greenhouse of Fools have 5 each).
In the new site:

- Each workshop gets **one page** at `/workshops/<slug>/` holding its description.
- Each run becomes a **schedule entry** (dates, city, venue, collaborators) linked to that workshop.
- The Workshops page lists upcoming entries, then the archive by year. Each workshop page lists its
  own upcoming and past runs.

When merging edition pages into one workshop page:

- Use the most recently modified edition page as the base text (`modified` column in `pages.csv`).
- Move per-edition details (dates, place, fees, registration, collaborators, edition-specific
  images) into schedule entries. Do not blend descriptions from different editions.
- If older editions contain substantial text the newest lacks, do not drop it silently. List those
  cases for the designer.
- Two old pages are Italian-language versions (I 20 Movimenti di Jacques Lecoq, Il Coro e la
  Città). Use each as the Italian version of its workshop page, not as part of the English text.
- Read exact dates from `text/workshops.md` and `text/past-workshops.md`.
- The old Past Workshops page also lists 21 runs (2018 to 2020, and four later ones) whose links go
  to other websites. Keep each as a schedule entry with its external link and no workshop page.

## 6. Two languages

The new site is fully bilingual. This replaces the old arrangement, where an "Italiano" menu item
linked to a separate, older website.

- **Addresses.** English stays at the root, so existing English URLs do not change. Italian pages
  live under `/it/` with the same path, for example `/workshops/` and `/it/workshops/`. Keeping
  the paths identical makes the toggle a simple swap. Translated Italian paths are optional and
  only worth doing if the designer asks.
- **Toggle.** Every page links to the same page in the other language, never to the other
  language's home page. Mark each page's language in the HTML and declare the two versions as
  alternates of each other for search engines.
- **Everything visible is translated:** menu labels, buttons, headings such as "Upcoming" and
  "Past", date formats, the 404 page and image descriptions.
- **Client entries.** Each form entry holds both languages (section 4). If the Italian field of
  an entry is empty, the Italian page shows the English text, so a half-filled entry never
  produces an empty or broken page. Report which entries are relying on this.
- **Source of Italian text.** Do not machine-translate the client's writing on your own
  initiative, and never present a machine translation as his text. Use Italian text supplied by
  the designer or client. Where none exists yet, build the Italian page with the English text in
  place and list it as awaiting Italian. If the designer asks for draft translations, label them
  as drafts for the client's review.
- **Order of work.** Build the English site and the language structure first, then fill in
  Italian as text arrives. The language toggle and `/it/` pages should exist from the first draft.

## 7. Behaviour requirements

- **Upcoming and past sort themselves.** An entry is upcoming until its end date has passed, then
  appears under past. The client never moves anything by hand. The daily scheduled rebuild keeps
  this current.
- **Old addresses keep working.** 70 old URLs change (listed in the map wherever `new_url` differs
  from `old_url`). GitHub Pages serves static files only and has no server-side redirect rules, so
  generate a small redirect page at each old path (meta refresh plus a canonical link to the new
  URL). If the designer chooses a host that supports real redirects, use those instead.
- **Media stays at its original address.** Publish files from `media/YYYY/MM/…` at
  `/wp-content/uploads/YYYY/MM/…`, the path they have today, so existing outside links to images
  and to the 48 PDFs continue to work.
- **Rewrite internal links.** Old pages link to each other with full addresses, some on an older
  hostname (`helikos737982018.wordpress.com`). Point every internal link at the new URL.
- **Self-host the helikos.com images.** The 32 images in `media/_other/` were loaded from another
  site that may disappear. Serve them from this site.
- **Videos** stay as embeds from YouTube and Vimeo. The two saved video files and the audio file are served locally.
- **Basics:** responsive layout, accessible markup, descriptive page titles, meta descriptions
  taken from the old pages, a generated `sitemap.xml`, and a helpful 404 page.

## 8. Design

The designer supplies the visual direction in the session. Do not invent a visual identity, colour
palette or typography on your own. Until direction is given, build with clean semantic HTML and
minimal neutral styling so that structure and content can be reviewed.

The first thing the designer needs is a **rough draft to show the client**. Aim the first working
version at these page types, with real content: Home, Workshops, one workshop page, Events, one
blog post, About.

## 9. Order of work

Stop for the designer's review at the end of each step.

1. Confirm the open decisions in section 10 and the technical defaults in section 3.
2. Scaffold the repository, build and deploy workflow, and a preview address.
3. Build the page types and the content model with a small sample of real content. This is the draft for the client.
4. Migrate all content following `migration-map.csv`.
5. Configure the editor with the four forms, and test each one end to end as the client would use it.
6. Generate redirects and run the checks in section 11.
7. Launch. Pointing the domain at the new site is the designer's and client's step. Do not change
   domain or DNS settings, and leave the WordPress site untouched.

## 10. Open decisions

Ask the designer. Defaults are stated so work is not blocked.

1. **Password-protected pages** (Bibliography, Video Resources). Their content must come from the
   client. This kind of hosting cannot password-protect a page. Default: leave them out and report.
2. **Source of the Italian text.** The archive has almost none. Options: the client writes or
   supplies it, it is taken from the old Italian website (which has not been archived), or it is
   translated. Default: build with English in place and list every page awaiting Italian.
3. **Pedagogy of Bouffons and Bibliographic References** are unlinked today. Default: publish under About.
4. **The Chorus in the City** (English and Italian pages, unlinked today). Default: one workshop page, the 27th.
5. **Photos:** four gallery pages or one combined page. Default: four.
6. **Contact:** a form needs an outside form service. Default: show the email address and the existing mailing-list link, with no form.

## 11. Checks before calling it done

- All 108 old URLs in `migration-map.csv` resolve: to a page, or to a redirect that lands on the right page. The two `hold` rows are reported, not guessed.
- The built site has the 66 pages in section 5 in each language, give or take the open decisions.
- The language toggle on every page leads to the same page in the other language, and back.
- A list exists of every page and entry still showing English text on the Italian side.
- Every image, PDF, video and audio file referenced by a page loads from this site. No page loads media from the old site.
- No link points to the old hostname or to a retired URL.
- Word counts of migrated pages are close to `pages.csv`. Explain any page that shrank.
- Upcoming and past lists are correct for today's date, and for a test date in the future.
- Each of the four forms was used to add, edit and remove a test entry, and the site republished without help.
- A short handover note for the client exists, in plain language: how to add a workshop date, an event and a blog post.

## 12. Report back

At each review point, give the designer: what was built, what was not and why, content problems
found (missing files, text that did not fit the model, suspected typos), and decisions needed.
Report failures plainly.
