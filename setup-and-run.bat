@echo off
chcp 65001 >nul
echo ========================================================
echo    Полная установка и запуск Knowledge Base
echo ========================================================
echo.

cd /d "%~dp0"

:: ==================== 1. ПРОВЕРКА СЕРВИСОВ ====================
echo [1/6] Проверка Docker и Ollama...
docker ps >nul 2>&1
if %errorlevel% neq 0 (
    echo ⚠️ Docker не запущен! Откройте Docker Desktop и повторите.
    pause & exit /b 1
)
docker start qdrant 2>nul || docker run -d --name qdrant -p 6333:6333 qdrant/qdrant
curl -s http://localhost:11434 >nul 2>&1 || echo ⚠️ Ollama не отвечает. Запустите: ollama serve
echo.

:: ==================== 2. BACKEND ====================
echo [2/6] Настройка Python backend...
cd /d "%~dp0\rag\knowledge-base"
if exist venv rmdir /s /q venv
python -m venv venv
call venv\Scripts\activate
python -m pip install --upgrade pip >nul

if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo ⚠️ requirements.txt не найден, ставим вручную...
    pip install flask flask-cors requests llama-index llama-index-core llama-index-embeddings-ollama llama-index-llms-ollama llama-index-vector-stores-qdrant==0.1.4 "numpy<2" python-dotenv pypdf
)
echo ✅ Backend готов.
echo.

:: ==================== 3. ДАННЫЕ ====================
echo [3/6] Синхронизация статей...
cd /d "%~dp0\site"
python sync.py
echo.

echo [4/6] Индексация в Qdrant...
cd /d "%~dp0\rag\knowledge-base"
python ingest.py
echo.

:: ==================== 4. FRONTEND ====================
echo [5/6] Настройка Frontend...
cd /d "%~dp0\site"
if exist node_modules rmdir /s /q node_modules
npm install
echo ✅ Frontend готов.
echo.

:: ==================== 5. ЗАПУСК ====================
echo [6/6] Запуск серверов...

start "🔙 Backend - API" cmd /k "cd /d "%~dp0\rag\knowledge-base" && call venv\Scripts\activate && python api.py"
timeout /t 2 >nul
start "🌐 Frontend - VitePress" cmd /k "cd /d "%~dp0\site" && npm run dev"

echo.
echo ========================================================
echo ✅ ГОТОВО! Откройте: http://localhost:5173
echo 💡 Чтобы остановить: закройте окна или запустите stop.bat
echo ========================================================
pause