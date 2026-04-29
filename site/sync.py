#!/usr/bin/env python3
import subprocess
import shutil
import sys
import json
import re
import os
from pathlib import Path
import tempfile
import hashlib

REPO_URL = "https://github.com/svyatoylol/knowledgebse.git"
BRANCH = "main"
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Пути
DATA_DIR = PROJECT_ROOT / "rag" / "knowledge-base" / "data"
ARTICLES_DIR = PROJECT_ROOT / "site" / "docs" / "articles"
ARTICLES_JSON = PROJECT_ROOT / "site" / "public" / "articles.json"

def run_cmd(cmd, cwd=None):
    print(f"🔄 {' '.join(cmd)}")
    subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)

def file_hash(path: Path) -> str:
    """Вычисляет MD5-хэш файла для сравнения изменений"""
    try:
        with open(path, 'rb') as f:
            return hashlib.md5(f.read()).hexdigest()
    except:
        return ""

def extract_metadata(file_path: Path):
    try:
        text = file_path.read_text(encoding="utf-8")[:600]
        text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)
        title_match = re.search(r'^#+\s+(.*)', text, re.MULTILINE)
        title = title_match.group(1).strip() if title_match else file_path.stem.replace('-', ' ').title()
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and not p.startswith('#')]
        desc = paragraphs[0][:120] + '...' if paragraphs else ""
        return title, desc
    except:
        return file_path.stem, ""

def sync_directory(source: Path, dest: Path) -> set:
    """
    Синхронизирует папку: копирует новые/изменённые файлы, удаляет отсутствующие в источнике.
    Возвращает множество имён файлов, которые есть в источнике.
    """
    source_files = {f.name for f in source.glob("*.md")}
    
    # 1. Копируем новые и изменённые файлы
    for src_file in source.glob("*.md"):
        dst_file = dest / src_file.name
        needs_copy = True
        
        if dst_file.exists():
            # Сравниваем по хэшу — копируем только если файл изменился
            if file_hash(src_file) == file_hash(dst_file):
                needs_copy = False
        
        if needs_copy:
            shutil.copy2(src_file, dst_file)
            action = "✅ Обновлено" if dst_file.exists() else "🆕 Добавлено"
            print(f"   {action}: {src_file.name}")
    
    # 2. Удаляем файлы, которых нет в источнике
    for dst_file in list(dest.glob("*.md")):
        if dst_file.name not in source_files:
            dst_file.unlink()
            print(f"   🗑️  Удалено: {dst_file.name}")
    
    return source_files

def update_kb():
    print(f"📂 Корень: {PROJECT_ROOT}")
    print(f"💾 Статьи хранятся в: {DATA_DIR}")
    
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    ARTICLES_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Скачивание из GitHub
    with tempfile.TemporaryDirectory() as tmp_dir:
        tmp_repo = Path(tmp_dir) / "kb-repo"
        run_cmd(["git", "clone", "--depth=1", "--filter=blob:none", "--no-checkout", REPO_URL, str(tmp_repo)])
        run_cmd(["git", "sparse-checkout", "init", "--cone"], cwd=tmp_repo)
        run_cmd(["git", "sparse-checkout", "set", "rag/knowledge-base/data"], cwd=tmp_repo)
        run_cmd(["git", "checkout", BRANCH], cwd=tmp_repo)
        
        source = tmp_repo / "rag" / "knowledge-base" / "data"
        if not source.exists():
            print("❌ Папка данных не найдена!"); sys.exit(1)

        # Синхронизация: rag/data (для RAG-индексации)
        print("🔄 Синхронизация rag/knowledge-base/data/")
        sync_directory(source, DATA_DIR)
        print(f"✅ В rag/data: {len(list(DATA_DIR.glob('*.md')))} статей")

    # 2. Синхронизация: site/docs/articles (для VitePress роутинга)
    print("🔄 Синхронизация site/docs/articles/")
    synced_files = sync_directory(DATA_DIR, ARTICLES_DIR)
    print(f"✅ В site/docs/articles: {len(synced_files)} статей")

    # 3. Генерация articles.json (только актуальные статьи)
    articles = []
    for md_file in DATA_DIR.glob("*.md"):
        if md_file.name in synced_files:  # Только файлы, которые есть в синхронизации
            title, desc = extract_metadata(md_file)
            articles.append({
                "title": title,
                "path": f"/articles/{md_file.stem}",
                "description": desc
            })
    
    ARTICLES_JSON.parent.mkdir(parents=True, exist_ok=True)
    with open(ARTICLES_JSON, "w", encoding="utf-8") as f:
        json.dump(articles, f, ensure_ascii=False, indent=2)
    print(f"📄 Сгенерирован: {ARTICLES_JSON} ({len(articles)} статей)")

    # Итог
    print("\n🎯 Синхронизация завершена:")
    print(f"   • Добавлено/обновлено: {len(synced_files)} статей")
    print(f"   • Удалено устаревших: {len(list(ARTICLES_DIR.glob('*.md'))) - len(synced_files)}")

if __name__ == "__main__":
    update_kb()