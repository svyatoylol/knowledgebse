#!/usr/bin/env python3
"""
Webhook listener для GitHub Actions.
📍 Расположение: scripts/webhook-listener.py
✅ Плоская структура: логи в logs/, пути от корня проекта
"""
import http.server, subprocess, json, os, hashlib, hmac, sys, logging, threading
from pathlib import Path
from dotenv import load_dotenv

# 🔗 Пути: scripts/ -> корень проекта
SCRIPTS_DIR = Path(__file__).parent.resolve()  # 📍 scripts/
PROJECT_ROOT = SCRIPTS_DIR.parent              # 📍 корень проекта
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 🔐 Загружаем .env из корня проекта
load_dotenv(PROJECT_ROOT / ".env")

# 🔐 Настройки
SECRET = os.getenv("WEBHOOK_SECRET", "").encode()
if not SECRET:
    print("❌ WEBHOOK_SECRET не задан в .env!", file=sys.stderr)
    sys.exit(1)

UPDATE_SCRIPT = SCRIPTS_DIR / "update.sh"  # 📍 scripts/update.sh
PORT = int(os.getenv("WEBHOOK_PORT", "25000"))

# 📝 Логирование в файл + консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "webhook.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def verify_signature(payload: bytes, signature: str) -> bool:
    """Проверяет HMAC-SHA256 подпись от GitHub"""
    if not signature or not signature.startswith("sha256="):
        return False
    expected = "sha256=" + hmac.new(SECRET, payload, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, expected)

def run_update_async():
    """Запускает update.sh в отдельном потоке"""
    try:
        logger.info("🔄 [ASYNC] Запуск update.sh...")
        result = subprocess.run(
            ["bash", str(UPDATE_SCRIPT)],  # 🔥 Явно указываем bash для .sh скриптов
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            env={**os.environ, "PYTHONUNBUFFERED": "1"},
            timeout=1800
        )
        if result.returncode == 0:
            logger.info("✅ [ASYNC] Обновление завершено!")
        else:
            stderr_snippet = result.stderr[:500] if result.stderr else "нет вывода"
            logger.error(f"❌ [ASYNC] Ошибка (код {result.returncode}): {stderr_snippet}")
    except subprocess.TimeoutExpired:
        logger.error("❌ [ASYNC] Таймаут: update.sh выполнялся дольше 30 минут")
    except Exception as e:
        logger.error(f"❌ [ASYNC] Критическая ошибка: {type(e).__name__}: {e}")

class Handler(http.server.BaseHTTPRequestHandler):
    protocol_version = 'HTTP/1.1'
    
    def log_message(self, *args): pass  # Отключаем стандартный спам
    
    def _send(self, code: int, body: dict):
        """Отправляет JSON-ответ с правильными заголовками"""
        response = json.dumps(body).encode()
        self.send_response(code)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Content-Length', len(response))
        self.send_header('Connection', 'close')
        self.end_headers()
        self.wfile.write(response)
        self.wfile.flush()
    
    def do_GET(self):
        """Health check endpoint"""
        if self.path == "/health":
            self._send(200, {"status": "ok", "service": "webhook-listener"})
        else:
            self._send(404, {"error": "not found"})
    
    def do_POST(self):
        """Обработка webhook от GitHub"""
        try:
            length = int(self.headers.get('Content-Length', 0))
            payload = self.rfile.read(length)
            signature = self.headers.get("X-Hub-Signature-256", "")
            
            # 🔐 Проверка подписи
            if not verify_signature(payload, signature):
                logger.warning(f"❌ Invalid signature from {self.client_address[0]}")
                self._send(403, {"error": "invalid signature"})
                return
            
            data = json.loads(payload)
            
            # Игнорируем пуши не в main
            if data.get("ref") != "refs/heads/main":
                logger.info(f"⏭ Игнорирую пуш в {data.get('ref')}")
                self._send(200, {"status": "ignored"})
                return
            
            repo_name = data.get("repository", {}).get("full_name", "unknown")
            logger.info(f"🔄 Push в main от {repo_name}")
            
            # 🔥 СРАЗУ отвечаем 202 — до запуска update.sh!
            self._send(202, {"status": "accepted", "message": "update started"})
            
            # 🔥 Потом запускаем обновление в фоне (не блокируя ответ)
            threading.Thread(target=run_update_async, daemon=True).start()
            
        except json.JSONDecodeError:
            logger.error("❌ Invalid JSON payload")
            self._send(400, {"error": "invalid JSON"})
        except Exception as e:
            logger.error(f"❌ Handler error: {type(e).__name__}: {e}", exc_info=True)
            try:
                self._send(500, {"error": "internal server error"})
            except:
                pass

def main():
    # Проверка наличия update.sh
    if not UPDATE_SCRIPT.exists():
        logger.error(f"❌ Скрипт не найден: {UPDATE_SCRIPT}")
        logger.error("💡 Убедитесь, что webhook-listener.py и update.sh лежат в scripts/")
        sys.exit(1)
    
    # Проверка прав на выполнение
    if not os.access(UPDATE_SCRIPT, os.X_OK):
        logger.warning(f"⚠️  update.sh не имеет прав на выполнение — пытаюсь исправить...")
        try:
            os.chmod(UPDATE_SCRIPT, 0o755)
            logger.info("✅ Права установлены")
        except Exception as e:
            logger.error(f"❌ Не удалось установить права: {e}")
    
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    logger.info(f"🎣 Webhook listener запущен на порту {PORT}")
    logger.info(f"📁 PROJECT_ROOT: {PROJECT_ROOT}")
    logger.info(f"📜 UPDATE_SCRIPT: {UPDATE_SCRIPT}")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("👋 Остановка по сигналу...")
        server.shutdown()
    except OSError as e:
        if "Address already in use" in str(e):
            logger.error(f"❌ Порт {PORT} занят! Проверьте: lsof -i :{PORT}")
        else:
            raise

if __name__ == "__main__":
    main()