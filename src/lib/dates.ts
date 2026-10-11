import type { Lang } from '../i18n/ui';

const MONTHS: Record<Lang, string[]> = {
  en: ['January','February','March','April','May','June','July','August','September','October','November','December'],
  it: ['gennaio','febbraio','marzo','aprile','maggio','giugno','luglio','agosto','settembre','ottobre','novembre','dicembre'],
  es: ['enero','febrero','marzo','abril','mayo','junio','julio','agosto','septiembre','octubre','noviembre','diciembre'],
  fr: ['janvier','février','mars','avril','mai','juin','juillet','août','septembre','octobre','novembre','décembre'],
  de: ['Januar','Februar','März','April','Mai','Juni','Juli','August','September','Oktober','November','Dezember'],
};
const DAYS: Record<Lang, string[]> = {
  en: ['Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday'],
  it: ['domenica','lunedì','martedì','mercoledì','giovedì','venerdì','sabato'],
  es: ['domingo','lunes','martes','miércoles','jueves','viernes','sábado'],
  fr: ['dimanche','lundi','mardi','mercredi','jeudi','vendredi','samedi'],
  de: ['Sonntag','Montag','Dienstag','Mittwoch','Donnerstag','Freitag','Samstag'],
};
/** How a day, month and year are joined in each language: "October 19, 2026", "19 ottobre 2026", "19 de octubre de 2026", "19. Oktober 2026". */
const STYLE: Record<Lang, { day: (n: number) => string; monthJoin: string; yearJoin: string; monthFirst: boolean }> = {
  en: { day: (n) => String(n), monthJoin: ' ', yearJoin: ', ', monthFirst: true },
  it: { day: (n) => String(n), monthJoin: ' ', yearJoin: ' ', monthFirst: false },
  es: { day: (n) => String(n), monthJoin: ' de ', yearJoin: ' de ', monthFirst: false },
  fr: { day: (n) => String(n), monthJoin: ' ', yearJoin: ' ', monthFirst: false },
  de: { day: (n) => `${n}.`, monthJoin: ' ', yearJoin: ' ', monthFirst: false },
};

/** Today's date at midnight UTC. Set SITE_TODAY=YYYY-MM-DD to test another date. */
export function today(): Date {
  const override = process.env.SITE_TODAY;
  if (override) return new Date(`${override}T00:00:00Z`);
  const n = new Date();
  return new Date(Date.UTC(n.getUTCFullYear(), n.getUTCMonth(), n.getUTCDate()));
}

/** An entry is upcoming until the day after its end date (or start date, if no end). */
export function isUpcoming(start: Date, end?: Date): boolean {
  return (end ?? start).getTime() >= today().getTime();
}

const same = (a: Date, b: Date, part: 'getUTCFullYear' | 'getUTCMonth') => a[part]() === b[part]();

/** "October 19 - 24, 2026"  /  "19 - 24 ottobre 2026"  /  "19 - 24 de octubre de 2026"  /  "19. - 24. Oktober 2026" */
export function formatRange(start: Date, end: Date | undefined, lang: Lang): string {
  const m = MONTHS[lang];
  const st = STYLE[lang];
  const fmt = (d: Date, withYear: boolean, withMonth = true) => {
    const day = st.day(d.getUTCDate());
    const mon = m[d.getUTCMonth()];
    const y = d.getUTCFullYear();
    if (st.monthFirst) return `${withMonth ? mon + st.monthJoin : ''}${day}${withYear ? st.yearJoin + y : ''}`;
    return `${day}${withMonth ? st.monthJoin + mon : ''}${withYear ? st.yearJoin + y : ''}`;
  };
  if (!end || end.getTime() === start.getTime()) return fmt(start, true);
  if (!same(start, end, 'getUTCFullYear')) return `${fmt(start, true)} - ${fmt(end, true)}`;
  if (!same(start, end, 'getUTCMonth')) return `${fmt(start, false)} - ${fmt(end, true)}`;
  // Same month: the month is written once.
  const [d1, d2, mon, y] = [st.day(start.getUTCDate()), st.day(end.getUTCDate()), m[start.getUTCMonth()], start.getUTCFullYear()];
  return st.monthFirst ? `${mon}${st.monthJoin}${d1} - ${d2}${st.yearJoin}${y}` : `${d1} - ${d2}${st.monthJoin}${mon}${st.yearJoin}${y}`;
}

/** "Saturday, August 22, 2026"  /  "sabato 22 agosto 2026"  /  "sábado, 22 de agosto de 2026"  /  "Samstag, 22. August 2026" */
export function formatDay(d: Date, lang: Lang): string {
  const wd = DAYS[lang][d.getUTCDay()];
  const comma = lang === 'en' || lang === 'es' || lang === 'de' ? ', ' : ' ';
  return `${wd}${comma}${formatLongDate(d, lang)}`;
}

export function formatLongDate(d: Date, lang: Lang): string {
  const st = STYLE[lang];
  const mon = MONTHS[lang][d.getUTCMonth()];
  const day = st.day(d.getUTCDate());
  const y = d.getUTCFullYear();
  return st.monthFirst ? `${mon}${st.monthJoin}${day}${st.yearJoin}${y}` : `${day}${st.monthJoin}${mon}${st.yearJoin}${y}`;
}

export const isoDate = (d: Date) => d.toISOString().slice(0, 10);

/** City names that differ by language. None today: the client's preference (261011) is "Padova" in every language, stored as "Padova" in the content.
 *  Add a { English: 'Italiano' } pair here if another city ever needs it. */
const CITY_IT: Record<string, string> = {};
export function cityName(city: string | undefined, lang: Lang): string | undefined {
  return city && lang === 'it' ? CITY_IT[city] ?? city : city;
}
