#!/usr/bin/env python3
"""
Индексация документов в Qdrant.
📍 Расположение: scripts/ingest.py
✅ Исправлено: пути рассчитываются от корня проекта, логи в logs/
"""
import os, sys, logging, hashlib, uuid
from pathlib import Path

# LlamaIndex
from llama_index.core import Settings
from llama_index.core.schema import Document
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.llms.ollama import Ollama

# Qdrant
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct
from dotenv import load_dotenv

# 🔗 Пути: scripts/ -> корень проекта
SCRIPTS_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPTS_DIR.parent
DATA_DIR = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 🔐 Загружаем .env из корня
load_dotenv(PROJECT_ROOT / ".env")

# 📝 Логирование в файл + консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "ingest.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)
logging.getLogger("llama_index").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("qdrant_client").setLevel(logging.WARNING)

# === КОНФИГУРАЦИЯ ===
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = os.getenv("QDRANT_COLLECTION", "my_kb_local")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
LLM_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", "768"))  # nomic-embed-text = 768

# === ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ===
def file_hash(path: Path) -> str:
    """Вычисляет MD5-хэш файла для отслеживания изменений"""
    try:
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return ""

def filename_to_uuid(filename: str) -> str:
    """Генерирует детерминированный UUID из имени файла"""
    return str(uuid.uuid5(uuid.NAMESPACE_DNS, filename))

def get_existing_hashes(client: QdrantClient, collection_name: str) -> dict:
    """Получает маппинг {filename: file_hash} из Qdrant"""
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
    
    # Проверка наличия статей
    if not DATA_DIR.exists():
        logger.error(f"❌ Папка data/ не найдена: {DATA_DIR}")
        logger.error("💡 Запустите сначала: python scripts/sync.py")
        sys.exit(1)
    
    # 1. Ручное чтение файлов (гарантирует 1 файл = 1 документ)
    md_files = sorted(DATA_DIR.glob("*.md"))
    if not md_files:
        logger.error("❌ В папке data/ нет .md файлов!")
        logger.error("💡 Добавьте статьи или запустите: python scripts/sync.py")
        sys.exit(1)
        
    logger.info(f"🔍 Найдено .md файлов: {len(md_files)}")
    
    documents = []
    for f in md_files:
        try:
            text = f.read_text(encoding="utf-8")
            doc = Document(
                text=text, 
                metadata={
                    "file_path": str(f), 
                    "filename": f.name,
                    "source": f.name.replace(".md", "")
                }
            )
            documents.append(doc)
        except Exception as e:
            logger.warning(f"⚠️ Пропуск {f.name}: {e}")
            
    if not documents:
        logger.warning("⚠️ Не удалось загрузить ни одного документа.")
        return
    logger.info(f"✅ Загружено {len(documents)} документов.")

    # 2. Подключение к Qdrant
    logger.info(f"🔗 Подключение к Qdrant: {QDRANT_URL}")
    client = QdrantClient(url=QDRANT_URL)
    
    if not client.collection_exists(COLLECTION_NAME):
        logger.info(f"🏗️ Создаю коллекцию '{COLLECTION_NAME}' (dim={EMBEDDING_DIM})...")
        client.create_collection(
            collection_name=COLLECTION_NAME,
            vectors_config=VectorParams(size=EMBEDDING_DIM, distance=Distance.COSINE)
        )
        logger.info("✅ Коллекция создана")
    
    # 3. Настройка моделей
    logger.info(f"🤖 Модели: {EMBEDDING_MODEL} (embed) + {LLM_MODEL} (llm)")
    Settings.embed_model = OllamaEmbedding(
        model_name=EMBEDDING_MODEL, 
        base_url="http://localhost:11434",
        embed_batch_size=4, 
        request_timeout=120.0
    )
    Settings.llm = Ollama(
        model=LLM_MODEL, 
        base_url="http://localhost:11434",
        request_timeout=120.0, 
        num_ctx=4096, 
        temperature=0.2
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
        
        # Пропускаем, если файл не менялся
        if filename in existing_hashes and existing_hashes[filename] == current_hash:
            continue
        
        # Генерируем эмбединг и добавляем в очередь
        try:
            embedding = Settings.embed_model.get_text_embedding(doc.text)
            points_to_upsert.append(PointStruct(
                id=filename_to_uuid(filename),
                vector=embedding,
                payload={
                    "text": doc.text, 
                    "filename": filename, 
                    "file_hash": current_hash,
                    "source": doc.metadata.get("source", filename)
                }
            ))
            updated_files.append(filename)
            logger.info(f"   📥 {filename}")
        except Exception as e:
            logger.error(f"❌ Ошибка эмбединга для {filename}: {e}")
    
    # Upsert в Qdrant
    if points_to_upsert:
        logger.info(f"⬆️ Загрузка {len(points_to_upsert)} векторов...")
        client.upsert(collection_name=COLLECTION_NAME, points=points_to_upsert)
        logger.info(f"✅ Обновлено/добавлено: {len(updated_files)} файлов")
    else:
        logger.info("✨ Все документы актуальны — изменений нет")
    
    # 5. Удаление удалённых из data/ файлов
    current_filenames = {doc.metadata["filename"] for doc in documents}
    deleted = [fn for fn in existing_hashes if fn not in current_filenames]
    if deleted:
        ids = [filename_to_uuid(fn) for fn in deleted]
        client.delete(collection_name=COLLECTION_NAME, points_selector=ids)
        logger.info(f"🗑️ Удалено из базы: {', '.join(deleted)}")

    logger.info("🎉 Индексация завершена!")
    return 0

if __name__ == "__main__":
    sys.exit(main() or 0)