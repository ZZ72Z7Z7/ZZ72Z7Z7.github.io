import { existsSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

/** Finds a file under public/ for a site address such as /wp-content/uploads/... . The build runs from the project folder, but the preview
 *  server can be started from a parent folder, so also try the folder two levels above this file. */
export function publicFile(src: string): string | undefined {
  const rel = join('public', src.split('?')[0]);
  const roots = [process.cwd(), fileURLToPath(new URL('../..', import.meta.url))];
  for (const root of roots) { const f = join(root, rel); if (existsSync(f)) return f; }
  return undefined;
}
