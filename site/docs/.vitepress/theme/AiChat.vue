<template>
  <div class="ai-chat">
    <h2>🤖 AI Assistant</h2>
    <div class="messages" ref="messagesEl">
      <div v-for="(msg, i) in messages" :key="i" :class="['message', msg.role]">
        <div class="bubble">{{ msg.content }}</div>
      </div>
      <div v-if="loading" class="message assistant">
        <div class="bubble loading">⏳ Думаю...</div>
      </div>
    </div>
    <form class="input-row" @submit.prevent="send">
      <input v-model="input" :disabled="loading" placeholder="Задайте вопрос..." autocomplete="off" />
      <button type="submit" :disabled="loading || !input.trim()">➤</button>
    </form>
    <p v-if="error" class="error">{{ error }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
const AI_API_URL = '/api/ask'
const messages = ref<{ role: string; content: string }[]>([])
const input = ref('')
const loading = ref(false)
const error = ref('')
const messagesEl = ref<HTMLElement>()

async function send() {
  const text = input.value.trim()
  if (!text) return
  messages.value.push({ role: 'user', content: text })
  input.value = ''; loading.value = true; error.value = ''
  await scrollToBottom()
  try {
    const res = await fetch(AI_API_URL, {
      method: 'POST', headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question: text })
    })
    if (!res.ok) throw new Error(`Server error: ${res.status}`)
    const data = await res.json()
    messages.value.push({ role: 'assistant', content: data.answer || 'Нет ответа' })
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Не удалось соединиться'
  } finally {
    loading.value = false; await scrollToBottom()
  }
}
async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) messagesEl.value.scrollTop = messagesEl.value.scrollHeight
}
</script>

<style scoped>
.ai-chat{display:flex;flex-direction:column;gap:1rem;max-width:600px;margin:0 auto}
.ai-chat h2{margin:0}
.messages{display:flex;flex-direction:column;gap:0.5rem;max-height:400px;overflow-y:auto;padding:1rem;border:1px solid var(--vp-c-divider);border-radius:12px;background:var(--vp-c-bg-soft)}
.message{display:flex}.message.user{justify-content:flex-end}
.bubble{max-width:80%;padding:0.75rem 1rem;border-radius:16px;line-height:1.5;white-space:pre-wrap}
.message.user .bubble{background:var(--vp-c-brand-1);color:#fff}.message.assistant .bubble{background:var(--vp-c-bg-mute)}
.loading{opacity:0.7}
.input-row{display:flex;gap:0.5rem}.input-row input{flex:1;padding:0.75rem;border:2px solid var(--vp-c-divider);border-radius:8px;background:var(--vp-c-bg)}
.input-row input:focus{border-color:var(--vp-c-brand-1)}
.input-row button{padding:0.75rem 1.5rem;border:none;border-radius:8px;background:var(--vp-c-brand-1);color:#fff;cursor:pointer}
.input-row button:disabled{opacity:0.5}.error{color:var(--vp-c-danger-1);margin:0}
</style>