#!/usr/bin/env bash
# 📍 НАХОДИТСЯ В КОРНЕ ПРОЕКТА
# ✅ Плоская структура: venv/, scripts/, data/, logs/ в корне
set -euo pipefail

GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; NC='\033[0m'
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$PROJECT_DIR/scripts"
VENV_DIR="$PROJECT_DIR/venv"
SITE_DIR="$PROJECT_DIR/site"
LOG_DIR="$PROJECT_DIR/logs"
VPS="root@86.110.194.68"
SSH_KEY="$HOME/.ssh/kb_vps"
TOTAL_STEPS=10
CURRENT_STEP=0
mkdir -p "$LOG_DIR"

progress() {
    CURRENT_STEP=$((CURRENT_STEP + 1))
    local pct=$((CURRENT_STEP * 100 / TOTAL_STEPS))
    local bar=""; for ((i=0; i<20; i++)); do [[ $i -lt $((pct/5)) ]] && bar+="#" || bar+="-"; done
    printf "\r${CYAN}[%s] %3d%% | %s${NC}" "$bar" "$pct" "$1"
}
log_ok() { echo -e "\n${GREEN}✅ $1${NC}"; }
log_warn() { echo -e "\n${YELLOW}⚠️  $1${NC}"; }

# 🚇 Туннель
start_tunnel() {
    progress "Туннель..."
    pkill -f "ssh.*-R.*86\.110\.194\.68" 2>/dev/null || true
    sleep 1
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -R 0.0.0.0:8000:localhost:8000 -N -o ServerAliveInterval=30 "$VPS" >> "$LOG_DIR/tunnel_api.log" 2>&1 &
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -R 0.0.0.0:25000:localhost:25000 -N -o ServerAliveInterval=30 "$VPS" >> "$LOG_DIR/tunnel_wh.log" 2>&1 &
    for i in {1..15}; do
        ssh -i "$SSH_KEY" "$VPS" "ss -tlnp 2>/dev/null | grep -q ':8000 '" 2>/dev/null && \
        ssh -i "$SSH_KEY" "$VPS" "ss -tlnp 2>/dev/null | grep -q ':25000 '" 2>/dev/null && break
        sleep 1
    done
    ssh -i "$SSH_KEY" "$VPS" "ss -tlnp 2>/dev/null | grep -q ':8000 '" 2>/dev/null && log_ok "API-туннель" || log_warn "API-туннель"
    ssh -i "$SSH_KEY" "$VPS" "ss -tlnp 2>/dev/null | grep -q ':25000 '" 2>/dev/null && log_ok "Webhook-туннель" || log_warn "Webhook-туннель"
}

# 🖥️ Запуск сервиса
launch_service() {
    local title="$1" work_dir="$2" venv="$3" script="$4"
    local cmd="cd '$work_dir' && source '$venv' && exec python3 '$script'"
    if command -v gnome-terminal &>/dev/null; then 
        gnome-terminal --title="$title" -- bash -ic "$cmd" &
    elif command -v cosmic-term &>/dev/null; then 
        cosmic-term -e bash -ic "$cmd" &
    elif command -v konsole &>/dev/null; then 
        konsole --new-tab -e bash -ic "$cmd" &
    else 
        (bash -ic "$cmd") &
    fi
}

# 🧹 Очистка (вызывает stop.sh)
cleanup() {
    echo -e "\n${YELLOW}🛑 Остановка...${NC}"
    if [[ -f "$PROJECT_DIR/stop.sh" ]]; then
        bash "$PROJECT_DIR/stop.sh" 2>/dev/null || true
    else
        pkill -f "ssh.*-R.*86\.110\.194\.68" 2>/dev/null || true
        pkill -f "python.*api\.py" 2>/dev/null || true
        pkill -f "python.*webhook-listener\.py" 2>/dev/null || true
    fi
}
trap cleanup EXIT INT TERM

# 🚀 ГЛАВНЫЙ ЗАПУСК
echo -e "${CYAN}╔════════════════════════╗${NC}"
echo -e "${CYAN}║  🚀 Запуск KB          ║${NC}"
echo -e "${CYAN}╚════════════════════════╝${NC}"

# 0. Очистка портов
progress "Очистка..."
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 25000/tcp 2>/dev/null || true
sleep 1
log_ok "Порты очищены"

# 1. Туннели
start_tunnel

# 2. Qdrant
progress "Qdrant..."
if command -v docker &>/dev/null; then
    if docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^qdrant$"; then
        log_ok "Qdrant запущен"
    else
        docker run -d --name qdrant -p 6333:6333 --restart unless-stopped qdrant/qdrant >/dev/null 2>&1
        sleep 2
        log_ok "Qdrant запущен"
    fi
else
    log_warn "Docker не найден — убедитесь, что Qdrant запущен вручную"
fi

# 3. Ollama
progress "Ollama..."
if curl -sf http://localhost:11434/api/tags >/dev/null 2>&1; then
    log_ok "Ollama готов"
else
    log_warn "Ollama не отвечает — запустите: ollama serve"
fi

# 4. Python venv + зависимости (максимально надёжная версия)
progress "Python..."

