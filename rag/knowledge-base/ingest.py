#!/usr/bin/env python3
"""
ingest.py — Прямая индексация: Ollama API + Qdrant
Без сложных обёрток — максимум надёжности
"""
import os
import sys
import json
import requests
import hashlib
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import TokenTextSplitter
from qdrant_client import QdrantClient, models
from qdrant_client.http import models as qmodels

# 🔹 КОНФИГУРАЦИЯ
EMBEDDING_MODEL = "mxbai-embed-large"
EMBEDDING_DIM = 1024
OLLAMA_URL = "http://localhost:11434"
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "my_kb_local"
CHUNK_SIZE = 128
CHUNK_OVERLAP = 16

print(f"🤖 Индексация: {EMBEDDING_MODEL} → Qdrant")

# 🔹 Проверка Ollama
try:
    resp = requests.get(f"{OLLAMA_URL}/api/tags", timeout=3)
    if resp.status_code != 200:
        raise Exception("Ollama не отвечает")
    print(f"✅ Ollama работает")
except Exception as e:
    print(f"❌ {e}\n💡 Запустите: ollama serve")
    sys.exit(1)

# 🔹 Загрузка документов
print("📄 Загрузка документов...")
documents = SimpleDirectoryReader("data").load_data()
if not documents:
    print("❌ Нет документов в data/")
    sys.exit(1)
print(f"✅ Загружено {len(documents)} документов")

# 🔹 Чанкинг
parser = TokenTextSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP, separator=" ")
nodes = parser.get_nodes_from_documents(documents)
print(f"📦 Создано {len(nodes)} чанков")

# 🔹 Функция получения эмбеддинга через прямой HTTP-запрос
def get_embedding(text: str, model: str, base_url: str) -> list[float]:
    """Прямой вызов Ollama Embed API — надёжнее, чем через llama-index wrapper"""
    # Обрезаем текст для безопасности (1500 символов ≈ 300-400 токенов)
    if len(text) > 1500:
        text = text[:1500]
    
    response = requests.post(
        f"{base_url}/api/embed",
        json={"model": model, "input": text},
        timeout=30
    )
    if response.status_code != 200:
        raise Exception(f"Ollama API error: {response.status_code} — {response.text}")
    
    result = response.json()
    embeddings = result.get("embeddings", [])
    if not embeddings:
        raise Exception("Пустой ответ от Ollama")
    return embeddings[0]

# 🔹 Подготовка Qdrant
client = QdrantClient(url=QDRANT_URL)
if client.collection_exists(COLLECTION_NAME):
    client.delete_collection(COLLECTION_NAME)
    print("🗑️ Старая коллекция удалена")

client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=models.VectorParams(size=EMBEDDING_DIM, distance=models.Distance.COSINE)
)
print(f"🗄️ Коллекция создана (dim={EMBEDDING_DIM})")

# 🔹 Индексация: чанк за чанком
print("🧠 Векторизация и загрузка в Qdrant...")
success = 0

for i, node in enumerate(nodes):
    try:
        text = node.get_content().strip()
        if not text:
            continue
            
        # Получаем эмбеддинг
        embedding = get_embedding(text, EMBEDDING_MODEL, OLLAMA_URL)
        
        # Генерируем уникальный ID из текста
        point_id = int(hashlib.md5(text.encode()).hexdigest()[:8], 16)
        
        # Подготовка метаданных
        metadata = {
            "text": text,
            "source": node.metadata.get("file_name", "unknown"),
            "chunk_idx": i
        }
        
        # Вставка в Qdrant
        client.upsert(
            collection_name=COLLECTION_NAME,
            points=[
                qmodels.PointStruct(
                    id=point_id,
                    vector=embedding,
                    payload=metadata
                )
            ]
        )
        
        success += 1
        if (i + 1) % 10 == 0:
            print(f"  ⏳ Обработано {i+1}/{len(nodes)}...")
            
    except Exception as e:
        print(f"⚠️ Пропущен чанк #{i+1}: {e}")
        continue

# 🔹 Итог
if success == 0:
    print("❌ Не удалось проиндексировать ни один чанк!")
    sys.exit(1)

print(f"\n✅ Готово! Проиндексировано {success}/{len(nodes)} чанков")
print(f"🔍 Коллекция: {COLLECTION_NAME} в {QDRANT_URL}")