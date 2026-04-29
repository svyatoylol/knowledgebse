#!/bin/bash
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 🔍 Находим корень проекта (где лежит этот скрипт)
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON_DIR="$PROJECT_DIR/rag/knowledge-base"
SITE_DIR="$PROJECT_DIR/site"

# Авто-определение терминала
detect_terminal() {
    if command -v cosmic-term &> /dev/null; then echo "cosmic-term"
    elif command -v alacritty &> /dev/null; then echo "alacritty"
    elif command -v kitty &> /dev/null; then echo "kitty"
    elif command -v gnome-terminal &> /dev/null; then echo "gnome-terminal"
    else echo "none"; fi
}
TERMINAL=$(detect_terminal)
echo -e "${GREEN}🚀 Запуск (терминал: $TERMINAL)...${NC}"

# 1. Проверка сервисов
echo -e "${YELLOW}📦 Qdrant...${NC}"
docker start qdrant 2>/dev/null || docker run -d --name qdrant -p 6333:6333 qdrant/qdrant

echo -e "${YELLOW}🤖 Ollama...${NC}"
if ! curl -s http://localhost:11434 > /dev/null 2>&1; then
    echo -e "   ${RED}⚠️ Запустите: ollama serve${NC}"
fi

# 2. Python окружение
echo -e "${YELLOW}🐍 Python...${NC}"
cd "$PYTHON_DIR"
[ ! -d "venv" ] && python3 -m venv venv
source venv/bin/activate
pip install -q flask flask-cors 2>/dev/null

# 3. Синхронизация данных
echo -e "${YELLOW}🔄 Синхронизация...${NC}"
cd "$SITE_DIR"
python3 sync.py

# 4. Индексация
echo -e "${YELLOW}🧠 Индексация...${NC}"
cd "$PYTHON_DIR"
python ingest.py

# 5. Запуск серверов
echo -e "${GREEN}✨ Запуск серверов...${NC}"

run_in_terminal() {
    local title="$1"; local cmd="$2"
    case "$TERMINAL" in
        cosmic-term) cosmic-term -e bash -c "$cmd; read -p 'Нажмите Enter...'" & ;;
        alacritty) alacritty -t "$title" -e bash -c "$cmd; exec bash" & ;;
        kitty) kitty -t "$title" bash -c "$cmd; exec bash" & ;;
        gnome-terminal) gnome-terminal --title="$title" -- bash -c "$cmd; exec bash" & ;;
        *) echo -e "${RED}❌ Терминал не найден. Запустите вручную:${NC}"
           echo "   Окно 1: cd $PYTHON_DIR && source venv/bin/activate && python api.py"
           echo "   Окно 2: cd $SITE_DIR && npm run dev"
           return 1 ;;
    esac
}

run_in_terminal "🔙 API" "cd '$PYTHON_DIR' && source venv/bin/activate && python api.py"
sleep 1
run_in_terminal "🌐 Site" "cd '$SITE_DIR' && npm run dev"

echo -e "${GREEN}✅ Готово! Откройте: ${NC}http://localhost:5173"