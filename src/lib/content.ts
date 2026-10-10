import { getCollection, type CollectionEntry } from 'astro:content';
import { isUpcoming } from './dates';
import type { Lang } from '../i18n/ui';

const byStart = (a: { data: { start: Date } }, b: { data: { start: Date } }) =>
  a.data.start.getTime() - b.data.start.getTime();

/** Split dated entries into upcoming (soonest first) and past (latest first). */
export function splitByDate<T extends { data: { start: Date; end?: Date } }>(items: T[]) {
  const upcoming = items.filter((i) => isUpcoming(i.data.start, i.data.end)).sort(byStart);
  const past = items.filter((i) => !isUpcoming(i.data.start, i.data.end)).sort((a, b) => byStart(b, a));
  return { upcoming, past };
}

export function groupByYear<T extends { data: { start: Date } }>(items: T[]) {
  const years = new Map<number, T[]>();
  for (const i of items) {
    const y = i.data.start.getUTCFullYear();
    years.set(y, [...(years.get(y) ?? []), i]);
  }
  return [...years.entries()].sort((a, b) => b[0] - a[0]);
}

export async function getSchedule() {
  return splitByDate(await getCollection('schedule'));
}
export async function getEvents() {
  return splitByDate(await getCollection('events'));
}

/** Pages are written once in English; a version in another language lives at pages/<lang>/<id>.md when it exists. */
export async function getPage(id: string, lang: Lang) {
  const pages = await getCollection('pages');
  const en = pages.find((p) => p.id === id);
  if (!en) throw new Error(`Missing page content: ${id}`);
  const own = lang !== 'en' ? pages.find((p) => p.id === `${lang}/${id}`) : undefined;
  return { entry: own ?? en, fallback: lang !== 'en' && !own };
}

/** blog entry id "2020-04-28-slug" -> { y, m, d, slug } and path "/2020/04/28/slug/" */
export function postParts(entry: CollectionEntry<'blog'>) {
  const m = entry.id.match(/^(\d{4})-(\d{2})-(\d{2})-(.+)$/);
  if (!m) throw new Error(`Blog file name must start with YYYY-MM-DD-: ${entry.id}`);
  return { year: m[1], month: m[2], day: m[3], slug: m[4] };
}
export function postPath(entry: CollectionEntry<'blog'>) {
  const p = postParts(entry);
  return `/${p.year}/${p.month}/${p.day}/${p.slug}/`;
}
export async function getPosts() {
  return (await getCollection('blog')).sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
}

export function formatTime(time: string | undefined, lang: Lang) {
  if (!time) return undefined;
  if (lang !== 'en') return time; // 24-hour clock
  const [h, m] = time.split(':').map(Number);
  return `${((h + 11) % 12) + 1}:${String(m).padStart(2, '0')} ${h < 12 ? 'am' : 'pm'}`;
}
