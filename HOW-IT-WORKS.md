# How this site is built (plain-language notes)

**What it is.** A static website for giovannifusetti.com. The content lives in plain text files;
a free tool called Astro turns them into ordinary web pages. Visitors only ever see the finished pages.

## Folder map

| Folder / file | What it holds |
|---|---|
| `src/content/` | All the writing and data: `workshops/`, `schedule/` (one file per workshop date), `events/`, `blog/`, `pages/` (Home, About, Creations, Contact) |
| `src/views/`, `src/components/`, `src/layouts/` | Page layouts, written once, used for every page |
| `src/styles/global.css` | Placeholder styling (neutral; design not chosen yet) |
| `src/i18n/ui.ts` | Menu labels and other interface words in English and Italian |
| `public/wp-content/uploads/` | Images and PDFs, at the same addresses as on the old site |
| `dist/` | The finished site, ready to open or upload. Rebuilt every time; not committed to GitHub |
| `tools/` | Scripts that import content from the site archive (used during the migration only) |
| `.github/workflows/deploy.yml` | Tells GitHub to build and publish the site automatically |
| `BUILD-BRIEF.md`, `migration-map.csv` | The brief and the page-by-page map |

## Languages
English pages live at the root (`/workshops/`); Italian pages at `/it/` (`/it/workshops/`).
In content files, Italian text goes in a field with the same name plus `_it` (for example `title_it`,
`body_it`). When the Italian field is empty, the Italian page shows the English text with a short notice.

## Upcoming and past
Workshops and events are "upcoming" until their end date has passed. GitHub rebuilds the site every
day at 03:30 UTC, so entries move to "past" by themselves. To test another date:
`SITE_TODAY=2026-08-01 npm run build`.

## Publishing
Push from GitHub Desktop. GitHub then builds the site and publishes it on GitHub Pages
(Settings → Pages → Source: "GitHub Actions", set once). Until launch the workflow marks the site
"noindex" so search engines ignore the demo; see the comment at the top of `deploy.yml`.

## If you ever need to rebuild by hand
Install Node.js 22 or newer, then in this folder: `npm ci`, then `npm run build`. The result is in `dist/`.
The dated backup folders under `BUILDS/` each contain everything needed except `node_modules/`.

## Tools used (all free)
Astro (builds the site), marked (turns Markdown text into HTML), turndown and linkedom (import only),
GitHub Pages (hosting), GitHub Actions (automatic builds), Pages CMS (the client's editing forms, step 5),
Web3Forms and Mailchimp (the two forms, wired up after the demo).
