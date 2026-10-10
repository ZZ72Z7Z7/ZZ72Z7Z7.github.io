import sharp from 'sharp';
import { publicFile } from './publicfile';

/** Photos whose edges are nearly white (drawings, posters, white backgrounds) get a hairline frame (1d, designer 261009),
 *  so they do not dissolve into the white page. Decided at build time from the average brightness of the picture's outer edge. */
const cache = new Map<string, Promise<boolean>>();

async function measure(src: string): Promise<boolean> {
  const file = publicFile(src);
  if (!file) return false;
  try {
    const { data, info } = await sharp(file).flatten({ background: '#fff' }).resize(40, 40, { fit: 'fill' }).greyscale().raw().toBuffer({ resolveWithObject: true });
    let sum = 0, n = 0;
    for (let y = 0; y < info.height; y++) for (let x = 0; x < info.width; x++) {
      if (x < 2 || y < 2 || x >= info.width - 2 || y >= info.height - 2) { sum += data[y * info.width + x]; n++; }
    }
    return sum / n > 225;
  } catch { return false; }
}

export function isPale(src?: string): Promise<boolean> {
  if (!src) return Promise.resolve(false);
  if (!cache.has(src)) cache.set(src, measure(src));
  return cache.get(src)!;
}
