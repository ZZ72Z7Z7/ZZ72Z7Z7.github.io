import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';
import { readdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

// SITE_URL is set by the deploy workflow. Until the real domain is pointed at
// GitHub Pages, the site builds with the final address so links stay correct.
const site = process.env.SITE_URL || 'https://giovannifusetti.com';

// Design review pages (src/design/*.astro) exist only while working locally; they are never built or published.
const designPages = {
  name: 'design-pages',
  hooks: {
    'astro:config:setup': ({ command, injectRoute }) => {
      if (command !== 'dev') return;
      const dir = fileURLToPath(new URL('./src/design/', import.meta.url));
      for (const file of readdirSync(dir).filter((f) => f.endsWith('.astro'))) {
        injectRoute({ pattern: `/design/${file.replace('.astro', '')}`, entrypoint: `${dir}${file}` });
      }
    },
  },
};

export default defineConfig({
  site,
  trailingSlash: 'always',
  build: { format: 'directory' },
  // docs/ (the copy GitHub Pages serves) and dist/ are build output: keep the dev server from watching them
  vite: { server: { watch: { ignored: ['**/docs/**', '**/dist/**', '**/archive/**'] } } },
  integrations: [
    designPages,
    sitemap({
      i18n: { defaultLocale: 'en', locales: { en: 'en', it: 'it' } },
    }),
  ],
});
