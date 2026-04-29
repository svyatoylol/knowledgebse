<template>
  <div class="article-list">
    <h2>📚 Статьи</h2>
    <ul>
      <li v-for="article in articles" :key="article.path">
        <a :href="article.path">{{ article.title }}</a>
        <span v-if="article.description" class="desc">{{ article.description }}</span>
      </li>
    </ul>
  </div>
</template>

<script setup lang="ts">
import { data as articles } from '../../articles.data.ts'
</script>

<style scoped>
.article-list { max-width: 800px; margin: 0 auto; padding: 1rem 0; }
.article-list h2 { margin: 0 0 1rem; }
ul { list-style: none; padding: 0; display: flex; flex-direction: column; gap: 0.75rem; }
li { padding: 0.75rem; border: 1px solid var(--vp-c-divider); border-radius: 8px; background: var(--vp-c-bg-soft); display: flex; flex-direction: column; gap: 0.25rem; }
a { font-weight: 600; color: var(--vp-c-brand-1); text-decoration: none; }
a:hover { text-decoration: underline; }
.desc { font-size: 0.85rem; color: var(--vp-c-text-2); }
</style>