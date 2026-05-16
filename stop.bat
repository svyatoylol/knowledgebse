@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion
cd /d "%~dp0"

echo ╔══════════════════════════════════════════════╗
echo ║  🛑 Остановка Knowledge Base                 ║
echo ╚══════════════════════════════════════════════╝
echo.

:: 1. SSH-туннели
echo 🔹 Остановка туннелей...
taskkill /f /im ssh.exe >nul 2>&1
if !errorlevel! equ 0 (echo ✅ Туннели остановлены) else (echo ⚠️  Туннели не были активны)

:: 2. Python-сервисы (по заголовкам окон)
echo 🔹 Остановка сервисов...
taskkill /f /fi "WINDOWTITLE eq 🔙 API" /im cmd.exe >nul 2>&1
taskkill /f /fi "WINDOWTITLE eq 📡 Webhook" /im cmd.exe >nul 2>&1
echo ✅ Сервисы остановлены

:: 3. Очистка портов (самый надёжный способ)
echo 🔹 Очистка портов...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000 ^| findstr LISTENING') do taskkill //PID %%a //F >nul 2>&1
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :25000 ^| findstr LISTENING') do taskkill //PID %%a //F >nul 2>&1
echo ✅ Порты очищены

:: 4. Проверка
echo 🔹 Проверка...
timeout /t 2 /nobreak >nul
netstat -ano | findstr :8000 | findstr LISTENING >nul 2>&1 && (echo ⚠️  Порт 8000 всё ещё занят) || (echo ✅ Порт 8000 свободен)
netstat -ano | findstr :25000 | findstr LISTENING >nul 2>&1 && (echo ⚠️  Порт 25000 всё ещё занят) || (echo ✅ Порт 25000 свободен)

echo.
echo ✅ Готово! Все сервисы остановлены.
pause >nul