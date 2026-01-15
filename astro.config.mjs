import { defineConfig } from 'astro/config';

export default defineConfig({
  site: 'https://penan-japanese-news.vercel.app',
  output: 'static',
  integrations: [], // 一旦エラー回避のため空にします
});
