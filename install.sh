#!/usr/bin/env bash
# 📍 НАХОДИТСЯ В КОРНЕ ПРОЕКТА
# ✅ Установка всех зависимостей для Knowledge Base
set -eo pipefail  # 🔥 Без -u, чтобы цвета работали надёжно

# 🎨 Цвета (безопасное определение)
: "${GREEN:=\033[0;32m}"
: "${YELLOW:=\033[1;33m}"
: "${RED:=\033[0;31m}"
: "${CYAN:=\033[0;36m}"
: "${NC:=\033[0m}"

log() { echo -e "${GREEN}✅ $1${NC}"; }
warn() { echo -e "${YELLOW}⚠️  $1${NC}"; }
err() { echo -e "${RED}❌ $1${NC}"; exit 1; }

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR" || err "Не удалось перейти в папку проекта"

echo -e "${CYAN}╔════════════════════════════════════╗${NC}"
echo -e "${CYAN}║  🚀 Установка Knowledge Base      ║${NC}"
echo -e "${CYAN}╚════════════════════════════════════╝${NC}"
echo ""

# 1. Системные пакеты
echo -e "${CYAN}[1/6] Установка системных пакетов...${NC}"
if command -v apt &>/dev/null; then
    sudo apt update && sudo apt install -y git curl wget build-essential python3-venv python3-pip
elif command -v brew &>/dev/null; then
    brew install git curl python3 node
else
    warn "Пакетный менеджер не обнаружен — установите зависимости вручную"
fi
log "Системные пакеты установлены"

# 2. Docker
echo -e "${CYAN}[2/6] Проверка Docker...${NC}"
if ! command -v docker &>/dev/null; then
    warn "Docker не найден — устанавливаю..."
    if command -v apt &>/dev/null; then
        sudo apt install -y docker.io
        sudo systemctl enable --now docker
        sudo usermod -aG docker "$USER" 2>/dev/null || true
        log "Docker установлен. Перезагрузитесь для активации прав."
    else
        warn "Установите Docker вручную: https://docs.docker.com/get-docker/"
    fi
else
    log "Docker уже установлен"
fi

# 3. Ollama
echo -e "${CYAN}[3/6] Проверка Ollama...${NC}"
if ! command -v ollama &>/dev/null; then
    warn "Ollama не найден — устанавливаю..."
    curl -fsSL https://ollama.com/install.sh | sh
    log "Ollama установлен"
else
    log "Ollama уже установлен"
fi

# 4. Node.js
echo -e "${CYAN}[4/6] Проверка Node.js...${NC}"
if ! command -v node &>/dev/null || [[ $(node -v | cut -d'v' -f2 | cut -d'.' -f1) -lt 20 ]]; then
    warn "Node.js < 20 — устанавливаю..."
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
    sudo apt install -y nodejs
    log "Node.js 20+ установлен"
else
    log "Node.js $(node -v) уже установлен"
fi

# 5. Python venv + зависимости
echo -e "${CYAN}[5/6] Настройка Python окружения...${NC}"
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    log "venv создан"
fi
source venv/bin/activate
pip install --upgrade pip setuptools wheel -q
pip install -r requirements.txt -q
log "Зависимости установлены"

# 6. SSH + .env
echo -e "${CYAN}[6/6] Настройка SSH и конфигов...${NC}"
SSH_KEY="$HOME/.ssh/kb_vps"
if [[ ! -f "$SSH_KEY" ]]; then
    ssh-keygen -t ed25519 -f "$SSH_KEY" -N "" -q
    log "SSH-ключ создан: $SSH_KEY"
fi
if [[ ! -f ".env" ]] && [[ -f ".env.example" ]]; then
    cp .env.example .env
    warn "Отредактируйте .env и укажите WEBHOOK_SECRET"
fi
log "Настройка завершена"

# Финал
echo ""
echo -e "${GREEN}╔════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 Установка завершена!          ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════╝${NC}"
echo ""
echo "📌 Следующие шаги:"
echo "1. Перезагрузите терминал (для активации группы docker)"
echo "2. Скопируйте SSH-ключ на VPS:"
echo "   ssh-copy-id -i $SSH_KEY.pub root@86.110.194.68"
echo "3. Запустите проект: ./start.sh"
echo ""