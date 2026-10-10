// Gallery lightbox: selecting a picture in the gallery opens it large over the page, with arrows (and the left/right keys, and swiping)
// to move between the pictures, a close button (and Escape, or a click outside the picture), and the caption and position underneath.
// Without JavaScript the gallery pictures are plain links to the full-size files.
const box = document.querySelector<HTMLDialogElement>('dialog.lightbox');
const links = Array.from(document.querySelectorAll<HTMLAnchorElement>('.wk-gallery a'));

if (box && links.length) {
  const img = box.querySelector<HTMLImageElement>('.lb-img')!;
  const cap = box.querySelector<HTMLElement>('.lb-caption')!;
  const count = box.querySelector<HTMLElement>('.lb-count')!;
  const prev = box.querySelector<HTMLButtonElement>('.lb-prev')!;
  const next = box.querySelector<HTMLButtonElement>('.lb-next')!;
  const close = box.querySelector<HTMLButtonElement>('.lb-close')!;
  const of = box.dataset.of ?? 'of';
  let index = 0;
  let opener: HTMLElement | null = null;

  const show = (i: number) => {
    index = (i + links.length) % links.length;
    const a = links[index];
    img.src = a.href;
    cap.innerHTML = a.closest('figure')?.querySelector('figcaption')?.innerHTML ?? '';
    cap.hidden = !cap.innerHTML.trim();
    count.textContent = links.length > 1 ? `${index + 1} ${of} ${links.length}` : '';
    // load the neighbours ahead of time so the arrows feel instant
    [index - 1, index + 1].forEach((n) => { const p = new Image(); p.src = links[(n + links.length) % links.length].href; });
  };
  const open = (i: number, from: HTMLElement) => {
    opener = from;
    show(i);
    box.showModal();
    document.documentElement.classList.add('lb-open');
  };
  const closeBox = () => box.close();

  links.forEach((a, i) => a.addEventListener('click', (e) => { e.preventDefault(); open(i, a); }));
  img.addEventListener('click', () => { if (links.length > 1) show(index + 1); }); // a click on the picture advances to the next one
  img.style.cursor = links.length > 1 ? 'pointer' : 'default';
  prev.addEventListener('click', () => show(index - 1));
  next.addEventListener('click', () => show(index + 1));
  close.addEventListener('click', closeBox);
  if (links.length < 2) { prev.hidden = true; next.hidden = true; }

  box.addEventListener('close', () => { document.documentElement.classList.remove('lb-open'); opener?.focus(); });
  // a click on the dark area (not on the picture, caption or buttons) closes it
  box.addEventListener('click', (e) => { if (e.target === box || (e.target as HTMLElement).classList.contains('lb-figure')) closeBox(); });
  box.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') { e.preventDefault(); show(index - 1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); show(index + 1); }
  });
  // swipe on touch screens
  let startX = 0;
  box.addEventListener('pointerdown', (e) => { startX = e.clientX; });
  box.addEventListener('pointerup', (e) => {
    const dx = e.clientX - startX;
    if (e.pointerType === 'touch' && Math.abs(dx) > 50) show(index + (dx < 0 ? 1 : -1));
  });
}
