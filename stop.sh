#!/bin/bash

echo "🛑 Остановка процессов..."

# Остановить контейнер Qdrant
docker stop qdrant 2>/dev/null
echo "✅ Qdrant остановлен."

# Найти и убить процессы Python (api.py) и Node (vite)
pkill -f "python api.py" 2>/dev/null
pkill -f "vitepress" 2>/dev/null

echo "✅ Все процессы остановлены."

