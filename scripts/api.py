#!/usr/bin/env python3
"""
Flask API для Knowledge Base — с поддержкой стриминга и корректными путями.
📍 Расположение: scripts/api.py
"""
from flask import Flask, request, jsonify, Response, stream_with_context
from flask_cors import CORS
from pathlib import Path
import sys, os, time, logging, json
from dotenv import load_dotenv

# 🔗 Пути: scripts/ -> корень проекта
SCRIPTS_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPTS_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 🔧 Добавляем scripts/ в путь для импорта локальных модулей (query.py и др.)
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

# 🔐 Загружаем .env из корня
load_dotenv(PROJECT_ROOT / ".env")

# 📝 Логирование в файл + консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "api.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# 🔥 Импорт локального модуля (query.py должен лежать в scripts/)
try:
    from query import get_answer
except ImportError as e:
    logger.error(f"❌ Не удалось импортировать get_answer: {e}")
    logger.error("💡 Убедитесь, что query.py находится в папке scripts/")
    sys.exit(1)

app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173", 
    "https://swinki.ru",
    "https://www.swinki.ru"
])

@app.route('/health', methods=['GET'])
def health():
    return jsonify({"status": "ok", "service": "kb-api"}), 200

@app.route('/api/ask', methods=['POST'])
def ask():
    start_time = time.time()
    try:
        if not request.is_json:
            return jsonify({"error": "Content-Type должен быть application/json"}), 400
            
        question = request.json.get('question', '').strip()
        if not question:
            return jsonify({"error": "Пустой вопрос"}), 400
        
        # 🔥 Поддержка стриминга через ?stream=true
        stream = request.args.get('stream', 'false').lower() == 'true'
        
        if stream:
            def generate():
                try:
                    answer = get_answer(question, stream=True)
                    yield json.dumps({
                        "success": True, 
                        "answer": answer, 
                        "meta": {"time_sec": round(time.time() - start_time, 2)}
                    }) + "\n"
                except Exception as e:
                    logger.error(f"❌ Stream error: {e}")
                    yield json.dumps({"success": False, "error": str(e)}) + "\n"
            return Response(stream_with_context(generate()), mimetype='application/json')
        else:
            logger.info(f"📥 Вопрос: {question[:200]}...")
            answer = get_answer(question, stream=False)
            elapsed = time.time() - start_time
            logger.info(f"✅ Ответ за {elapsed:.2f}с | Длина: {len(answer)} симв.")
            return jsonify({
                "success": True, 
                "answer": answer, 
                "meta": {"time_sec": round(elapsed, 2)}
            })
            
    except Exception as e:
        elapsed = time.time() - start_time
        logger.error(f"❌ API error ({elapsed:.2f}s): {type(e).__name__}: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    logger.info(f"🚀 API запущен: http://0.0.0.0:8000")
    logger.info(f"📁 PROJECT_ROOT: {PROJECT_ROOT}")
    logger.info(f"🤖 Модель: {os.getenv('OLLAMA_MODEL', 'qwen2.5:7b')} | Стриминг: ✅")
    app.run(host='0.0.0.0', port=8000, debug=False)