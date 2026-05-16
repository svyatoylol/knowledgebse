#!/usr/bin/env bash
set -euo pipefail

# === 🎨 Логирование ===
GREEN='\033[0;32m'; YELLOW='\033[1;33m'; RED='\033[0;31m'; CYAN='\033[0;36m'; NC='\033[0m'
step() { echo -e "\n${CYAN}📦 [ШАГ $1] ${2}${NC}"; }
ok() { echo -e "${GREEN}   ✅ $1${NC}"; }
warn() { echo -e "${YELLOW}   ⚠️  $1${NC}"; }
err() { echo -e "${RED}   ❌ $1${NC}"; exit 1; }

# === 🔐 Проверка прав ===
if [[ $EUID -eq 0 ]]; then
    err "Запустите этот скрипт от имени обычного пользователя (не root)!"
fi

if [[ ! -f /etc/debian_version ]]; then
    warn "Скрипт оптимизирован для Ubuntu/Debian/Pop!_OS. На других ОС шаги могут отличаться."
fi

# === 1. Система ===
step 1 "Обновление и базовые утилиты"
sudo apt update && sudo apt upgrade -y
sudo apt install -y git curl wget build-essential jq openssl rsync
ok "Пакеты установлены"

# === 2. Docker ===
step 2 "Установка Docker"
if command -v docker &>/dev/null; then
    ok "Docker уже установлен ($(docker --version))"
else
    sudo apt install -y docker.io
    sudo systemctl enable --now docker
    sudo usermod -aG docker "$USER"
    ok "Docker установлен. Перезагрузитесь для активации прав: sudo reboot"
fi

# === 3. Ollama ===
step 3 "Установка Ollama (LLM)"
if command -v ollama &>/dev/null; then
    ok "Ollama уже установлен"
else
    curl -fsSL https://ollama.com/install.sh | sh
    ok "Ollama установлен"
fi

# === 4. Node.js ===
step 4 "Установка Node.js 20+"
if command -v node &>/dev/null; then
    NODE_MAJOR=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
    if [[ $NODE_MAJOR -ge 20 ]]; then
        ok "Node.js уже установлен ($(node -v))"
    else
        curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
        sudo apt install -y nodejs
        ok "Node.js обновлён до 20+"
    fi
else
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -
    sudo apt install -y nodejs
    ok "Node.js установлен"
fi

# === 5. Проект ===
step 5 "Подготовка репозитория"
if [[ ! -f "./start.sh" ]]; then
    read -rp "🔗 URL репозитория (Enter для default): " REPO_URL
    REPO_URL="${REPO_URL:-https://github.com/svyatoylol/knowledgebse.git}"
    git clone "$REPO_URL" knowledge-base
    cd knowledge-base
fi
ok "Рабочая директория: $(pwd)"

# === 6. SSH для VPS ===
step 6 "Настройка SSH-подключения к VPS"
read -rp "🌐 IP-адрес VPS (Enter для 86.110.194.68): " VPS_IP
VPS_IP="${VPS_IP:-86.110.194.68}"
SSH_KEY="$HOME/.ssh/kb_vps"

if [[ ! -f "$SSH_KEY" ]]; then
    ssh-keygen -t ed25519 -f "$SSH_KEY" -N "" -q
    ok "SSH-ключ создан: $SSH_KEY"
else
    ok "SSH-ключ уже существует"
fi

echo -e "\n${YELLOW}🔑 Введите пароль root от VPS для копирования ключа:${NC}"
if ssh-copy-id -i "$SSH_KEY.pub" "root@$VPS_IP" 2>/dev/null; then
    ok "Ключ успешно добавлен на VPS"
else
    warn "Не удалось автоматически добавить ключ. Выполните вручную:"
    echo "   ssh-copy-id -i $SSH_KEY.pub root@$VPS_IP"
fi

# Обновляем IP в скриптах, если отличается от дефолтного
if [[ "$VPS_IP" != "86.110.194.68" ]]; then
    sed -i "s/root@86\.110\.194\.68/root@$VPS_IP/g" start.sh scripts/update.sh 2>/dev/null || true
    ok "IP VPS обновлён в скриптах"
fi

# === 7. Переменные окружения ===
step 7 "Настройка .env"
if [[ -f ".env.example" && ! -f ".env" ]]; then
    cp .env.example .env
    ok "Файл .env создан"
    warn "⚠️  Обязательно отредактируйте .env и укажите WEBHOOK_SECRET!"
    echo -e "   ${YELLOW}nano .env${NC}"
fi

# === 8. Финал ===
step 8 "Права и завершение"
chmod +x start.sh stop.sh scripts/*.sh 2>/dev/null || true
ok "Права на скрипты установлены"

echo -e "\n${GREEN}╔════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  🎉 Установка успешно завершена!    ║${NC}"
echo -e "${GREEN}╚════════════════════════════════════╝${NC}"
echo -e "\n${CYAN}📋 Что делать дальше:${NC}"
echo "1. Перезагрузите компьютер (обязательно для Docker):"
echo "   sudo reboot"
echo "2. После перезагрузки перейдите в папку проекта:"
echo "   cd ~/knowledge-base  # или ваша папка"
echo "3. Запустите проект:"
echo "   ./start.sh"
echo -e "\n${YELLOW}⏱️  Первый запуск займёт 5-15 минут (скачивание моделей и Docker-образа)${NC}"
echo -e "${GREEN}🚀 Готово!${NC}\n"