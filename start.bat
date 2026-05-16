@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0knowledgebse"

set VPS=86.110.194.68
set SSH_KEY=%USERPROFILE%\.ssh\kb_vps
set PYTHON_DIR=rag\knowledge-base
set SITE_DIR=site

echo ╔══════════════════════════════════════════════╗
echo ║  🚀 Запуск Knowledge Base (Windows)          ║
echo ╚══════════════════════════════════════════════╝
echo.

:: 0. Очистка портов
echo [##------------------]  10%% | Очистка портов...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill //PID %%a //F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :25000 ^| findstr LISTENING') do taskkill //PID %%a //F >nul 2>&1
timeout /t 2 /nobreak >nul
echo ✅ Порты очищены

:: 1. Туннели
echo [####----------------]  20%% | Подключение SSH-туннелей...
taskkill /f /im ssh.exe >nul 2>&1
timeout /t 2 /nobreak >nul
start /min "Tunnel-API" ssh -i "%SSH_KEY%" -o StrictHostKeyChecking=no -R 0.0.0.0:8000:localhost:8000 -N -o ServerAliveInterval=30 root@%VPS%
start /min "Tunnel-WH" ssh -i "%SSH_KEY%" -o StrictHostKeyChecking=no -R 0.0.0.0:25000:localhost:25000 -N -o ServerAliveInterval=30 root@%VPS%
timeout /t 5 /nobreak >nul
curl -s http://127.0.0.1:8000/ >nul 2>&1 && echo ✅ API-туннель активен || echo ⚠️  API-туннель не активен
curl -s http://127.0.0.1:25000/ >nul 2>&1 && echo ✅ Webhook-туннель активен || echo ⚠️  Webhook-туннель не активен

:: 2. Qdrant
echo [######--------------]  30%% | Проверка Qdrant...
docker ps --format "{{.Names}}" | findstr "qdrant" >nul 2>&1
if %errorlevel% neq 0 (
    docker run -d --name qdrant -p 6333:6333 -p 6334:6334 -v "%CD%\qdrant_storage:/qdrant/storage" --restart unless-stopped qdrant/qdrant:latest >nul 2>&1
    timeout /t 5 /nobreak >nul
)
curl -s http://localhost:6333/ >nul 2>&1 && echo ✅ Qdrant готов || echo ⚠️  Qdrant не отвечает

:: 3. Ollama
echo [########------------]  40%% | Проверка Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1 && echo ✅ Ollama готов || echo ⚠️  Запустите Ollama!

:: 4. Python
echo [##########----------]  50%% | Настройка Python...
if not exist "%PYTHON_DIR%\venv" (
    cd "%PYTHON_DIR%" && python -m venv venv && cd ..
)
call "%PYTHON_DIR%\venv\Scripts\activate"
pip install -q flask flask-cors requests llama-index llama-index-core llama-index-embeddings-ollama llama-index-llms-ollama llama-index-vector-stores-qdrant==0.1.4 "numpy<2" python-dotenv pypdf >nul 2>&1
echo ✅ Зависимости установлены

:: 5. Синхронизация
echo [############--------]  60%% | Синхронизация данных...
python "%SITE_DIR%\sync.py" >nul 2>&1 && echo ✅ Данные синхронизированы || echo ⚠️  sync.py упал

:: 6. Индексация
echo [##############------]  70%% | Индексация...
python "%PYTHON_DIR%\ingest.py" >nul 2>&1 && echo ✅ База проиндексирована || echo ⚠️  ingest.py упал

:: 7. Сборка & Деплой
echo [################----]  80%% | Сборка и деплой...
cd "%SITE_DIR%"
call npm run build --silent >nul 2>&1
cd ..
:: Windows-аналог rsync: scp (требует настроенный SSH-ключ)
if exist "%SITE_DIR%\docs\.vitepress\dist\" (
    scp -o StrictHostKeyChecking=no -r "%SITE_DIR%\docs\.vitepress\dist\*" root@%VPS%:/var/www/swinki.ru/dist/ >nul 2>&1 && echo ✅ Фронтенд задеплоен || echo ⚠️  Деплой пропущен (проверьте SSH-ключ)
)

:: 8. Сервисы
echo [##################--]  90%% | Запуск сервисов...
start "🔙 API" cmd /k "cd /d "%CD%\%PYTHON_DIR%" && call venv\Scripts\activate && python api.py"
timeout /t 2 /nobreak >nul
if exist "webhook-listener.py" (
    start "📡 Webhook" cmd /k "cd /d "%CD%" && call "%PYTHON_DIR%\venv\Scripts\activate" && python webhook-listener.py"
    echo ✅ Webhook запущен
) else (
    echo ⚠️  webhook-listener.py не найден
)

:: Финал
echo.
echo [####################] 100%% | Готово!
echo ╔══════════════════════════════════════════════╗
echo ║  🎉 Все сервисы запущены!                    ║
echo ╚══════════════════════════════════════════════╝
echo 🌐 Сайт:    https://swinki.ru
echo 🤖 API:     http://localhost:8000
echo 🎣 Webhook: http://localhost:25000
echo 💡 Закройте окна терминалов для остановки.
pause >nul