import { readFileSync } from 'node:fs';
import { publicFile } from './publicfile';

/** Size of a picture under public/ as the visitor sees it (JPEG and PNG), read straight from the file header so it works in the synchronous
 *  text renderer. JPEG photos that carry a "rotate" mark (EXIF orientation 5 to 8) are reported with width and height swapped. */
const cache = new Map<string, { w: number; h: number } | null>();

function read(file: string): { w: number; h: number } | null {
  const b = readFileSync(file);
  if (b.length > 24 && b.readUInt32BE(0) === 0x89504e47) return { w: b.readUInt32BE(16), h: b.readUInt32BE(20) };
  if (b[0] !== 0xff || b[1] !== 0xd8) return null;
  let o = 2, orient = 1, dims: { w: number; h: number } | null = null;
  while (o + 4 < b.length) {
    if (b[o] !== 0xff) { o++; continue; }
    const m = b[o + 1], len = b.readUInt16BE(o + 2);
    if (m === 0xe1 && b.toString('latin1', o + 4, o + 8) === 'Exif') {
      const t = o + 10, le = b.toString('latin1', t, t + 2) === 'II';
      const u16 = (p: number) => (le ? b.readUInt16LE(p) : b.readUInt16BE(p));
      const u32 = (p: number) => (le ? b.readUInt32LE(p) : b.readUInt32BE(p));
      const ifd = t + u32(t + 4), n = u16(ifd);
      for (let i = 0; i < n; i++) { const e = ifd + 2 + i * 12; if (u16(e) === 0x0112) orient = u16(e + 8); }
    }
    if (m >= 0xc0 && m <= 0xcf && m !== 0xc4 && m !== 0xc8 && m !== 0xcc) { dims = { h: b.readUInt16BE(o + 5), w: b.readUInt16BE(o + 7) }; break; }
    o += 2 + len;
  }
  if (!dims) return null;
  return orient >= 5 ? { w: dims.h, h: dims.w } : dims;
}

export function imageSize(src: string): { w: number; h: number } | null {
  if (!cache.has(src)) {
    let r: { w: number; h: number } | null = null;
    try { const f = publicFile(src); if (f) r = read(f); } catch { r = null; }
    cache.set(src, r);
  }
  return cache.get(src)!;
}

/** Portrait pictures (taller than wide) are the ones the portrait rule in global.css applies to. The slideshow also treats nearly square pictures
 *  (width under 1.2 times the height) as tall, because a wide frame would cut too much off them: pass 1.2 there. */
export function isTallImage(src: string, limit = 1): boolean {
  const d = imageSize(src);
  return !!d && d.w / d.h < limit;
}
