import { today, formatLongDate, isUpcoming } from './dates';
import { t, type Lang } from '../i18n/ui';

export type StatusKey = 'pending' | 'open' | 'waitlist' | 'closed';
export interface Status { key: StatusKey; label: string; note?: string }

/**
 * Application status chip of a workshop edition (designer, 261011).
 * Only upcoming editions show one. A Pending edition becomes Open on its opening date, if one is given. An Open edition becomes Closed on its own once its
 * application deadline has passed. Pending and Open add a line of text (shown on the details page only).
 */
export function getStatus(
  d: { status?: StatusKey; applications_open?: Date; applications_close?: Date; start: Date; end?: Date },
  lang: Lang,
): Status | undefined {
  if (!d.status || !isUpcoming(d.start, d.end)) return undefined;
  const ui = t(lang);
  let key = d.status;
  const now = today().getTime();
  // Pending turns Open by itself once its opening date has passed (when one is given)
  if (key === 'pending' && d.applications_open && d.applications_open.getTime() <= now) key = 'open';
  if (key === 'open' && d.applications_close && d.applications_close.getTime() < now) key = 'closed';
  const label = { pending: ui.statusPending, open: ui.statusOpen, waitlist: ui.statusWaitlist, closed: ui.statusClosed }[key];
  let note: string | undefined;
  if (key === 'pending') note = d.applications_open ? `${ui.appsOpen} ${formatLongDate(d.applications_open, lang)}` : ui.appsDateTba;
  if (key === 'open' && d.applications_close) note = `${ui.appsClose} ${formatLongDate(d.applications_close, lang)}`;
  return { key, label, note };
}
