import sharp from 'sharp';
import { existsSync } from 'node:fs';
import { join } from 'node:path';

/** Pictures that are portrait or nearly square (width under 1.2 times the height) are shown whole in the workshop slideshow,
 *  on a grey ground, instead of being cropped to the wide frame (designer, 261010). Decided at build time. */
const cache = new Map<string, Promise<boolean>>();

async function measure(src: string): Promise<boolean> {
  const file = join(process.cwd(), 'public', src.split('?')[0]);
  if (!existsSync(file)) return false;
  try {
    const { width, height } = await sharp(file).metadata();
    return !!width && !!height && width / height < 1.2;
  } catch { return false; }
}

export function isTall(src?: string): Promise<boolean> {
  if (!src) return Promise.resolve(false);
  if (!cache.has(src)) cache.set(src, measure(src));
  return cache.get(src)!;
}
