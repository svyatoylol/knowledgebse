#!/usr/bin/env python3
from flask import Flask, request, jsonify
from flask_cors import CORS
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

# Импортируем get_answer из query.py
from query import get_answer

app = Flask(__name__)
CORS(app, origins=["http://localhost:5173", "http://127.0.0.1:5173"])

@app.route('/api/ask', methods=['POST'])
def ask():
    try:
        question = request.json.get('question', '').strip()
        if not question:
            return jsonify({"error": "Пустой вопрос"}), 400
        
        print(f"📥 Вопрос: {question}")
        answer = get_answer(question)  # 🔑 Вызываем ту же функцию, что и в терминале
        return jsonify({"success": True, "answer": answer})
    except Exception as e:
        print(f"❌ API error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 API: http://0.0.0.0:8000")
    app.run(host='0.0.0.0', port=8000)