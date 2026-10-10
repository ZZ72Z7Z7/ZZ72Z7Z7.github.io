// Workshop page sections: on desktop (1024px and up) every section is open and stays open; on phones and tablets each section is an accordion row,
// all closed at first. Without JavaScript every section is simply open.
const list = document.querySelector<HTMLElement>('[data-wk-acc]');
if (list) {
  const rows = Array.from(list.querySelectorAll<HTMLDetailsElement>('details.wk-acc'));
  const desktop = window.matchMedia('(min-width: 64rem)');
  const apply = () => rows.forEach((d) => { d.open = desktop.matches; });
  apply();
  desktop.addEventListener('change', apply);
  // on desktop the headings are plain headings: selecting them does nothing
  rows.forEach((d) => d.querySelector('summary')!.addEventListener('click', (e) => { if (desktop.matches) e.preventDefault(); }));
}
