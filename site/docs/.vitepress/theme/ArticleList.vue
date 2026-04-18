<template>
  <section class="article-list">
    <h2>Articles</h2>

    <div v-if="loadError" class="load-error">Failed to load articles.</div>

    <ul v-else>
      <li v-for="article in articles" :key="article.path">
        <a :href="withBase(article.path)">{{ article.title }}</a>
        <span v-if="article.description" class="desc">{{ article.description }}</span>
      </li>
    </ul>
  </section>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { withBase } from 'vitepress'

interface Article {
  title: string
  path: string
  description?: string
}

const articles = ref<Article[]>([])
const loadError = ref(false)

onMounted(async () => {
  try {
    const res = await fetch(withBase('/articles.json'))
    if (!res.ok) throw new Error()
    articles.value = await res.json()
  } catch {
    loadError.value = true
  }
})
</script>

<style scoped>
.article-list h2 {
  margin: 0 0 1rem;
}

ul {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

li {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}

a {
  font-weight: 500;
  color: var(--vp-c-brand-1);
  text-decoration: none;
}

a:hover {
  text-decoration: underline;
}

.desc {
  font-size: 0.875rem;
  color: var(--vp-c-text-2);
}

.load-error {
  color: var(--vp-c-danger-1);
}
</style>
