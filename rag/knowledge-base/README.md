# 🧠 Локальная база знаний (RAG)

Полностью автономная система для вопросов-ответов по вашим документам. Работает офлайн, без API-ключей и лимитов.

**Стек:** `Ollama` (LLM + Embeddings) + `Qdrant` (Vector DB) + `Python` + `LlamaIndex`

---

## ✨ Возможности
- 🔒 **Приватность**: данные не покидают ваш компьютер
- 🌐 **Без лимитов**: никаких очередей, платных подписок или зависимостей от интернета
- 📚 **Поддержка форматов**: `.txt`, `.md`, `.pdf`, `.docx`, `.html`
- 🔍 **Семантический поиск**: находит ответы по смыслу, а не только по ключевым словам
- 🤖 **Локальные модели**: использует лёгкие и эффективные модели Ollama

---

## 🚀 Быстрый старт

### Предварительные требования
- Python 3.10+
- [Docker](https://docs.docker.com/get-docker/) (для Qdrant)
- [Ollama](https://ollama.com/download) (для ИИ-моделей)

### 1. Установка зависимостей
```bash
cd rag/knowledge-base
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Qdrant (векторная база данных)
docker start qdrant 2>/dev/null || \
docker run -d --name qdrant -v qdrant_/qdrant/storage -p 6333:6333 qdrant/qdrant

# Ollama + модели
ollama pull llama3.2:3b mxbai-embed-large

# Создаём локальный конфиг (не отслеживается в Git)
cp .env.example .env

# Добавьте свои файлы в папку data/
echo "Ваш текст, инструкции, код, заметки..." > data/info.txt

# Векторизация документов (займёт 1-3 минуты)
python ingest.py

# Интерактивный чат
python query.py

Конфигурация .env(подключить к файлам)
OLLAMA_URL
http://localhost:11434
Адрес API Ollama
OLLAMA_LLM_MODEL
llama3.2:3b
Модель для генерации ответов
OLLAMA_EMBEDDING_MODEL
mxbai-embed-large
Модель для векторизации текста
QDRANT_URL
http://localhost:6333
Адрес Qdrant
CHUNK_SIZE
128
Размер чанка в токенах
