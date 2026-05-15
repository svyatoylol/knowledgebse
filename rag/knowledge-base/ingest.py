#!/usr/bin/env python3
"""
Индексация документов в Qdrant.
Исправлено: ручное чтение файлов гарантирует точное соответствие 1 файл = 1 документ.
"""
import os, sys, logging, hashlib, uuid
from pathlib import Path

# LlamaIndex
from llama_index.core import StorageContext, Settings
from llama_index.core.schema import Document
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

# Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

# 🔇 Логирование
logging.basicConfig(level=logging.INFO, format='%(message)s', stream=sys.stdout)
logger = logging.getLogger(__name__)
logging.getLogger("llama_index").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("qdrant_client").setLevel(logging.WARNING)

# === КОНФИГУРАЦИЯ ===
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_ROOT = SCRIPT_DIR.parent.parent
DATA_DIR = PROJECT_ROOT / "data"

QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "my_kb_local"
EMBEDDING_MODEL = "nomic-embed-text"
LLM_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
def file_hash(path: Path) -> str:
    with open(path, 'rb') as f:
        return hashlib.md5(f.read()).hexdigest()

def filename_to_uuid(filename: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, filename))

def get_existing_hashes(client: QdrantClient, collection_name: str) -> dict:
    hashes = {}
    try:
        records, _ = client.scroll(
            collection_name=collection_name,
            with_payload=["filename", "file_hash"],
            limit=10000
        )
        for record in records:
            if record.payload and "filename" in record.payload:
                hashes[record.payload["filename"]] = record.payload.get("file_hash")
    except Exception as e:
        logger.warning(f"⚠️ Не удалось прочитать хэши: {e}")
    return hashes

def main():
    logger.info(f"📂 Загрузка документов из: {DATA_DIR}")
    
    # 1. Ручное чтение файлов (гарантирует 1:1, без скрытого сплита LlamaIndex)
    md_files = sorted(DATA_DIR.glob("*.md"))
    if not md_files:
        logger.error("❌ В папке data/ нет .md файлов! Запустите: python site/sync.py")
        sys.exit(1)
        
    logger.info(f"🔍 Найдено .md файлов: {len(md_files)}")
    
    documents = []
    for f in md_files:
        try:
            text = f.read_text(encoding="utf-8")
            doc = Document(text=text, metadata={"file_path": str(f), "filename": f.name})
            documents.append(doc)
        except Exception as e:
            logger.warning(f"⚠️ Пропуск {f.name}: {e}")
            
    if not documents:
        logger.warning("⚠️ Не удалось загрузить ни одного документа.")
        return
    logger.info(f"✅ Загружено {len(documents)} документов.")

    # 2. Подключение к Qdrant
    client = QdrantClient(QDRANT_URL)
    if not client.collection_exists(COLLECTION_NAME):
        logger.info(f"🏗️ Создаю коллекцию '{COLLECTION_NAME}'...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=768, distance=Distance.COSINE)
        )
    
    # 3. Настройка моделей
    Settings.embed_model = OllamaEmbedding(
        model_name=EMBEDDING_MODEL, base_url="http://localhost:11434",
        embed_batch_size=4, request_timeout=120.0
    )
    Settings.llm = Ollama(
        model=LLM_MODEL, base_url="http://localhost:11434",
        request_timeout=120.0, num_ctx=4096, num_gpu=1, temperature=0.2
    )

    # 4. Инкрементальная индексация
    logger.info("⚡ Проверка изменений...")
    existing_hashes = get_existing_hashes(client, COLLECTION_NAME)
    points_to_upsert = []
    updated_files = []
    
    for doc in documents:
        filename = doc.metadata["filename"]
        filepath = Path(doc.metadata["file_path"])
        current_hash = file_hash(filepath)
        
        # Пропускаем, если хэш совпадает
        if filename in existing_hashes and existing_hashes[filename] == current_hash:
            continue
        
        embedding = Settings.embed_model.get_text_embedding(doc.text)
        points_to_upsert.append(PointStruct(
            id=filename_to_uuid(filename),
            vector=embedding,
            payload={"text": doc.text, "filename": filename, "file_hash": current_hash}
        ))
        updated_files.append(filename)
    
    if points_to_upsert:
        client.upsert(collection_name=COLLECTION_NAME, points=points_to_upsert)
        logger.info(f"✅ Обновлено/добавлено: {len(updated_files)} файлов")
    else:
        logger.info("✨ Все документы актуальны")
    
    # 5. Удаление удалённых из data/
    current_filenames = {doc.metadata["filename"] for doc in documents}
    deleted = [fn for fn in existing_hashes if fn not in current_filenames]
    if deleted:
        ids = [filename_to_uuid(fn) for fn in deleted]
        client.delete(collection_name=COLLECTION_NAME, points_selector=ids)
        logger.info(f"🗑️ Удалено из базы: {', '.join(deleted)}")

    logger.info("🎉 Индексация завершена!")

if __name__ == "__main__":
    main()