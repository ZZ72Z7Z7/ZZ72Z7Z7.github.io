// Workshop page sections: on desktop (1024px and up) every section is open and stays open; on phones and tablets each section is an accordion row,
// all closed at first. Without JavaScript every section is simply open.
const list = document.querySelector<HTMLElement>('[data-wk-acc]');
if (list) {
  const rows = Array.from(list.querySelectorAll<HTMLDetailsElement>('details.wk-acc'));
  // a list marked data-desktop-acc keeps the accordion behaviour at every width (experiment on one page)
  const keep = list.hasAttribute('data-desktop-acc');
  const desktop = window.matchMedia('(min-width: 64rem)');
  const flat = () => desktop.matches && !keep;
  // in the accordion-everywhere experiment only the sections marked data-open-default start open, and a window resize leaves them alone
  const apply = () => rows.forEach((d) => { d.open = keep ? d.hasAttribute('data-open-default') : flat(); });
  apply();
  if (!keep) desktop.addEventListener('change', apply);
  // on desktop the headings are plain headings: selecting them does nothing
  rows.forEach((d) => d.querySelector('summary')!.addEventListener('click', (e) => { if (flat()) e.preventDefault(); }));
}
