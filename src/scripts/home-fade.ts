// Home page: the photo stays pinned, and scrolling fades the photo's soft, darker copy in and the poem with it.
// Only runs where the page script has switched on `fx-home` (scripts on, no reduced-motion request); otherwise the plain stacked layout stays.
// After 2.5 seconds (counted from when the photo has loaded) with no action from the visitor, the page scrolls itself through the sequence; scrolling back up reverses it.
const root = document.documentElement;
const section = document.querySelector<HTMLElement>('[data-fade]');

if (section && root.classList.contains('fx-home')) {
  const track = section.querySelector<HTMLElement>('.split-track')!;
  const stage = section.querySelector<HTMLElement>('.split-stage')!;
  const poem = section.querySelector<HTMLElement>('.poem-s');
  const wrap = section.querySelector<HTMLElement>('.split-poem')!;
  const soft = section.querySelector<HTMLElement>('.split-soft')!;
  const lines = [...(poem ? Array.from(poem.querySelectorAll<HTMLElement>('p')) : []), ...Array.from(wrap.querySelectorAll<HTMLElement>('.notice'))];
  const smooth = (a: number, b: number, x: number) => { const t = Math.min(1, Math.max(0, (x - a) / (b - a))); return t * t * (3 - 2 * t); };

  let fadeLen = 0;

  const measure = () => {
    const h = stage.clientHeight;
    const pad = h < 700 ? 40 : 64;
    // shrink the whole poem (type and spacing together, to no less than 78%) so it fits the window with a margin above and below
    section.style.setProperty('--fit', '1');
    const natural = poem ? poem.offsetHeight : 0;
    const fit = natural ? Math.min(1, Math.max(0.78, (h - 2 * pad) / natural)) : 1;
    section.style.setProperty('--fit', fit.toFixed(3));
    section.style.setProperty('--pad', pad + 'px');
    const overflow = poem ? Math.max(0, poem.offsetHeight + 2 * pad - h) : 0; // only for windows too short even after shrinking
    fadeLen = h * 0.9;
    track.style.height = h + fadeLen + overflow + 'px';
    wrap.classList.toggle('tall', overflow > 0);
    section.dataset.overflow = String(overflow);
    update();
  };

  const update = () => {
    const y = window.scrollY;
    const p = smooth(0, 1, y / fadeLen);
    soft.style.opacity = p.toFixed(4);
    const o = smooth(0.25, 0.9, p).toFixed(3);
    lines.forEach((el) => { el.style.opacity = o; });
    const overflow = Number(section.dataset.overflow || 0);
    if (poem) poem.style.transform = overflow > 0 ? `translateY(${-Math.min(overflow, Math.max(0, y - fadeLen)).toFixed(1)}px)` : '';
  };

  // the soft copy, the poem and the header-height variable all follow the scroll position
  window.addEventListener('scroll', update, { passive: true });
  window.addEventListener('resize', measure);
  window.addEventListener('load', measure);
  measure();
  root.classList.add('fx-on');

  // the automatic run: scroll through the sequence over about 2.8 seconds; any action by the visitor stops it at once
  let animating = false;
  let cancel = () => {};
  const run = () => {
    if (animating) return;
    const from = window.scrollY;
    const to = fadeLen;
    if (from >= to - 1) return;
    animating = true;
    const start = performance.now();
    const dur = 2800;
    const stop = () => { animating = false; stopEvents.forEach((e) => window.removeEventListener(e, stop)); };
    const stopEvents = ['wheel', 'touchstart', 'keydown', 'mousedown'];
    stopEvents.forEach((e) => window.addEventListener(e, stop, { passive: true }));
    cancel = stop;
    const step = (now: number) => {
      if (!animating) return;
      const t = Math.min(1, (now - start) / dur);
      const e = t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; // ease in and out
      window.scrollTo({ top: from + (to - from) * e, behavior: 'instant' }); // 'instant': the page's own smooth scrolling would lag behind each step
      if (t < 1) requestAnimationFrame(step); else stop();
    };
    requestAnimationFrame(step);
  };

  // 2.5 seconds after the photo has loaded, with no scroll, key, touch or click
  let acted = false;
  const mark = () => { acted = true; };
  const actions = ['wheel', 'touchstart', 'keydown', 'mousedown', 'scroll'];
  actions.forEach((e) => window.addEventListener(e, mark, { passive: true, once: true }));
  const startTimer = () => window.setTimeout(() => { if (!acted && window.scrollY < 1 && document.visibilityState === 'visible') run(); }, 2500);
  const photo = section.querySelector<HTMLImageElement>('.split-photo picture img');
  if (!photo || (photo.complete && photo.naturalWidth > 0)) startTimer();
  else { photo.addEventListener('load', startTimer, { once: true }); photo.addEventListener('error', startTimer, { once: true }); }

}
