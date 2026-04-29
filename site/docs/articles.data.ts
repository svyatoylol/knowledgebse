// site/docs/articles.data.ts
import { readFileSync, readdirSync } from 'fs'
import { join } from 'path'

export interface Article {
  title: string
  path: string
  description: string
}

export default {
  // Следить за изменениями в папке со статьями
  watch: ['../../rag/knowledge-base/data/*.md'],
  
  async load(): Promise<Article[]> {
    const dataDir = join(__dirname, '../../rag/knowledge-base/data')
    const articles: Article[] = []
    
    for (const file of readdirSync(dataDir)) {
      if (!file.endsWith('.md')) continue
      
      const content = readFileSync(join(dataDir, file), 'utf-8')
      
      // Извлекаем заголовок (# ...)
      const titleMatch = content.match(/^#\s+(.+)$/m)
      const title = titleMatch?.[1]?.trim() || file.replace('.md', '')
      
      // Извлекаем первое предложение после заголовка как описание
      const descMatch = content.match(/^#\s+.+\n\n(.+?)(?:\n\n|##|$)/s)
      const rawDesc = descMatch?.[1]?.trim() || ''
      const description = rawDesc.slice(0, 120) + (rawDesc.length > 120 ? '...' : '')
      
      articles.push({
        title,
        path: `/articles/${file.replace('.md', '')}`,
        description
      })
    }
    
    return articles
  }
}
