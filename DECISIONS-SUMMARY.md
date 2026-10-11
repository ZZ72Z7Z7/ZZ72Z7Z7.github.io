# giovannifusetti.com: design decisions, 11 October 2026 (updated 261011)

**Site:** static Astro site for GitHub Pages. English and Italian. Black and white, red accents, Figtree type.

## 1 Foundation
- **Colour:** black on white. Logo red `#f00800` (logo, large type, dots, focus ring). Dark red `#b20000` for small red text, hover, selected text and buttons. Greys `#5f5f5f` and `#ddd`. No second accent colour.
- **Type:** Figtree. H1 40, H2 32, H3 24 (bold; phones 32, 24, 18). P1 18, P2 16, P3 14. Body line height 1.6. Menu 17px, sentence case.
- **Layout:** text column 44rem, wide pages 64rem, side margin 20px on phones, 40px above page titles and between sections, 18px between paragraphs, 120px below the last line. Banner rule: wider than text, inset.
- **Shapes:** square corners. Buttons red with white text. Dividers thin grey (red dots tried, reverted). Links black, underlined, red on hover. Red focus ring. Pale photos get a hairline frame (automatic).

## 2 Frame
- **Header:** logo and name left, menu right. Sticky on phones and tablets (not when held sideways). No line under it.
- **Menu:** About, Workshops, Events, Creations (Writings, Lectures, Shows, Blog), Gallery (Photo, Video), Contact. Dropdowns open on hover. Three-bar menu below 1024px.
- **Languages:** English and Italiano only (globe menu). Spanish, French, German removed.
- **Footer:** spiral and "©2026 Giovanni Fusetti", P2 grey.

## 3 Pages
- **Home:** photo, then the poem, centred. **About:** banner and first-person bio.
- **Workshops / Events:** same entry layout (picture left, text right), upcoming first, past below with greyscale thumbnails (colour on hover). Workshops past = year accordions; Events past = one list. Place line is P1 black. Taglines P2 grey italic (Workshops index: P1, grey, italic, 261011).
- **Workshop and event pages:** title, tagline, dates, place, picture, then sections (open on desktop, accordions on phones). Events: Description, Location, Admission, Tickets.
- **Application status chip (261011, workshops only, upcoming editions only):** a square white-on-colour chip in capitals: Pending grey, Open green, Waitlist blue, Closed black. Stack on list and workshop page: dates, location, chip, 24px gap, title, tagline, then button (list) or photo (page). On the list the chip stands alone; the italic line ("Applications open March 1", "Application date TBA", "Applications close April 30") appears only on the workshop page, below the chip. Waitlist and Closed have no line. Open turns Closed by itself after its deadline; the chip disappears when the workshop's dates pass. The DETAILS button on the Workshops list is solid red, capitals, no arrow, at the bottom of the row; phone order: title, dates, location, chip, photo, tagline, button..
- **Blog:** banner, then each post as a small `date · category` line, bold title, first paragraph.
- **Contact:** no title; mailing-list form and "Write to Giovanni:" form, centred.
- **Writings, Lectures, Shows:** entry lists in the same style; PDFs open in a new window; Lectures pictures one height; Shows newest first.
- **Index page titles centred.** 404: centred, red button home, small Italian line.

## 4 to 6
- **Components:** taglines and entry spacing unified (50px with pictures, 24px text-only). No back-to-top control.
- **Responsive:** no sideways scrolling at 375, 768, 1024. Tap targets 44px or more. Tablet pictures capped at 32rem.
- **Personality:** logo spins while pointed at; spiral above footer; red-dot bullets in text lists.

## Added later the same day
- **About menu is a dropdown:** Bio, The Pedagogy, The Pedagogy of the Red Nose Clown, The Roots, Helikos School.
- **Photo and Video:** titles hidden; Photo tiles are equal 4:3 pictures with the title over a 60% veil (red on hover); Video is a 2 x 3 grid of 16:9 thumbnails that play in a viewer; viewer arrows white, close button red.
- **Writings, Lectures, Shows:** entry lists in the Workshops style; PDFs open in a new window; Red Nose / Clown's Life text removed from Shows (to go in the past-workshops archive later).
- **Empty states:** "- no events currently scheduled -" / "- no workshops currently scheduled -", italic, with a red "Join the Mailing List" button.
- **25 workshop pages** now exist (20 added); old edition details cut, schedule and location kept; paragraph breaks added.
- **Italian:** a full draft by Claude is merged and marked as a draft; it needs human review (`ITALIAN-REVIEW.md`).
- **Typos fixed:** Bioenergetics, Troisième, Internationale, $20.00, Giovanni, Flu, Brunswick, Aldrovandi and others.

## On hold until the client has reviewed the design
The editor and its four forms, Web3Forms and Mailchimp wiring, the 70 redirects and final checks, the client handover note, and launch.

## Not yet live (you explain to the client)
Mailchimp signup and Web3Forms contact form; the editor (Pages CMS) and its forms; redirects for 70 changed addresses; GitHub repository and publishing; a human review of the Italian draft.

## On hold / open
- Some of the removed Red Nose / Clown's Life training text and photos go into the past-workshops archive later.
- Vector spiral (tabled).
- Later items: real alt text for pictures, hand-written page descriptions, the blog's paragraph breaks.
- Pedagogy of Bouffons, Bibliographic References, The Chorus in the City: not built until the client decides.
- Test on a real phone, both orientations, before launch.
