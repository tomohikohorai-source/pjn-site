import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  site: 'https://penan-japanese-news.vercel.app',
  integrations: [sitemap()],
});
