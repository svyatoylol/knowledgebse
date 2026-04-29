# 🧠 Knowledge Base

AI-powered документация с возможностью задавать вопросы по содержимому базы знаний.

> **RAG-система** (Retrieval-Augmented Generation) на локальных моделях — без облачных зависимостей.

---

## ✨ Возможности

- 🔍 **Поиск по базе знаний**: задавайте вопросы на естественном языке
- 🤖 **Локальный AI**: работает через Ollama (llama3.2:3b), без отправки данных в интернет
- 📚 **VitePress-сайт**: красивая документация с поддержкой Markdown
- 🔄 **Автосинхронизация**: статьи подтягиваются из внешнего репозитория
- 🐧🪟 **Кроссплатформенность**: скрипты запуска для Linux и Windows

---

## 🛠️ Технологический стек

| Компонент | Технология |
|-----------|-----------|
| **Фронтенд** | VitePress, Vue 3, TypeScript |
| **Бэкенд** | Python 3.10+, Flask, Flask-CORS |
| **Векторная БД** | Qdrant |
| **LLM / Эмбеддинги** | Ollama (llama3.2:3b, mxbai-embed-large) |
| **Синхронизация** | Git sparse-checkout, Python |

---

## 🚀 Быстрый старт

### Требования

- [Docker](https://docs.docker.com/get-docker/) — для Qdrant
- [Ollama](https://ollama.ai) — для локальных моделей
- [Python 3.10+](https://python.org)
- [Node.js 18+](https://nodejs.org)

### Установка

```bash
# 1. Клонируйте репозиторий
git clone https://github.com/svyatoylol/knowledgebse.git

# 2. Настройте окружение
setup-and-run.bat # Windows

# 3. Запустите проект
./start.sh          # Linux / macOS
# или
start.bat           # Windows

# 4. Перейдите по ссылке окна с Vitepress из раздела local
