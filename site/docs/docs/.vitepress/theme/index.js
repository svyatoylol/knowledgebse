import DefaultTheme from 'vitepress/theme'
import Layout from './Layout.vue'

export default {
  extends: DefaultTheme,
  Layout,
  enhanceApp({ app }) {
    // Здесь можно регистрировать глобальные компоненты, плагины и т.д.
  }
}