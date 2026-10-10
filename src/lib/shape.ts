import { isTallImage } from './imgsize';

/** Pictures that are portrait or nearly square (width under 1.2 times the height) are shown whole in the workshop slideshow
 *  instead of being cropped to the wide frame (designer, 261010). Decided at build time. */
export async function isTall(src?: string): Promise<boolean> {
  return !!src && isTallImage(src, 1.2);
}
