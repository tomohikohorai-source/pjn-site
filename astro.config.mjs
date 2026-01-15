import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  // あなたの実際のURLに書き換えてください
  site: 'https://penan-japanese-news.vercel.app',
  integrations: [sitemap()],
  output: 'static',
});
