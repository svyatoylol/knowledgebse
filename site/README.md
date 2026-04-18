# Knowledge Base

VitePress + AI assistant + статьи.

## Структура

```
docs/
  .vitepress/
    config.ts          — конфиг сайта + Vite proxy
    theme/
      index.ts         — подключение кастомной темы
      Layout.vue       — обёртка: вставляет компоненты на главной
      AiChat.vue       — чат с AI, POST /api/ask → JSON
      ArticleList.vue  — список статей из public/articles.json
  public/
    articles.json      — мета-данные статей (title, path, description)
  index.md             — главная страница
  *.md                 — статьи
ai_backend.py          — заглушка Python-бэкенда (замените на свой скрипт)
```

## Запуск

```bash
# 1. Установить зависимости
npm install

# 2. Запустить Python-бэкенд (в отдельном терминале)
python ai_backend.py

# 3. Запустить VitePress
npm run dev
```

## Добавление статей

1. Создайте файл `docs/your-article.md`.
2. Добавьте запись в `docs/public/articles.json`:

```json
{
  "title": "Your Article",
  "path": "/your-article",
  "description": "Short description"
}
```

## Интеграция своего AI-скрипта

В `ai_backend.py` замените тело функции `ask()`:

```python
def ask(query: str) -> dict:
    result = subprocess.run(["python", "my_ai_script.py", query], capture_output=True)
    return json.loads(result.stdout)
```

Ожидаемый формат ответа от скрипта — JSON с полем `answer`:

```json
{ "answer": "Текст ответа" }
```

Можно добавить любые дополнительные поля — `AiChat.vue` читает только `data.answer`,
остальное игнорируется.
