// Converts the main content of an archived page (html/<slug>.html) to clean Markdown.
// Usage: node tools/html_to_md.mjs <slug>
// Used because the archive's own Markdown loses structure in places (nested emphasis,
// spacing around bold/italic). Words, line breaks and verse layout are kept as written.
import { readFileSync } from 'node:fs';
import { parseHTML } from 'linkedom';
import TurndownService from 'turndown';

const slug = process.argv[2];
const archive = new URL('../../../WORDPRESS/site-archive/', import.meta.url);
const html = readFileSync(new URL(`html/${slug}.html`, archive), 'utf8');
const { document } = parseHTML(html);

const root = document.querySelector('.entry-content');
if (!root) { console.error(`no .entry-content in ${slug}`); process.exit(1); }

// WordPress furniture that is not the author's content.
for (const sel of ['.sharedaddy', '#jp-relatedposts', '.wp-block-spacer', 'script', 'style', 'noscript', '.wp-block-buttons.splash-enter']) {
  root.querySelectorAll(sel).forEach((n) => n.remove());
}

// Tidy emphasis so the Markdown comes out clean:
// - an emphasis tag inside the same tag (<strong><strong>x</strong></strong>) collapses to one;
// - a line break at the very start or end of an emphasis tag moves outside it.
const EMPH = ['strong', 'b', 'em', 'i'];
const kind = (n) => ({ b: 'strong', i: 'em' }[n.localName] ?? n.localName);
for (const el of [...root.querySelectorAll(EMPH.join(','))]) {
  if (!el.parentNode) continue;
  let p = el.parentNode;
  while (p && p !== root) {
    if (EMPH.includes(p.localName) && kind(p) === kind(el)) {
      while (el.firstChild) el.parentNode.insertBefore(el.firstChild, el);
      el.remove();
      break;
    }
    p = p.parentNode;
  }
}
const isBlank = (n) => n && ((n.nodeType === 3 && !n.textContent.trim()) || n.localName === 'br');
for (const el of root.querySelectorAll(EMPH.join(','))) {
  while (isBlank(el.lastChild) && el.lastChild.localName === 'br') el.after(el.lastChild);
  while (isBlank(el.firstChild) && el.firstChild.localName === 'br') el.before(el.firstChild);
}

// Two neighbouring tags of the same kind (<em>The</em> <em>Boulder</em>) become one.
for (const el of [...root.querySelectorAll(EMPH.join(','))]) {
  if (!el.parentNode) continue;
  const gapNodes = [];
  let gap = el.nextSibling;
  while (gap && gap.nodeType === 3 && !gap.textContent.trim()) { gapNodes.push(gap); gap = gap.nextSibling; }
  if (gap && gap.nodeType === 1 && gap.localName === el.localName && !gap.attributes.length && !el.attributes.length) {
    el.append(gapNodes.map((n) => n.textContent).join(''));
    gapNodes.forEach((n) => n.remove());
    while (gap.firstChild) el.append(gap.firstChild);
    gap.remove();
  }
}

const td = new TurndownService({
  headingStyle: 'atx', hr: '---', bulletListMarker: '-', emDelimiter: '*', strongDelimiter: '**',
  codeBlockStyle: 'fenced', br: '  ',
});
td.keep(['audio', 'video', 'iframe']);   // embeds stay as HTML

// Emphasis around punctuation only (<em>,</em>) cannot be written in Markdown, so it stays as HTML;
// emphasis around whitespace only is dropped.
td.addRule('emphWithoutWords', {
  filter: (n) => EMPH.includes(n.localName) && !/[\p{L}\p{N}]/u.test(n.textContent),
  replacement: (_c, n) => (n.textContent.trim() ? n.outerHTML : n.textContent),
});

// Line breaks. A break straight after another break is written as <br>, so that verse with
// blank lines between stanzas stays one paragraph and keeps its italics.
const prevMeaningful = (n) => { let p = n.previousSibling; while (p && p.nodeType === 3 && !p.textContent.trim()) p = p.previousSibling; return p; };
td.addRule('br', {
  filter: 'br',
  replacement: (_c, n) => (prevMeaningful(n)?.localName === 'br' ? '<br>\n' : '  \n'),
});

// Image: use the original file, at its original /wp-content/uploads path, never a resized variant.
td.addRule('img', {
  filter: 'img',
  replacement(_c, node) {
    const src = node.getAttribute('data-orig-file') || node.getAttribute('src') || '';
    const m = src.match(/\/wp-content\/uploads\/([^?#]+)/) || src.match(/\/media\/([^?#]+)/);
    const path = m ? `/wp-content/uploads/${m[1]}` : src;
    const alt = (node.getAttribute('alt') || '').replace(/\n/g, ' ');
    return `![${alt}](${path})`;
  },
});
td.addRule('figcaption', { filter: 'figcaption', replacement: (c) => `\n\n${c.trim()}\n\n` });

let md = td.turndown(root.innerHTML);
md = md.replace(/\n{3,}/g, '\n\n').trim();
process.stdout.write(md + '\n');
