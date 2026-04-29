#!/usr/bin/env python3
import requests
import json
import sys
from pathlib import Path

OLLAMA_URL = "http://127.0.0.1:11434"
QDRANT_URL = "http://127.0.0.1:6333"
COLLECTION_NAME = "my_kb_local"
LLM_MODEL = "llama3.2:3b"
EMBEDDING_MODEL = "mxbai-embed-large"
TOP_K = 5
MIN_SCORE = 0.2  
def _extract_text(payload: dict) -> str:
    """Извлекает текст из payload (учитывает формат llama-index)"""
    # Прямой текст
    if payload.get("text"):
        return payload["text"]
    
    # llama-index: текст в _node_content как JSON-строка
    if "_node_content" in payload:
        try:
            node = json.loads(payload["_node_content"])
            if node.get("text"):
                return node["text"]
        except:
            pass
    
    # Фолбэк: склеиваем все текстовые поля
    parts = [str(v) for k, v in payload.items() 
             if k not in ("_node_content", "embedding") and isinstance(v, (str, int, float))]
    return " ".join(parts)[:2000]

def get_answer(question: str) -> str:
    try:
        print(f"🔍 Поиск: '{question}'")
        
        # 1. Эмбеддинг вопроса
        embed_resp = requests.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBEDDING_MODEL, "input": [question]},
            timeout=30
        )
        embed_resp.raise_for_status()
        question_vector = embed_resp.json()["embeddings"][0]

        # 2. Поиск в Qdrant с порогом релевантности
        search_resp = requests.post(
            f"{QDRANT_URL}/collections/{COLLECTION_NAME}/points/search",
            json={
                "vector": question_vector,
                "limit": TOP_K,
                "with_payload": True,
                "score_threshold": MIN_SCORE  # 🔥 Фильтруем слабые совпадения
            },
            timeout=30
        )
        search_resp.raise_for_status()
        results = search_resp.json()["result"]

        print(f"📄 Найдено {len(results)} фрагментов (score >= {MIN_SCORE})")

        if not results:
            return "❌ В базе знаний не найдено информации по вашему вопросу. Попробуйте сформулировать иначе."

        # 3. Формируем контекст с отладочной информацией
        context_parts = []
        for i, r in enumerate(results, 1):
            payload = r.get("payload", {})
            text = _extract_text(payload)
            score = r.get("score", 0)
            if text and len(text.strip()) > 20:  # 🔥 Игнорируем слишком короткие фрагменты
                context_parts.append(f"[{i}] (score: {score:.3f}) {text.strip()}")
                print(f"   📋 [{i}] score={score:.3f}: {text[:100]}...")
        
        context = "\n\n".join(context_parts)
        
        if not context:
            return "❌ Не удалось извлечь текст из найденных документов."

        # 4. промпт с жёсткими инструкциями
        prompt = f"""Ты — помощник по базе знаний на русском языке.

ПРАВИЛА:
1. Отвечай ТОЛЬКО на основе контекста ниже.
2. Если в контексте нет ответа на вопрос — честно скажи: "В базе знаний нет информации по этому вопросу".
3. Не выдумывай факты, не используй внешние знания.
4. Отвечай подробно, но только если контекст позволяет.

КОНТЕКСТ ИЗ БАЗЫ ЗНАНИЙ:
{context}

ВОПРОС ПОЛЬЗОВАТЕЛЯ: {question}

ОТВЕТ:"""

        # 5. Запрос к LLM
        llm_resp = requests.post(
            f"{OLLAMA_URL}/api/generate",
            json={"model": LLM_MODEL, "prompt": prompt, "stream": False, "options": {"temperature": 0.1}},
            timeout=120
        )
        llm_resp.raise_for_status()
        answer = llm_resp.json().get("response", "").strip()
        
        # 6. Пост-обработка: если ответ бессмысленный — заменяем
        if len(answer) < 10 or any(bad in answer.lower() for bad in ["господи помилуй", "colecciones", "no specific"]):
            return "⚠️ Не удалось сформировать осмысленный ответ. Попробуйте перефразировать вопрос."
        
        return answer

    except requests.exceptions.ConnectionError:
        return "❌ Не удалось соединиться с сервером. Проверьте, запущены ли Ollama и Qdrant."
    except Exception as e:
        print(f"❌ Ошибка: {type(e).__name__}: {e}")
        return f"❌ Произошла ошибка: {str(e)}"

if __name__ == "__main__":
    print(f"🤖 RAG Чат | Модель: {LLM_MODEL}")
    print("-" * 60)
    while True:
        try:
            q = input("\n❓ Вопрос: ").strip()
            if q.lower() in ("exit", "quit", "выход", "q"): 
                print("👋 До свидания!"); break
            if not q: continue
            print("🤔 Думаю...")
            answer = get_answer(q)
            print(f"\n💡 {answer}")
            print("-" * 60)
        except KeyboardInterrupt:
            print("\n👋 Выход"); break