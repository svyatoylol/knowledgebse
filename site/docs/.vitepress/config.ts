import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'Knowledge Base',
  description: 'AI-powered knowledge base',
  vite: {
    server: {
      proxy: {
        '/api': 'http://localhost:3001',
      },
    },
  },
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
    ],
  },
})
