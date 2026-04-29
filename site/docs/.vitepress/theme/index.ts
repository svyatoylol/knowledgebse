// site/docs/.vitepress/theme/index.ts
import DefaultTheme from 'vitepress/theme'
import AiChat from './AiChat.vue'        // 👇 ./ означает "текущая папка"
import ArticleList from './ArticleList.vue'

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('AiChat', AiChat)
    app.component('ArticleList', ArticleList)
  }
}