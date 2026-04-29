#!/usr/bin/env python3
import os, sys, logging
from pathlib import Path
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.core.node_parser import SentenceSplitter
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

#данные лежат в rag/knowledge-base/data/
SCRIPT_DIR = Path(__file__).parent.absolute()
DATA_DIR = SCRIPT_DIR / "data"

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "my_kb_local"
EMBEDDING_MODEL = "mxbai-embed-large"
LLM_MODEL = "llama3.2:3b"
CHUNK_SIZE = 256
CHUNK_OVERLAP = 32
EMBED_BATCH_SIZE = 20

def main():
    print(f"📂 Загрузка документов из: {DATA_DIR}")
    if not DATA_DIR.exists():
        print(f"❌ Папка не найдена! Запустите сначала: python site/sync.py")
        print(f"   Ожидаемый путь: {DATA_DIR}")
        sys.exit(1)

    try:
        documents = SimpleDirectoryReader(DATA_DIR).load_data()
        print(f"✅ Загружено {len(documents)} документов.")
    except Exception as e:
        print(f"❌ Ошибка чтения: {e}")
        sys.exit(1)

    if not documents:
        print("⚠️ Документы не найдены."); return

    client = QdrantClient(QDRANT_URL)
    
    # Пересоздаём коллекцию
    if client.collection_exists(COLLECTION_NAME):
        print(f"🗑️ Очищаю старую коллекцию...")
        client.delete_collection(COLLECTION_NAME)
    
    client.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=1024, distance=Distance.COSINE)
    )
    print(f"✅ Коллекция '{COLLECTION_NAME}' создана")

    # Настройки моделей
    Settings.embed_model = OllamaEmbedding(model_name=EMBEDDING_MODEL, embed_batch_size=EMBED_BATCH_SIZE, request_timeout=120.0)
    Settings.llm = Ollama(model=LLM_MODEL, request_timeout=120.0)

    # Индексация
    vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)
    storage_context = StorageContext.from_defaults(vector_store=vector_store)
    
    print(f"⚡ Индексация... (Чанк: {CHUNK_SIZE})")
    index = VectorStoreIndex.from_documents(
        documents, 
        storage_context=storage_context,
        transformations=[SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)],
        show_progress=True
    )
    print("🎉 Индексация завершена!")

if __name__ == "__main__":
    main()