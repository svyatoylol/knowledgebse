// 📍 site/docs/articles.data.ts
import { createContentLoader } from 'vitepress'
import { fileURLToPath } from 'node:url'
import { dirname, resolve } from 'node:path'
import { readdirSync, readFileSync } from 'node:fs'

const __filename = fileURLToPath(import.meta.url)
const __dirname = dirname(__filename)

const PROJECT_ROOT = resolve(__dirname, '..', '..', '..')
const DATA_DIR = resolve(PROJECT_ROOT, 'data')
const ARTICLES_JSON = resolve(PROJECT_ROOT, 'site', 'public', 'articles.json')

interface Article {
  title: string
  path: string
  description: string
  filename: string
  date?: string
}

declare const data: Article[]
export { data }

export default createContentLoader('articles/*.md', {
  excerpt: true,
  render: true,
  transform(raw): Article[] {
    if (!raw?.length) return []
    
    return raw.map(({ url, frontmatter, excerpt }) => {
      // 🔥 1. Чистое имя файла (убираем и .md, и .html)
      const rawName = url.split('/').pop() || 'article'
      const cleanName = rawName.replace(/\.(md|html)$/, '')

      // 🔥 2. Извлечение заголовка (3 уровня приоритета)
      let title = frontmatter?.title
      if (!title && excerpt?.text) {
        const h1Match = excerpt.text.match(/^#\s+(.+)/m)
        if (h1Match) title = h1Match[1].trim()
      }
      if (!title) {
        // Fallback: человекочитаемое имя файла
        title = cleanName.replace(/[-_]/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
      }

      // 🔥 3. Извлечение описания
      const cleanText = excerpt?.text?.replace(/^#\s+.+\n*/s, '').trim() || ''
      const description = frontmatter?.description 
        || (cleanText.length > 10 ? cleanText.slice(0, 120) + '...' : 'Без описания')

      return { title, path: url, description, filename: rawName, date: frontmatter?.date }
    }).sort((a, b) => {
      const dA = a.date ? new Date(a.date).getTime() : 0
      const dB = b.date ? new Date(b.date).getTime() : 0
      return dB - dA
    })
  }
})