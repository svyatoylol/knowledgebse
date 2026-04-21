<script setup>
import { ref } from 'vue';
import { useRouter } from 'vitepress';

const router = useRouter();
const query = ref('');
const results = ref([]);
const loading = ref(false);
const error = ref('');

// Основная функция поиска
const searchCSharpTopic = async () => {
  const text = query.value;
  if (!text.trim()) {
    results.value = [];
    return;
  }

  loading.value = true;
  error.value = '';
  results.value = []; // Очищаем старые результаты при новом поиске

  try {
    const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:3000/api/search';
    
    const response = await fetch(API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text })
    });

    if (!response.ok) {
      throw new Error('Ошибка сервера');
    }

    const data = await response.json();
    results.value = data.results || [];

    // Если найден ровно 1 результат -> сразу переходим
    if (results.value.length === 1) {
      const slug = results.value[0].slug;
      router.go(`/articles/${slug}`);
    }
  } catch (err) {
    error.value = err.message || 'Не удалось выполнить поиск';
    results.value = [];
  } finally {
    loading.value = false;
  }
};

// Переход по выбранной статье из списка
const selectResult = (slug) => {
  router.go(`/articles/${slug}`);
};
</script>

<template>
  <div class="search-hero">
    <h1 class="title">Изучай C# с умом</h1>
    <p class="subtitle">Введи тему и нажми Enter или кнопку 🔍</p>

    <div class="search-box">
      <input
        v-model="query"
        type="text"
        placeholder="Например: асинхронность, LINQ, паттерны проектирования..."
        :disabled="loading"
        @keyup.enter="searchCSharpTopic"
      />
      <button 
        class="search-btn" 
        @click="searchCSharpTopic" 
        :disabled="loading || !query.trim()"
      >
        <span v-if="loading">⏳</span>
        <span v-else>🔍</span>
      </button>
    </div>

    <p v-if="error" class="error">{{ error }}</p>

    <ul v-if="results.length > 1" class="results-list">
      <li v-for="item in results" :key="item.slug" class="result-item">
        <button @click="selectResult(item.slug)">
          📘 {{ item.title }}
          <span class="score">Совпадение: {{ (item.score * 100).toFixed(0) }}%</span>
        </button>
      </li>
    </ul>

    <p v-else-if="query && results.length === 0 && !loading" class="no-results">
      Ничего не найдено. Попробуй изменить запрос.
    </p>
  </div>
</template>

<style scoped>
.search-hero {
  max-width: 800px;
  margin: 4rem auto 2rem;
  text-align: center;
  padding: 0 1rem;
}
.title {
  font-size: 2.5rem;
  margin-bottom: 0.5rem;
}
.subtitle {
  color: var(--vp-c-text-2);
  margin-bottom: 2rem;
}
.search-box {
  display: flex;
  gap: 0.5rem;
  max-width: 600px;
  margin: 0 auto;
}
.search-box input {
  flex: 1;
  padding: 1rem 1.2rem;
  font-size: 1.1rem;
  border: 2px solid var(--vp-c-divider);
  border-radius: 12px;
  background: var(--vp-c-bg-soft);
  transition: border-color 0.2s;
}
.search-box input:focus {
  outline: none;
  border-color: var(--vp-c-brand);
}
.search-btn {
  padding: 0 1.2rem;
  font-size: 1.3rem;
  background: var(--vp-c-brand);
  color: white;
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: opacity 0.2s, transform 0.1s;
}
.search-btn:hover:not(:disabled) {
  opacity: 0.9;
  transform: scale(1.05);
}
.search-btn:active:not(:disabled) {
  transform: scale(0.98);
}
.search-btn:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}
.error {
  color: #ef4444;
  margin-top: 1rem;
}
.results-list {
  list-style: none;
  padding: 0;
  margin: 2rem auto 0;
  max-width: 600px;
  text-align: left;
}
.result-item button {
  width: 100%;
  padding: 1rem;
  margin-bottom: 0.5rem;
  background: var(--vp-c-bg-soft);
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 1rem;
  transition: background 0.2s, border-color 0.2s;
}
.result-item button:hover {
  background: var(--vp-c-bg-mute);
  border-color: var(--vp-c-brand);
}
.score {
  font-size: 0.85rem;
  color: var(--vp-c-text-2);
}
.no-results {
  margin-top: 1rem;
  color: var(--vp-c-text-2);
}
</style>