#!/usr/bin/env python3
"""
Синхронизатор статей Knowledge Base.
📍 Расположение: scripts/sync.py
✅ Плоская структура: data/ в корне, логи в logs/, без rag/
"""
import subprocess, shutil, sys, json, re, os, hashlib, logging
from pathlib import Path
import tempfile
from dotenv import load_dotenv

# 🔗 Пути: scripts/ -> корень проекта
SCRIPTS_DIR = Path(__file__).parent.resolve()
PROJECT_ROOT = SCRIPTS_DIR.parent  # 📍 scripts/ -> корень
DATA_ROOT = PROJECT_ROOT / "data"
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)

# 🔐 Загружаем .env из корня
load_dotenv(PROJECT_ROOT / ".env")

# 📝 Логирование в файл + консоль
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_DIR / "sync.log", encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Пути назначения (обновлено для плоской структуры)
ARTICLES_DIR = PROJECT_ROOT / "site" / "docs" / "articles"
ARTICLES_JSON = PROJECT_ROOT / "site" / "public" / "articles.json"

# GitHub настройки (из .env или дефолтные)
REPO_URL = os.getenv("GITHUB_REPO_URL", "https://github.com/svyatoylol/knowledgebse.git")
BRANCH = os.getenv("GITHUB_BRANCH", "main")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")  # Опционально для приватных репо

def file_hash(path: Path) -> str:
    """Вычисляет MD5-хэш файла для сравнения изменений"""
    try:
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return ""

def extract_metadata(file_path: Path):
    """Извлекает заголовок и описание из Markdown-файла"""
    try:
        text = file_path.read_text(encoding="utf-8")[:600]
        # Удаляем frontmatter если есть
        text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
        # Ищем заголовок первого уровня
        title_match = re.search(r'^#+\s+(.*)', text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else file_path.stem.replace('-', ' ').title()
        # Берём первый абзац как описание
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and not p.startswith('#')]
        desc = paragraphs[0][:120] + '...' if paragraphs else ""
        return title, desc
    except Exception as e:
        logger.warning(f"⚠️ Ошибка парсинга метаданных {file_path.name}: {e}")
        return file_path.stem, ""

def sync_directory(source: Path, dest: Path) -> set:
    """Синхронизирует папку: копирует новые/изменённые, удаляет отсутствующие в источнике."""
    dest.mkdir(parents=True, exist_ok=True)
    source_files = {f.name for f in source.glob("*.md")}
    synced = set()
    
    # 1. Копируем новые и изменённые
    for src_file in source.glob("*.md"):
        dst_file = dest / src_file.name
        if not dst_file.exists() or file_hash(src_file) != file_hash(dst_file):
            shutil.copy2(src_file, dst_file)
            logger.info(f"   {'✅ Обновлено' if dst_file.exists() else '🆕 Добавлено'}: {src_file.name}")
            synced.add(src_file.name)
    
    # 2. Удаляем файлы, которых нет в источнике
    for dst_file in list(dest.glob("*.md")):
        if dst_file.name not in source_files:
            dst_file.unlink()
            logger.info(f"   🗑️  Удалено из {dest.name}: {dst_file.name}")
    
    return synced

