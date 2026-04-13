# fallback_query.py — работает даже когда Gemini недоступен
import os
from llama_index.core import Settings, VectorStoreIndex, StorageContext
from llama_index.llms.ollama import Ollama
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

# 🔹 Локальные модели (без лимитов!)
Settings.llm = Ollama(model="llama3.2:3b", request_timeout=120.0)
Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

# Подключение к существующему Qdrant
client = QdrantClient(url="http://localhost:6333")
vector_store = QdrantVectorStore(client=client, collection_name="my_kb")
storage_context = StorageContext.from_defaults(vector_store=vector_store)

# Загрузка индекса
index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
    storage_context=storage_context
)
query_engine = index.as_query_engine(similarity_top_k=3)

print("🤖 Локальная база знаний готова (Ollama + Qdrant). Введите 'exit' для выхода.")
while True:
    question = input("\n❓ Ваш вопрос: ").strip()
    if question.lower() in ("exit", "quit", "выход", "q"):
        break
    if not question:
        continue
    try:
        response = query_engine.query(question)
        print(f"\n💡 Ответ: {response.response}")
    except Exception as e:
        print(f"❌ Ошибка: {e}")
