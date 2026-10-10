// Video gallery: selecting a thumbnail opens that video in the viewer, with arrows (and the left/right keys) to move between videos and a close button
// (also Escape, or a click outside the video). Closing the viewer removes the video, so the sound stops. Without JavaScript the thumbnails are plain links to the videos.
const box = document.querySelector<HTMLDialogElement>('dialog.video-box');
const tiles = Array.from(document.querySelectorAll<HTMLAnchorElement>('.video-tiles a.vtile'));

if (box && tiles.length) {
  const frame = box.querySelector<HTMLIFrameElement>('.lb-video')!;
  const cap = box.querySelector<HTMLElement>('.lb-caption')!;
  const count = box.querySelector<HTMLElement>('.lb-count')!;
  const prev = box.querySelector<HTMLButtonElement>('.lb-prev')!;
  const next = box.querySelector<HTMLButtonElement>('.lb-next')!;
  const close = box.querySelector<HTMLButtonElement>('.lb-close')!;
  const of = box.dataset.of ?? 'of';
  let index = 0;
  let opener: HTMLElement | null = null;

  const show = (i: number) => {
    index = (i + tiles.length) % tiles.length;
    const a = tiles[index];
    frame.title = a.dataset.title ?? '';
    frame.src = a.dataset.embed ?? a.href;
    cap.innerHTML = a.dataset.caption ? `<strong>${a.dataset.title ?? ''}</strong><br>${a.dataset.caption}` : '';
    cap.hidden = !cap.innerHTML.trim();
    count.textContent = `${index + 1} ${of} ${tiles.length}`;
  };
  tiles.forEach((a, i) => a.addEventListener('click', (e) => { e.preventDefault(); opener = a; show(i); box.showModal(); document.documentElement.classList.add('lb-open'); }));
  prev.addEventListener('click', () => show(index - 1));
  next.addEventListener('click', () => show(index + 1));
  close.addEventListener('click', () => box.close());
  box.addEventListener('close', () => { frame.src = 'about:blank'; document.documentElement.classList.remove('lb-open'); opener?.focus(); });
  box.addEventListener('click', (e) => { if (e.target === box || (e.target as HTMLElement).classList.contains('lb-figure')) box.close(); });
  box.addEventListener('keydown', (e) => {
    if (e.key === 'ArrowLeft') { e.preventDefault(); show(index - 1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); show(index + 1); }
  });
}
