#!/usr/bin/env python3
"""
query.py — Прямой поиск: Ollama API + Qdrant
Исправлено для qdrant-client >= 1.5.0
"""
import os
import sys
import json
import requests
from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

# 🔹 КОНФИГУРАЦИЯ (должна совпадать с ingest.py)
EMBEDDING_MODEL = "mxbai-embed-large"
OLLAMA_URL = "http://localhost:11434"
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "my_kb_local"
LLM_MODEL = "llama3.2:3b"
TOP_K = 5

print(f"🔗 Локальный чат: {LLM_MODEL} + {EMBEDDING_MODEL}")

# 🔹 Проверка подключения
try:
    requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
    client = QdrantClient(url=QDRANT_URL)
    if not client.collection_exists(COLLECTION_NAME):
        print(f"❌ Коллекция '{COLLECTION_NAME}' не найдена!")
        print("💡 Сначала запустите: python ingest.py")
        sys.exit(1)
    print("✅ Подключено к Ollama и Qdrant")
except Exception as e:
    print(f"❌ Ошибка подключения: {e}")
    sys.exit(1)

# 🔹 Функции для API-вызовов
def get_embedding(text: str) -> list[float]:
    """Получение эмбеддинга через Ollama API"""
    if len(text) > 500:
        text = text[:500]
    resp = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMBEDDING_MODEL, "input": text},
        timeout=30
    )
    if resp.status_code != 200:
        raise Exception(f"Embed API error: {resp.text}")
    return resp.json()["embeddings"][0]

def search_qdrant(query_vector: list[float], top_k: int = TOP_K) -> list[dict]:
    """Поиск похожих чанков в Qdrant (исправлено для новой версии клиента)"""
    try:
        # 🔹 Новый API: query_points (qdrant-client >= 1.5)
        result = client.query_points(
            collection_name=COLLECTION_NAME,
            query=query_vector,
            limit=top_k,
            with_payload=True,
            with_vectors=False
        )
        points = result.points if hasattr(result, 'points') else result
    except AttributeError:
        # 🔹 Старый API: search (qdrant-client < 1.5)
        points = client.search(
            collection_name=COLLECTION_NAME,
            query_vector=query_vector,
            limit=top_k,
            with_payload=True,
            with_vectors=False
        )
    
    return [
        {
            "text": p.payload.get("text", "") if p.payload else "",
            "source": p.payload.get("source", "unknown") if p.payload else "unknown",
            "score": p.score if hasattr(p, 'score') else 0
        }
        for p in points
    ]

def generate_answer(question: str, context: str) -> str:
    """Генерация ответа через Ollama Generate API"""
    prompt = f"""Ты — помощник по базе знаний. Ответь на вопрос, используя контекст ниже.
Если в контексте нет ответа, так и скажи.

Контекст:
{context}

Вопрос: {question}

Ответ:"""
    
    resp = requests.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
        timeout=120
    )
    if resp.status_code != 200:
        raise Exception(f"Generate API error: {resp.text}")
    return resp.json().get("response", "Нет ответа")

# 🔹 Интерактивный цикл
print("\n🤖 База знаний готова. Введите 'exit' для выхода.")
print("-" * 60)

while True:
    try:
        question = input("\n❓ Ваш вопрос: ").strip()
        if question.lower() in ("exit", "quit", "выход", "q", ""):
            break
        if not question:
            continue
            
        print("🔍 Поиск...")
        
        # 1. Эмбеддинг вопроса
        query_vec = get_embedding(question)
        
        # 2. Поиск в Qdrant
        results = search_qdrant(query_vec)
        if not results:
            print("💡 Ничего не найдено. Попробуйте перефразировать.")
            continue
            
        # 3. Подготовка контекста
        context = "\n\n".join([f"[{r['source']}] {r['text']}" for r in results])
        
        # 4. Генерация ответа
        print("🤔 Думаю...")
        answer = generate_answer(question, context)
        
        print(f"\n💡 Ответ: {answer.strip()}")
        
        # 5. Источники
        print("\n📎 Источники:")
        for i, r in enumerate(results, 1):
            preview = r["text"][:100].replace('\n', ' ') + "..."
            print(f"  {i}. {r['source']} (score: {r['score']:.3f})\n     «{preview}»")
            
    except KeyboardInterrupt:
        print("\n👋 Прервано")
        break
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        # Для отладки: раскомментируйте строку ниже
        # import traceback; traceback.print_exc()