#!/usr/bin/env bash
set -eo pipefail

# 🎨 Цвета (одинарные кавычки безопасны для set -e/-u)
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

log_ok() { echo -e "${GREEN}✅ $1${NC}"; }
log_warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo -e "\n${CYAN}🛑 Остановка Knowledge Base...${NC}"

# 1. SSH-туннели
echo -e "\n${YELLOW}🔹 Остановка туннелей...${NC}"
if pkill -f "ssh.*-R.*86\.110\.194\.68" 2>/dev/null; then
    log_ok "Туннели остановлены"
else
    log_warn "Туннели не были активны"
fi

# 2. Python-сервисы
echo -e "\n${YELLOW}🔹 Остановка сервисов...${NC}"
if pkill -f "python.*scripts/api\.py" 2>/dev/null; then
    log_ok "API остановлен"
else
    log_warn "API не был запущен"
fi

if pkill -f "python.*webhook-listener\.py" 2>/dev/null; then
    log_ok "Webhook остановлен"
else
    log_warn "Webhook не был запущен"
fi

# 3. Очистка портов (упрощено для надёжности)
echo -e "\n${YELLOW}🔹 Очистка портов...${NC}"
if command -v fuser >/dev/null 2>&1; then
    fuser -k 8000/tcp 2>/dev/null || true
    fuser -k 25000/tcp 2>/dev/null || true
else
    lsof -ti:8000 2>/dev/null | xargs -r kill -9 2>/dev/null || true
    lsof -ti:25000 2>/dev/null | xargs -r kill -9 2>/dev/null || true
fi
log_ok "Порты очищены"

# 4. Проверка
echo -e "\n${YELLOW}🔹 Проверка...${NC}"
sleep 1
if ss -tlnp 2>/dev/null | grep -qE ":(8000|25000) "; then
    log_warn "Порты всё ещё заняты (возможно, запущены от root)"
else
    log_ok "Все сервисы остановлены, порты свободны"
fi

echo -e "\n${GREEN}👋 Готово!${NC}\n"