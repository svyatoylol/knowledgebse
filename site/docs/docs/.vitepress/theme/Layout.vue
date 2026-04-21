<script setup>
import DefaultTheme from 'vitepress/theme'
import SearchHero from '../components/SearchHero.vue'
import { useRoute } from 'vitepress'

const route = useRoute()
</script>

<template>
  <DefaultTheme.Layout>
    <!-- Показываем поиск только на главной странице -->
    <template #home-hero-before>
      <SearchHero v-if="route.path === '/'" />
    </template>
  </DefaultTheme.Layout>
</template>