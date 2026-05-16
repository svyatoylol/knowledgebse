#!/usr/bin/env bash
set -euo pipefail

# 🎨 Цвета
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; NC='\033[0m'
log() { echo -e "${GREEN}[$(date '+%H:%M:%S')] $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }

# 🔗 Пути: скрипт в scripts/ → корень проекта на уровень выше
SCRIPTS_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPTS_DIR")"
VENV="$PROJECT_ROOT/venv/bin/activate"
SITE_DIR="$PROJECT_ROOT/site"
LOG_DIR="$PROJECT_ROOT/logs"
LOG_FILE="$LOG_DIR/update.log"

# 🔐 Создаём папку для логов
mkdir -p "$LOG_DIR"

# 📝 Логирование в файл + консоль
exec > >(tee -a "$LOG_FILE") 2>&1

log "🔄 Начало обновления..."
log "   📁 Проект: $PROJECT_ROOT"
log "   🐍 Venv: $VENV"

# === 0. Проверка окружения ===
if [[ ! -f "$VENV" ]]; then
    error "❌ Виртуальное окружение не найдено: $VENV"
    error "💡 Запустите: python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

# === 1️⃣ Git pull ===
log "📥 Синхронизация с репозиторием..."
cd "$PROJECT_ROOT"

# Сохраняем локальные изменения (если есть)
if ! git diff --quiet || ! git diff --cached --quiet; then
    warn "📦 Есть локальные изменения — сохраняю в stash..."
    git stash push -m "auto-stash before update $(date '+%Y-%m-%d %H:%M')" >/dev/null 2>&1
    STASHED=true
else
    STASHED=false
fi

# Делаем pull
if git pull --rebase origin main >/dev/null 2>&1; then
    log "✅ Репозиторий обновлён"
else
    warn "⚠️  Не удалось сделать rebase — пробую обычный merge..."
    git pull origin main >/dev/null 2>&1 && log "✅ Репозиторий обновлён" || \
        { warn "⚠️  Конфликты слияния — разрешите их вручную"; }
fi

# Восстанавливаем засташенные изменения
if [[ "$STASHED" == "true" ]]; then
    warn "♻️  Восстанавливаю локальные изменения..."
    git stash pop >/dev/null 2>&1 || warn "⚠️  Конфликт при восстановлении — проверьте файлы"
fi

# === 2️⃣ Активация venv и проверка зависимостей ===
log "🐍 Активация Python окружения..."
source "$VENV"

# Быстрая проверка критичных пакетов
if ! python3 -c "import llama_index, qdrant_client, flask" >/dev/null 2>&1; then
    warn "⚠️  Зависимости не установлены — запускаю pip install..."
    pip install -q -r "$PROJECT_ROOT/requirements.txt" 2>/dev/null && \
        log "✅ Зависимости установлены" || warn "⚠️  Ошибка установки зависимостей"
fi

# === 3️⃣ Синхронизация статей ===
log "🔄 Синхронизация статей..."
if python3 "$SCRIPTS_DIR/sync.py" 2>&1 | tee -a "$LOG_FILE"; then
    log "✅ Статьи синхронизированы"
else
    warn "⚠️  sync.py вернул ошибку — проверьте логи"
fi

# === 4️⃣ Сборка фронтенда ===
log "📦 Сборка фронтенда..."
cd "$SITE_DIR"
if npm run build --silent 2>&1 | tee -a "$LOG_FILE"; then
    log "✅ VitePress build завершён"
else
    warn "⚠️  Сборка фронтенда упала — проверьте node_modules"
fi

# === 5️⃣ Деплой на VPS ===
log "🚀 Деплой на VPS..."
VPS_USER="${VPS_USER:-root}"
VPS_HOST="${VPS_HOST:-86.110.194.68}"
SSH_KEY="${VPS_SSH_KEY:-$HOME/.ssh/kb_vps}"

if rsync -avz --delete -q -e "ssh -i '$SSH_KEY' -o StrictHostKeyChecking=no" \
    docs/.vitepress/dist/ \
    "${VPS_USER}@${VPS_HOST}:/var/www/swinki.ru/dist/" 2>&1 | tee -a "$LOG_FILE"; then
    log "✅ Фронтенд задеплоен на $VPS_HOST"
else
    warn "⚠️  rsync не удался — проверьте SSH-ключ и доступность VPS"
fi

# === 6️⃣ Переиндексация базы (только если изменились статьи) ===
log "🧠 Проверка необходимости переиндексации..."
cd "$PROJECT_ROOT"

# Проверяем, менялись ли файлы в data/ за последний коммит
if git diff HEAD~1 HEAD --name-only 2>/dev/null | grep -q "^data/"; then
    log "📚 Статьи изменились — запускаю индексацию..."
    if python3 "$SCRIPTS_DIR/ingest.py" 2>&1 | tee -a "$LOG_FILE"; then
        log "✅ База проиндексирована в Qdrant"
    else
        warn "⚠️  ingest.py вернул ошибку — проверьте Qdrant/Ollama"
    fi
else
    log "✨ Статьи не менялись — пропускаю индексацию"
fi

# === 7️⃣ Перезапуск сервисов (опционально, раскомментируйте если нужно) ===
# log "🔄 Перезапуск сервисов..."
# pkill -f "python.*scripts/api.py" 2>/dev/null || true
# sleep 2
# (cd "$PROJECT_ROOT" && source "$VENV" && python3 "$SCRIPTS_DIR/api.py" >> "$LOG_DIR/api.log" 2>&1 &)
# log "✅ Сервисы перезапущены"

# === 🎉 ФИНАЛ ===
log "🎉 Обновление завершено!"
echo ""
echo "   🌐 Сайт:     https://swinki.ru"
echo "   🤖 API:      https://swinki.ru/api/ask"
echo "   📁 Логи:     $LOG_FILE"
echo "   🧠 Qdrant:   http://localhost:6333/dashboard"