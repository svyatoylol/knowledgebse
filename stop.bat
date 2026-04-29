@echo off
chcp 65001 > nul
color 0C

:: 🔍 Находим корень проекта
set "PROJECT_DIR=%~dp0"
set "PYTHON_DIR=%PROJECT_DIR%rag\knowledge-base"
set "SITE_DIR=%PROJECT_DIR%site"

echo 🛑 Остановка системы...
echo.

:: 1. Остановка Qdrant (Docker)
echo 📦 Qdrant...
docker stop qdrant 2>nul
if %errorlevel% equ 0 (
    echo    ✅ Остановлен
) else (
    echo    ⚠️ Не найден или уже остановлен
)

:: 2. Остановка Python процессов (api.py)
echo 🔙 API Server...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq 🔙 API*" 2>nul
taskkill /F /IM pythonw.exe /FI "WINDOWTITLE eq 🔙 API*" 2>nul
:: Фолбэк: убиваем все процессы с api.py в командной строке
wmic process where "commandline like '%%api.py%%'" delete 2>nul
echo    ✅ Процессы api.py завершены

:: 3. Остановка VitePress / Node процессов
echo 🌐 VitePress...
taskkill /F /IM node.exe /FI "WINDOWTITLE eq 🌐 Site*" 2>nul
:: Фолбэк: убиваем процессы с vitepress в командной строке
wmic process where "commandline like '%%vitepress%%'" delete 2>nul
echo    ✅ Процессы VitePress завершены

:: 4. Очистка портов (если что-то зависло)
echo 🧹 Очистка портов...
:: Порт 6333 (Qdrant)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :6333 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)
:: Порт 5173 (VitePress)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5173 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)
:: Порт 5000 (Flask API)
for /f "tokens=5" %%a in ('netstat -aon ^| findstr :5000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a 2>nul
)
echo    ✅ Порты освобождены

:: 5. Деактивация виртуального окружения (если активно в текущем окне)
if defined VIRTUAL_ENV (
    echo 🐍 Python venv...
    call deactivate 2>nul
    echo    ✅ Деактивировано
)

echo.
echo ✅ Система остановлена.
echo.
pause
