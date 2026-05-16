@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ╔══════════════════════════════════════════════╗
echo ║  🚀 Knowledge Base — Установка (Windows)     ║
echo ╚══════════════════════════════════════════════╝
echo.

:: 1. Проверка winget
where winget >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ winget не найден. Требуется Windows 10 (21H2+) или 11.
    pause & exit /b 1
)

:: 2. Установка зависимостей
echo [1/6] Установка системных пакетов...
winget install -e --id Git.Git --accept-package-agreements --silent >nul 2>&1
winget install -e --id Python.Python.3.12 --accept-package-agreements --silent >nul 2>&1
winget install -e --id OpenJS.NodeJS.LTS --accept-package-agreements --silent >nul 2>&1
winget install -e --id Docker.DockerDesktop --accept-package-agreements --silent >nul 2>&1
winget install -e --id Ollama.Ollama --accept-package-agreements --silent >nul 2>&1
echo ✅ Пакеты установлены. Перезапустите терминал.

:: 3. Репозиторий
echo [2/7] Проверка репозитория...
if not exist "knowledgebse" (
    git clone https://github.com/svyatoylol/knowledgebse.git
    cd knowledgebse
) else (
    cd knowledgebse
)

:: 4. Python venv & зависимости
echo [3/7] Настройка Python...
if not exist "venv" (
    python -m venv venv
)
call venv\Scripts\activate.bat
python -m pip install --upgrade pip setuptools wheel >nul 2>&1
pip install -r requirements.txt >nul 2>&1
echo ✅ Python окружение готово.

:: 5. Node.js
echo [4/7] Настройка Node.js...
cd site && call npm install >nul 2>&1 && cd ..
echo ✅ Frontend зависимости установлены.

:: 6. SSH & .env
echo [5/7] Настройка SSH и конфигов...
if not exist "%USERPROFILE%\.ssh\kb_vps" (
    ssh-keygen -t ed25519 -f "%USERPROFILE%\.ssh\kb_vps" -N "" -q
)
if not exist ".env" copy .env.example .env >nul 2>&1
echo ⚠️  Отредактируйте .env (WEBHOOK_SECRET) и скопируйте ключ на VPS:
echo type "%USERPROFILE%\.ssh\kb_vps.pub" ^| ssh root@86.110.194.68 "cat >> ~/.ssh/authorized_keys"

:: 7. Финал
echo.
echo ╔══════════════════════════════════════════════╗
echo ║  🎉 Установка завершена!                     ║
echo ╚══════════════════════════════════════════════╝
echo 📌 1. Перезапустите терминал
echo 📌 2. Запустите Docker Desktop и дождитесь 🐳
echo 📌 3. Скопируйте SSH-ключ на VPS (команда выше)
echo 📌 4. Выполните: start.bat
pause