import { defineConfig } from 'astro/config';
import sitemap from '@astrojs/sitemap';

export default defineConfig({
  // 末尾にスラッシュを入れない、最もクリーンなURL指定
  site: 'https://penan-japanese-news.vercel.app',
  integrations: []
});
