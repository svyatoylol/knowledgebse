@echo off
chcp 65001 > nul
color 0A

:: 🔍 Находим корень проекта (где лежит этот батник)
set "PROJECT_DIR=%~dp0"
set "PYTHON_DIR=%PROJECT_DIR%rag\knowledge-base"
set "SITE_DIR=%PROJECT_DIR%site"

echo 🚀 Запуск системы...
echo.

:: 1. Проверка сервисов
echo 📦 Qdrant...
docker start qdrant 2>nul
if %errorlevel% neq 0 (
    echo    ⚠️ Qdrant не запущен. Пытаемся создать контейнер...
    docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
)

echo 🤖 Ollama...
curl -s http://localhost:11434 > nul 2>&1
if %errorlevel% neq 0 (
    echo    ⚠️ Ollama не отвечает. Запустите вручную: ollama serve
)

:: 2. Python окружение
echo 🐍 Python...
if not exist "%PYTHON_DIR%\venv" (
    echo    ️ Создаем виртуальное окружение...
    python -m venv "%PYTHON_DIR%\venv"
)
call "%PYTHON_DIR%\venv\Scripts\activate.bat"
pip install -q flask flask-cors >nul 2>&1

:: 3. Синхронизация данных
echo 🔄 Синхронизация...
cd /d "%SITE_DIR%"
python sync.py

:: 4. Индексация
echo 🧠 Индексация...
cd /d "%PYTHON_DIR%"
python ingest.py

:: 5. Запуск серверов
echo ✨ Запуск серверов...
echo.

:: Окно 1: API (открывается в новом окне)
start "🔙 API" cmd /k "cd /d "%PYTHON_DIR%" && call venv\Scripts\activate.bat && python api.py"

timeout /t 2 >nul

:: Окно 2: Сайт (открывается в новом окне)
start "🌐 Site" cmd /k "cd /d "%SITE_DIR%" && npm run dev"

echo.
echo ✅ Готово! Откройте: http://localhost:5173
echo.
pause