# Функция для создания/восстановления venv
ensure_venv() {
    if [[ ! -d "$VENV_DIR" ]] || [[ ! -x "$VENV_DIR/bin/python3" ]]; then
        log_warn "⚠️  venv не найден или повреждён — создаю заново..."
        rm -rf "$VENV_DIR"
        
        # Проверяем наличие python3-venv
        if ! python3 -m venv --help >/dev/null 2>&1; then
            log_warn "⚠️  python3-venv не установлен — пытаюсь установить..."
            sudo apt update && sudo apt install -y python3.12-venv 2>/dev/null || \
            sudo apt install -y python3-venv 2>/dev/null || true
        fi
        
        python3 -m venv "$VENV_DIR"
        
        # Проверка успеха
        if [[ ! -x "$VENV_DIR/bin/python3" ]]; then
            log_warn "❌ Не удалось создать venv — проверьте права и наличие python3-venv"
            return 1
        fi
        log_ok "venv создан"
    fi
    return 0
}

# Создаём/проверяем venv
if ! ensure_venv; then
    log_warn "⚠️  Пропускаю установку зависимостей (venv недоступен)"
    progress "Синхронизация..."  # Сдвигаем счётчик шагов
    continue
fi

# Определяем пути к python/pip (учитываем, что может быть pip или pip3)
PYTHON="$VENV_DIR/bin/python3"
PIP="$VENV_DIR/bin/pip"
[[ ! -x "$PIP" ]] && PIP="$VENV_DIR/bin/pip3"
[[ ! -x "$PIP" ]] && PIP="$VENV_DIR/bin/pip3.12"

# Финальная проверка
if [[ ! -x "$PIP" ]]; then
    log_warn "❌ pip не найден в venv — пересоздаю..."
    rm -rf "$VENV_DIR"
    python3 -m venv "$VENV_DIR"
    PIP="$VENV_DIR/bin/pip"
    [[ ! -x "$PIP" ]] && PIP="$VENV_DIR/bin/pip3"
fi

# Обновляем pip и устанавливаем зависимости
if "$PIP" install -q --upgrade pip setuptools wheel 2>&1 | tee -a "$LOG_DIR/start.log"; then
    # Установка основных зависимостей
    if "$PIP" install -q -r "$PROJECT_DIR/requirements.txt" 2>&1 | tee -a "$LOG_DIR/start.log"; then
        log_ok "Зависимости установлены"
    else
        log_warn "❌ pip install упал — см. $LOG_DIR/start.log"
        log_warn "💡 Попробуйте вручную: $PIP install -r requirements.txt"
    fi
else
    log_warn "⚠️  Не удалось обновить pip — продолжаю без обновления"
    # Пробуем установить зависимости старым pip
    "$PIP" install -q -r "$PROJECT_DIR/requirements.txt" 2>&1 | tee -a "$LOG_DIR/start.log" && \
        log_ok "Зависимости установлены" || \
        log_warn "❌ Ошибка установки зависимостей"
fi
# 5. Синхронизация статей
progress "Синхронизация..."
if python3 "$SCRIPTS_DIR/sync.py" >/dev/null 2>&1; then
    log_ok "Данные синхронизированы"
else
    log_warn "sync.py упал"
fi

# 6. Индексация в Qdrant
progress "Индексация..."
if python3 "$SCRIPTS_DIR/ingest.py" >/dev/null 2>&1; then
    log_ok "База проиндексирована"
else
    log_warn "ingest.py упал"
fi

# 7. Сборка фронтенда
progress "Сборка..."
cd "$SITE_DIR" 2>/dev/null && npm run build --silent >/dev/null 2>&1 && log_ok "Build завершён" || log_warn "npm build упал"

# 8. Деплой на VPS
progress "Деплой..."
cd "$SITE_DIR" 2>/dev/null
if rsync -avz --delete -q docs/.vitepress/dist/ "$VPS:/var/www/swinki.ru/dist/" 2>/dev/null; then
    log_ok "Фронтенд задеплоен"
else
    log_warn "rsync не удался — проверьте SSH"
fi

# 9. Запуск API
progress "Запуск API..."
echo ""
launch_service "🔙 API" "$PROJECT_DIR" "$VENV_DIR/bin/activate" "$SCRIPTS_DIR/api.py"
sleep 2

# 10. Запуск Webhook
progress "Запуск Webhook..."
if [[ -f "$SCRIPTS_DIR/webhook-listener.py" ]]; then
    launch_service "📡 Webhook" "$PROJECT_DIR" "$VENV_DIR/bin/activate" "$SCRIPTS_DIR/webhook-listener.py"
    log_ok "Webhook запущен"
else
    log_warn "webhook-listener.py не найден"
fi

# === 🎉 ФИНАЛ ===
echo -e "\n\n${GREEN}╔════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 Готово!            ║${NC}"
echo -e "${GREEN}╚════════════════════════╝${NC}"
echo -e "🌐 ${CYAN}https://swinki.ru${NC}"
echo -e "🤖 ${CYAN}http://localhost:8000${NC}"
echo -e "🎣 ${CYAN}http://localhost:25000${NC}"
echo -e "${YELLOW}💡 Закройте вкладки или нажмите ./stop.sh для остановки${NC}"
wait 2>/dev/null || true