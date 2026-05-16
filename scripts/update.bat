@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

set "PROJECT_DIR=%CD%"
set "SCRIPTS_DIR=%PROJECT_DIR%\scripts"
set "VENV_DIR=%PROJECT_DIR%\venv"
set "SITE_DIR=%PROJECT_DIR%\site"
set "LOG_DIR=%PROJECT_DIR%\logs"
set "LOG_FILE=%LOG_DIR%\update.log"
set "VPS_USER=root"
set "VPS_HOST=86.110.194.68"
set "SSH_KEY=%USERPROFILE%\.ssh\kb_vps"

mkdir "%LOG_DIR%" 2>nul

echo ╔══════════════════════════════════════════════╗
echo ║  🔄 Обновление Knowledge Base                ║
echo ╚══════════════════════════════════════════════╝
echo.

:: Логирование в файл
echo [%date% %time%] Начало обновления >> "%LOG_FILE%"

:: 1. Git pull
echo [1/6] 📥 Синхронизация с репозиторием...
git pull origin main >> "%LOG_FILE%" 2>&1
if %errorlevel% neq 0 (
    echo ⚠️  Не удалось обновить репозиторий — проверьте подключение
    echo [%date% %time%] ⚠️ Git pull failed >> "%LOG_FILE%"
) else (
    echo ✅ Репозиторий обновлён
    echo [%date% %time%] ✅ Git pull success >> "%LOG_FILE%"
)

:: 2. Активация venv
echo [2/6] 🐍 Активация Python окружения...
set "PYTHON=%VENV_DIR%\Scripts\python.exe"
set "PIP=%VENV_DIR%\Scripts\pip.exe"
if not exist "%PYTHON%" set "PYTHON=%VENV_DIR%\Scripts\python3.exe"
if not exist "%PIP%" set "PIP=%VENV_DIR%\Scripts\pip3.exe"

if not exist "%PYTHON%" (
    echo ❌ Python в venv не найден
    exit /b 1
)

:: 3. Синхронизация статей
echo [3/6] 🔄 Синхронизация статей...
"%PYTHON%" "%SCRIPTS_DIR%\sync.py" >> "%LOG_FILE%" 2>&1
if %errorlevel% equ 0 (echo ✅ Статьи синхронизированы) else (echo ⚠️  sync.py вернул ошибку)

:: 4. Сборка фронтенда
echo [4/6] 📦 Сборка фронтенда...
cd "%SITE_DIR%"
call npm run build --silent >> "%LOG_FILE%" 2>&1
if %errorlevel% equ 0 (echo ✅ VitePress build завершён) else (echo ⚠️  Сборка фронтенда упала)
cd "%PROJECT_DIR%"

:: 5. Деплой на VPS
echo [5/6] 🚀 Деплой на VPS...
if exist "%SITE_DIR%\docs\.vitepress\dist\" (
    scp -o StrictHostKeyChecking=no -r "%SITE_DIR%\docs\.vitepress\dist\*" %VPS_USER%@%VPS_HOST%:/var/www/swinki.ru/dist/ >> "%LOG_FILE%" 2>&1
    if %errorlevel% equ 0 (echo ✅ Фронтенд задеплоен) else (echo ⚠️  rsync/scp не удался)
)

:: 6. Индексация (только если изменились статьи)
echo [6/6] 🧠 Проверка необходимости переиндексации...
git diff HEAD~1 HEAD --name-only 2>nul | findstr "^data/" >nul
if %errorlevel% equ 0 (
    echo 📚 Статьи изменились — запускаю индексацию...
    "%PYTHON%" "%SCRIPTS_DIR%\ingest.py" >> "%LOG_FILE%" 2>&1
    if %errorlevel% equ 0 (echo ✅ База проиндексирована) else (echo ⚠️  ingest.py вернул ошибку)
) else (
    echo ✨ Статьи не менялись — пропускаю индексацию
)

:: Финал
echo.
echo ╔══════════════════════════════════════════════╗
echo ║  🎉 Обновление завершено!                    ║
echo ╚══════════════════════════════════════════════╝
echo 🌐 Сайт:     https://swinki.ru
echo 🤖 API:      https://swinki.ru/api/ask
echo 📁 Логи:     %LOG_FILE%
echo.
echo [%date% %time%] ✅ Update completed >> "%LOG_FILE%"
pause