def update_kb():
    logger.info(f"🔍 PROJECT_ROOT: {PROJECT_ROOT}")
    logger.info(f"🔍 DATA_ROOT: {DATA_ROOT}")
    
    # Проверка: правильно ли определился корень
    if not str(PROJECT_ROOT).endswith("knowledgebse"):
        logger.error(f"❌ ОШИБКА: Неправильный корень проекта!\nОжидалось: .../knowledgebse\nПолучено: {PROJECT_ROOT}")
        logger.error("💡 Убедитесь, что sync.py лежит в scripts/, а не в корне")
        sys.exit(1)
    
    # Создаём папку data/ если нет
    DATA_ROOT.mkdir(parents=True, exist_ok=True)
    logger.info(f"📂 Синхронизация статей в: {DATA_ROOT}")
    
    # 1️⃣ Скачиваем из GitHub -> в локальную data/
    logger.info("\n📥 Синхронизация с GitHub (папка data/)...")
    
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_repo = Path(tmp_dir) / "kb-repo"
        
        # Формируем команду git clone с токеном если есть
        clone_cmd = ["git", "clone", "--depth=1", "--filter=blob:none", "--no-checkout"]
        if GITHUB_TOKEN:
            repo_url = REPO_URL.replace("https://", f"https://{GITHUB_TOKEN}@")
            clone_cmd.extend([repo_url, str(tmp_repo)])
        else:
            clone_cmd.extend([REPO_URL, str(tmp_repo)])
        
        try:
            subprocess.run(clone_cmd, check=True, capture_output=True, timeout=60)
            subprocess.run(["git", "sparse-checkout", "init", "--cone"], cwd=tmp_repo, check=True)
            subprocess.run(["git", "sparse-checkout", "set", "data"], cwd=tmp_repo, check=True)
            subprocess.run(["git", "checkout", BRANCH], cwd=tmp_repo, check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Ошибка git: {e.stderr.decode() if e.stderr else e}")
            return
        except Exception as e:
            logger.error(f"❌ Ошибка клонирования: {e}")
            return
        
        github_source = tmp_repo / "data"
        if github_source.exists():
            github_files = {f.name for f in github_source.glob("*.md")}
            logger.info(f"🔍 Найдено статей на GitHub: {len(github_files)}")
            
            # Копируем/обновляем файлы
            for f in github_source.glob("*.md"):
                dst = DATA_ROOT / f.name
                if not dst.exists() or file_hash(f) != file_hash(dst):
                    shutil.copy2(f, dst)
                    logger.info(f"   📥 {f.name}")
                    
            # Удаляем локальные файлы, которых нет на GitHub
            for local_md in list(DATA_ROOT.glob("*.md")):
                if local_md.name not in github_files:
                    local_md.unlink()
                    logger.info(f"   🗑️  Удалено локально (нет на GitHub): {local_md.name}")
        else:
            logger.warning(f"⚠️ Папка data/ не найдена в репозитории на ветке {BRANCH}")

    local_count = len(list(DATA_ROOT.glob("*.md")))
    logger.info(f"✅ В локальной data/: {local_count} статей")

    # 2️⃣ Синхронизация ИЗ data/ → в site/docs/articles/ (для VitePress)
    logger.info("\n🔄 data/ → site/docs/articles/")
    synced_to_site = sync_directory(DATA_ROOT, ARTICLES_DIR)

    # 3️⃣ Генерация articles.json (для авто-сайдбара VitePress)
    logger.info("\n📄 Генерация articles.json...")
    articles = []
    for md_file in sorted(DATA_ROOT.glob("*.md")):
        if md_file.name in synced_to_site or True:  # Генерируем для всех статей
            title, desc = extract_metadata(md_file)
            articles.append({
                "title": title,
                "path": f"/articles/{md_file.stem}",
                "description": desc,
                "filename": md_file.name,
                "updated": md_file.stat().st_mtime
            })
    
    ARTICLES_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(ARTICLES_JSON, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    logger.info(f"✅ Сгенерировано {len(articles)} записей в {ARTICLES_JSON}")
    
    # 🎯 Итог
    logger.info("\n" + "="*50)
    logger.info("🎯 СИНХРОНИЗАЦИЯ ЗАВЕРШЕНА")
    logger.info("="*50)
    logger.info(f"   • Локально data/: {local_count} файлов")
    logger.info(f"   • Синхронизировано в site/: {len(synced_to_site)}")
    logger.info(f"   • Записей в articles.json: {len(articles)}")
    logger.info("="*50)
    
    return 0

if __name__ == "__main__":
    sys.exit(update_kb() or 0)