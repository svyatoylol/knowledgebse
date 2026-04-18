<template>
  <section class="ai-chat">
    <h2>AI Assistant</h2>

    <div class="messages" ref="messagesEl">
      <div
        v-for="(msg, i) in messages"
        :key="i"
        :class="['message', msg.role]"
      >
        <div class="bubble">{{ msg.content }}</div>
      </div>
      <div v-if="loading" class="message assistant">
        <div class="bubble loading">...</div>
      </div>
    </div>

    <form class="input-row" @submit.prevent="send">
      <input
        v-model="input"
        :disabled="loading"
        placeholder="Ask something..."
        autocomplete="off"
      />
      <button type="submit" :disabled="loading || !input.trim()">Send</button>
    </form>

    <p v-if="error" class="error">{{ error }}</p>
  </section>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

interface ApiResponse {
  answer: string
  [key: string]: unknown
}

const AI_API_URL = '/api/ask'

const messages = ref<Message[]>([])
const input = ref('')
const loading = ref(false)
const error = ref('')
const messagesEl = ref<HTMLElement>()

async function send() {
  const text = input.value.trim()
  if (!text) return

  messages.value.push({ role: 'user', content: text })
  input.value = ''
  loading.value = true
  error.value = ''

  await scrollToBottom()

  try {
    const res = await fetch(AI_API_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query: text }),
    })

    if (!res.ok) throw new Error(`Server error: ${res.status}`)

    const data: ApiResponse = await res.json()
    messages.value.push({ role: 'assistant', content: data.answer })
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Unknown error'
  } finally {
    loading.value = false
    await scrollToBottom()
  }
}

async function scrollToBottom() {
  await nextTick()
  if (messagesEl.value) {
    messagesEl.value.scrollTop = messagesEl.value.scrollHeight
  }
}
</script>

<style scoped>
.ai-chat {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.ai-chat h2 {
  margin: 0;
}

.messages {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 400px;
  overflow-y: auto;
  padding: 1rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 8px;
  background: var(--vp-c-bg-soft);
}

.message {
  display: flex;
}

.message.user {
  justify-content: flex-end;
}

.bubble {
  max-width: 75%;
  padding: 0.5rem 0.875rem;
  border-radius: 12px;
  line-height: 1.5;
  white-space: pre-wrap;
  word-break: break-word;
}

.message.user .bubble {
  background: var(--vp-c-brand-1);
  color: #fff;
}

.message.assistant .bubble {
  background: var(--vp-c-bg-mute);
  color: var(--vp-c-text-1);
}

.loading {
  opacity: 0.6;
}

.input-row {
  display: flex;
  gap: 0.5rem;
}

.input-row input {
  flex: 1;
  padding: 0.5rem 0.75rem;
  border: 1px solid var(--vp-c-divider);
  border-radius: 6px;
  background: var(--vp-c-bg);
  color: var(--vp-c-text-1);
  font-size: 1rem;
  outline: none;
}

.input-row input:focus {
  border-color: var(--vp-c-brand-1);
}

.input-row button {
  padding: 0.5rem 1.25rem;
  border: none;
  border-radius: 6px;
  background: var(--vp-c-brand-1);
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
}

.input-row button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.error {
  color: var(--vp-c-danger-1);
  margin: 0;
}
</style>
