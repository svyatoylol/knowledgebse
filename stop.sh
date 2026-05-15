#!/usr/bin/env bash
echo -e "\n🛑 Остановка всех сервисов..."

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOG_DIR="$PROJECT_DIR/logs"
VPS="root@86.110.194.68"

# 1. Туннель
echo "🔹 Остановка туннеля..."
[[ -f "$LOG_DIR/tunnel.pid" ]] && kill "$(cat "$LOG_DIR/tunnel.pid")" 2>/dev/null || true
pkill -f "ssh.*-R.*8000.*$VPS" 2>/dev/null && echo "  ✅ Туннель остановлен" || echo "  ⏭ Туннель не найден"

# 2. Сервисы
echo "🔹 Остановка Python-сервисов..."
pkill -f "python.*api\.py" 2>/dev/null && echo "  ✅ API остановлен" || echo "  ⏭ API не был запущен"
pkill -f "python.*webhook-listener\.py" 2>/dev/null && echo "  ✅ Webhook остановлен" || echo "  ⏭ Webhook не был запущен"

# 3. Порты
echo "🔹 Очистка портов..."
fuser -k 8000/tcp 2>/dev/null && echo "  ✅ Порт 8000 очищен" || echo "  ⏭ Порт 8000 свободен"
fuser -k 25000/tcp 2>/dev/null && echo "  ✅ Порт 25000 очищен" || echo "  ⏭ Порт 25000 свободен"

echo -e "\n${GREEN}✅ Готово!${NC}\n"