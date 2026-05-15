#!/usr/bin/env bash

# === 🎨 НАСТРОЙКИ ===
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; NC='\033[0m'
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$PROJECT_DIR/rag/knowledge-base"
SITE_DIR="$PROJECT_DIR/site"
LOG_DIR="$PROJECT_DIR/logs"
VPS="root@86.110.194.68"
SSH_KEY="$HOME/.ssh/kb_vps"
mkdir -p "$LOG_DIR"

# === 📊 ПРОГРЕСС-БАР ===
STEP=0; TOTAL=10
progress() {
    STEP=$((STEP + 1))
    local pct=$((STEP * 100 / TOTAL))
    local bar=""; for ((i=0; i<20; i++)); do [[ $i -lt $((pct/5)) ]] && bar+="#" || bar+="-"; done
    printf "\r${CYAN}[%s] %3d%% | %s${NC}" "$bar" "$pct" "$1"
}
log_ok() { echo -e "\n${GREEN}✅ $1${NC}"; }
log_warn() { echo -e "\n${YELLOW}⚠️  $1${NC}"; }

# === 🚇 ТУННЕЛЬ ===
start_tunnel() {
    progress "Туннель..."
    pkill -f "ssh.*-R.*86\.110\.194\.68" 2>/dev/null || true
    sleep 1
    
    # Два отдельных туннеля
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
        -R 0.0.0.0:8000:localhost:8000 -N -o ServerAliveInterval=30 "$VPS" >> "$LOG_DIR/tunnel_api.log" 2>&1 &
    ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
        -R 0.0.0.0:25000:localhost:25000 -N -o ServerAliveInterval=30 "$VPS" >> "$LOG_DIR/tunnel_wh.log" 2>&1 &
    
    # Проверка НА ВПС
    for i in {1..15}; do
        if ssh -i "$SSH_KEY" "$VPS" "ss -tlnp 2>/dev/null | grep -q ':8000 '" 2>/dev/null && \
           ssh -i "$SSH_KEY" "$VPS" "ss -tlnp 2>/dev/null | grep -q ':25000 '" 2>/dev/null; then
            break
        fi
        sleep 1
    done
    
    ssh -i "$SSH_KEY" "$VPS" "ss -tlnp 2>/dev/null | grep -q ':8000 '" 2>/dev/null && log_ok "API-туннель активен" || log_warn "API-туннель НЕ активен"
    ssh -i "$SSH_KEY" "$VPS" "ss -tlnp 2>/dev/null | grep -q ':25000 '" 2>/dev/null && log_ok "Webhook-туннель активен" || log_warn "Webhook-туннель НЕ активен"
}

# === 🖥️ ЗАПУСК СЕРВИСА В ТЕРМИНАЛЕ ===
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
        # Fallback: просто в фоне
        echo -e "${YELLOW}⚠️  Терминал не найден, запускаю '$title' в фоне${NC}"
        (bash -ic "$cmd") &
    fi
}

# === 🧹 ОЧИСТКА ===
cleanup() {
    echo -e "\n${YELLOW}🛑 Остановка...${NC}"
    pkill -f "ssh.*-R.*86\.110\.194\.68" 2>/dev/null || true
    pkill -f "python.*api\.py" 2>/dev/null || true
    pkill -f "python.*webhook-listener\.py" 2>/dev/null || true
}
trap cleanup EXIT INT TERM

# === 🚀 ГЛАВНЫЙ ЗАПУСК ===
echo -e "${CYAN}╔════════════════════════╗${NC}"
echo -e "${CYAN}║  🚀 Запуск KB          ║${NC}"
echo -e "${CYAN}╚════════════════════════╝${NC}"

# 0. Очистка портов
progress "Очистка..."
fuser -k 8000/tcp 2>/dev/null || true
fuser -k 25000/tcp 2>/dev/null || true
sleep 1
log_ok "Порты очищены"

# 1. Туннель
start_tunnel

# 2. Qdrant
progress "Qdrant..."
if command -v docker &>/dev/null && docker ps --format '{{.Names}}' 2>/dev/null | grep -q "^qdrant$"; then
    log_ok "Qdrant запущен"
elif command -v docker &>/dev/null; then
    docker run -d --name qdrant -p 6333:6333 --restart unless-stopped qdrant/qdrant >/dev/null 2>&1
    sleep 2 && log_ok "Qdrant запущен" || log_warn "Docker не запустил Qdrant"
else
    log_warn "Docker не найден"
fi

# 3. Ollama
progress "Ollama..."
curl -sf http://localhost:11434/api/tags >/dev/null 2>&1 && log_ok "Ollama готов" || log_warn "Ollama не отвечает"

# 4. Python venv
progress "Python..."
cd "$PYTHON_DIR" 2>/dev/null || { log_warn "Папка не найдена"; }
[ ! -d "venv" ] && python3 -m venv venv
source "$PYTHON_DIR/venv/bin/activate" 2>/dev/null || true
pip install -q flask flask-cors requests llama-index llama-index-core llama-index-embeddings-ollama llama-index-llms-ollama llama-index-vector-stores-qdrant==0.1.4 "numpy<2" python-dotenv 2>/dev/null
log_ok "Зависимости установлены"

# 5. Синхронизация
progress "Синхронизация..."
cd "$SITE_DIR" 2>/dev/null && python3 sync.py >/dev/null 2>&1 && log_ok "Данные синхронизированы" || log_warn "sync.py упал"

# 6. Индексация
progress "Индексация..."
cd "$PYTHON_DIR" 2>/dev/null && python3 ingest.py >/dev/null 2>&1 && log_ok "База проиндексирована" || log_warn "ingest.py упал"

# 7. Сборка фронтенда
progress "Сборка..."
cd "$SITE_DIR" 2>/dev/null && npm run build --silent >/dev/null 2>&1 && log_ok "Build завершён" || log_warn "npm build упал"

# 8. Деплой
progress "Деплой..."
cd "$SITE_DIR" 2>/dev/null
rsync -avz --delete -q docs/.vitepress/dist/ "$VPS:/var/www/swinki.ru/dist/" 2>/dev/null && log_ok "Фронтенд задеплоен" || log_warn "rsync упал"

# 9. 🔥 ЗАПУСК СЕРВИСОВ (исправленные вызовы!)
progress "Запуск API..."
echo ""
launch_service "🔙 API" "$PYTHON_DIR" "$PYTHON_DIR/venv/bin/activate" "$PYTHON_DIR/api.py"
sleep 2

# 10. Webhook
progress "Запуск Webhook..."
WEBHOOK_SCRIPT="$PROJECT_DIR/webhook-listener.py"
if [ -f "$WEBHOOK_SCRIPT" ]; then
    launch_service "📡 Webhook" "$PROJECT_DIR" "$PYTHON_DIR/venv/bin/activate" "$WEBHOOK_SCRIPT"
    log_ok "Webhook запущен"
else
    log_warn "webhook-listener.py не найден: $WEBHOOK_SCRIPT"
fi

# === 🎉 ФИНАЛ ===
echo -e "\n\n${GREEN}╔════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 Готово!            ║${NC}"
echo -e "${GREEN}╚════════════════════════╝${NC}"
echo -e "🌐 ${CYAN}https://swinki.ru${NC}"
echo -e "🤖 ${CYAN}http://localhost:8000${NC}"
echo -e "🎣 ${CYAN}http://localhost:25000${NC}"
echo -e "${YELLOW}💡 Закройте вкладки для остановки${NC}"
wait 2>/dev/null || true