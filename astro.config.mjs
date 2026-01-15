import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  // URLの末尾にスラッシュを入れない設定で統一します
  site: 'https://penan-japanese-news.vercel.app',
  integrations: [sitemap()],
  output: 'static'
});
