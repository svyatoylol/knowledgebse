# Knowledge Base


## Запуск

```bash
# 1. Установить зависимости
npm install

# 2. Запустить VitePress
npm run dev
```


Ожидаемый формат ответа от скрипта — JSON с полем `answer`:

```json
{ "answer": "Текст ответа" }
```

Можно добавить любые дополнительные поля — `AiChat.vue` читает только `data.answer`,
остальное игнорируется.
