// Workshop photo slideshow (bottom of the page): a horizontal strip that moves on to the next photo every 3 seconds and starts again at the
// first one after the last. It waits while the pointer or keyboard focus is on it, while the photo viewer is open, while it is off screen or the
// tab is hidden, and it never moves by itself for visitors who asked for reduced motion (the arrows and swiping still work).
const root = document.querySelector<HTMLElement>('[data-slideshow]');
const track = root?.querySelector<HTMLElement>('.ss-track');
if (root && track) {
  const slides = Array.from(track.querySelectorAll<HTMLElement>('.ss-slide'));
  const step = () => (slides.length > 1 ? slides[1].offsetLeft - slides[0].offsetLeft : track.clientWidth);
  const atEnd = () => track.scrollLeft + track.clientWidth >= track.scrollWidth - 4;
  const go = (dir: 1 | -1) => {
    if (dir === 1 && atEnd()) track.scrollTo({ left: 0, behavior: 'smooth' });
    else if (dir === -1 && track.scrollLeft <= 4) track.scrollTo({ left: track.scrollWidth, behavior: 'smooth' });
    else track.scrollBy({ left: dir * step(), behavior: 'smooth' });
  };
  root.querySelector('.ss-prev')?.addEventListener('click', () => go(-1));
  root.querySelector('.ss-next')?.addEventListener('click', () => go(1));
  if (slides.length < 2) root.querySelectorAll<HTMLElement>('.ss-btn').forEach((b) => (b.hidden = true));

  const reduced = window.matchMedia('(prefers-reduced-motion: reduce)');
  let hover = false, focus = false, visible = false, touching = false;
  root.addEventListener('pointerenter', (e) => { if (e.pointerType === 'mouse') hover = true; });
  root.addEventListener('pointerleave', () => { hover = false; });
  root.addEventListener('focusin', () => { focus = true; });
  root.addEventListener('focusout', () => { focus = false; });
  root.addEventListener('touchstart', () => { touching = true; }, { passive: true });
  root.addEventListener('touchend', () => { window.setTimeout(() => { touching = false; }, 4000); }, { passive: true });
  new IntersectionObserver((entries) => { visible = entries[0].isIntersecting; }, { threshold: 0.3 }).observe(root);

  window.setInterval(() => {
    if (reduced.matches || slides.length < 2) return;
    if (hover || focus || touching || !visible || document.hidden) return;
    if (document.documentElement.classList.contains('lb-open')) return;
    go(1);
  }, 3000);
}
