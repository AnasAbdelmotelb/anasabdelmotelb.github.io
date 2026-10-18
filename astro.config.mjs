// @ts-check
import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

// User site on GitHub Pages is served from the domain root, so no `base` is needed.
export default defineConfig({
  site: 'https://anasabdelmotelb.github.io',
  // Generates sitemap-index.xml + sitemap-0.xml at build time from the real pages.
  // The 404 page is left out: it is not a page anyone should land on from search.
  integrations: [sitemap({ filter: (page) => !page.includes('/404') })],
});
