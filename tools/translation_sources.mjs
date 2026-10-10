// Writes the English sources for the Italian draft translation (261009) into translations/source/, in the sectioned format described in translations/BRIEF.md.
// Run from the project folder:  node tools/translation_sources.mjs
import { readFileSync, writeFileSync, mkdirSync, readdirSync, existsSync } from 'node:fs';
import { parse } from 'yaml';
const C = 'src/content', S = 'translations/source';
const split = (t) => { const m = t.match(/^---\n([\s\S]*?)\n---\n?([\s\S]*)$/); return m ? [parse(m[1]) ?? {}, m[2].replace(/^\n+/, '').replace(/\s+$/, '')] : [{}, t]; };
const sec = (name, text) => `=== ${name} ===\n${String(text).replace(/\s+$/, '')}\n`;
const ls = (d) => readdirSync(`${C}/${d}`).filter((f) => !f.startsWith('.') && !f.includes('/') && /\.(md|yml)$/.test(f));
for (const d of ['workshops', 'blog', 'events', 'schedule', 'pages']) mkdirSync(`${S}/${d}`, { recursive: true });

// workshops
for (const f of ls('workshops')) {
  const [fm, body] = split(readFileSync(`${C}/workshops/${f}`, 'utf8'));
  let out = '';
  if (fm.subtitle && !fm.subtitle_it) out += sec('subtitle', fm.subtitle);
  if (body && !fm.body_it) out += sec('body', body);
  if (fm.program && !fm.program_it) out += sec('program', fm.program);
  if (fm.image_caption && !fm.image_caption_it) out += sec('image_caption', fm.image_caption);
  if (fm.credits && !fm.credits_it) out += sec('credits', fm.credits);
  const caps = (fm.gallery ?? []).map((g, i) => (g.caption && !g.caption_it ? `${i + 1}: ${String(g.caption).replace(/\n/g, ' ')}` : null)).filter(Boolean);
  if (caps.length) out += sec('gallery_captions', caps.join('\n'));
  if (out) writeFileSync(`${S}/workshops/${f}`, out);
}
// blog
for (const f of ls('blog')) {
  const [fm, body] = split(readFileSync(`${C}/blog/${f}`, 'utf8'));
  let out = '';
  if (fm.title && !fm.title_it) out += sec('title', fm.title);
  if (body && !fm.body_it) out += sec('body', body);
  if (out) writeFileSync(`${S}/blog/${f}`, out);
}
// events
for (const f of ls('events')) {
  const [fm, body] = split(readFileSync(`${C}/events/${f}`, 'utf8'));
  let out = '';
  if (fm.title && !fm.title_it) out += sec('title', fm.title);
  if (fm.subtitle && !fm.subtitle_it) out += sec('subtitle', fm.subtitle);
  if (body && !fm.body_it) out += sec('body', body);
  if (fm.admission && !fm.admission_it) out += sec('admission', fm.admission);
  const labels = (fm.pdfs ?? []).map((p, i) => (p.label && !p.label_it ? `${i + 1}: ${p.label}` : null)).filter(Boolean);
  if (labels.length) out += sec('pdf_labels', labels.join('\n'));
  if (out) writeFileSync(`${S}/events/${f}`, out);
}
// schedule: the long text fields of the upcoming entries, and every tagline (description) of the past ones
const upcoming = [];
const taglines = [];
for (const f of ls('schedule')) {
  const fm = parse(readFileSync(`${C}/schedule/${f}`, 'utf8')) ?? {};
  const long = ['schedule', 'location_details', 'tuition', 'applications'].filter((k) => fm[k] && !fm[`${k}_it`]);
  let out = '';
  for (const k of long) out += sec(k, fm[k]);
  if (fm.extra_dates && !fm.extra_dates_it) out += sec('extra_dates', fm.extra_dates);
  if (fm.language_note && !fm.language_note_it) out += sec('language_note', fm.language_note);
  if (out) { writeFileSync(`${S}/schedule/${f.replace(/\.yml$/, '.md')}`, out); upcoming.push(f); }
  if (fm.description && !fm.description_it) taglines.push(`${f}\t${String(fm.description).replace(/\n/g, ' / ')}`);
}
writeFileSync(`${S}/schedule/_taglines.tsv`, taglines.join('\n') + '\n');
// pages: the whole file (front matter included)
for (const f of ls('pages')) {
  if (existsSync(`${C}/pages/it/${f}`)) continue;
  writeFileSync(`${S}/pages/${f}`, readFileSync(`${C}/pages/${f}`, 'utf8'));
}
console.log('sources written; upcoming schedule files:', upcoming.length, '; taglines:', taglines.length);
