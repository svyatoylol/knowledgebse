#!/usr/bin/env python3
"""
query.py — Загрузка из GitHub + запуск ingest.py + ответ + output_pending.json
Исправлена проблема с путями на Windows
"""

import os
import sys
import json
import requests
import subprocess
import shutil
import uuid
from pathlib import Path

# ====================== КОНФИГУРАЦИЯ ======================
GITHUB_REPO = "https://github.com/svyatoylol/knowledgebse.git"
GITHUB_BRANCH = "andy"
GITHUB_FOLDER = "rag/knowledge-base"          # папка в репозитории
TEMP_DIR = "./github_kb_temp"
LOCAL_DATA_DIR = "data"                       # локальная папка для ingest.py

OLLAMA_URL = "http://localhost:11434"
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "my_kb_local"
LLM_MODEL = "llama3.2:3b"
EMBEDDING_MODEL = "mxbai-embed-large"
TOP_K = 5

# Получаем абсолютный путь к папке, где лежит query.py
SCRIPT_DIR = Path(__file__).parent.absolute()

print(f"🔗 Локальный чат: {LLM_MODEL} + {EMBEDDING_MODEL}")
print(f"📥 GitHub: {GITHUB_REPO} / {GITHUB_FOLDER} (branch {GITHUB_BRANCH})")
print(f"📍 Рабочая папка: {SCRIPT_DIR}")

# ====================== СКАЧИВАНИЕ ИЗ GITHUB ======================
def download_github_folder(repo_url: str, branch: str, folder_path: str, target_dir: str):
    if repo_url.endswith(".git"):
        repo_url = repo_url[:-4]
    owner_repo = repo_url.split("github.com/")[-1].strip("/")
    owner, repo = owner_repo.split("/")

    folder_path = folder_path.strip("/") if folder_path else ""
    base_api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
    base_raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{branch}/"

    os.makedirs(target_dir, exist_ok=True)
    count = 0

    def download_recursive(current_path: str, current_local: Path):
        nonlocal count
        url = f"{base_api_url}/{current_path}" if current_path else base_api_url
        try:
            resp = requests.get(url, timeout=20)
            resp.raise_for_status()
            items = resp.json()
            if not isinstance(items, list):
                items = [items]

            for item in items:
                name = item["name"]
                item_path = item["path"]
                local_path = current_local / name

                if item["type"] == "dir":
                    local_path.mkdir(parents=True, exist_ok=True)
                    download_recursive(item_path, local_path)
                elif item["type"] == "file":
                    file_url = base_raw_url + item_path
                    try:
                        file_resp = requests.get(file_url, timeout=30)
                        file_resp.raise_for_status()
                        local_path.write_bytes(file_resp.content)
                        count += 1
                    except Exception:
                        pass
        except Exception:
            pass

    print("🌐 Скачиваем данные из GitHub...")
    download_recursive(folder_path, Path(target_dir))
    print(f"✅ Скачано {count} файлов в {target_dir}")


# ====================== ОСНОВНАЯ ЛОГИКА ======================
if __name__ == "__main__":
    # 1. Очищаем старые данные
    if os.path.exists(TEMP_DIR):
        shutil.rmtree(TEMP_DIR, ignore_errors=True)
    if os.path.exists(LOCAL_DATA_DIR):
        shutil.rmtree(LOCAL_DATA_DIR, ignore_errors=True)
    os.makedirs(LOCAL_DATA_DIR, exist_ok=True)

    # 2. Скачиваем из GitHub
    download_github_folder(GITHUB_REPO, GITHUB_BRANCH, GITHUB_FOLDER, TEMP_DIR)

    # 3. Копируем содержимое data/ из скачанного в локальную data/
    downloaded_data = Path(TEMP_DIR) / "data"
    if downloaded_data.exists() and list(downloaded_data.iterdir()):
        print(f"📂 Копируем документы из {downloaded_data} → ./{LOCAL_DATA_DIR}/")
        for item in downloaded_data.iterdir():
            dest = Path(LOCAL_DATA_DIR) / item.name
            if item.is_file():
                shutil.copy2(item, dest)
            elif item.is_dir():
                shutil.copytree(item, dest, dirs_exist_ok=True)
    else:
        print("⚠️  В GitHub не найдена папка data/ с документами.")

    # 4. Запускаем ingest.py с правильным путём
    ingest_path = SCRIPT_DIR / "ingest.py"
    print("\n🚀 Запускаем ingest.py для индексации...")

    if not ingest_path.exists():
        print(f"❌ Файл ingest.py не найден по пути:\n   {ingest_path}")
        print("   Убедитесь, что ingest.py лежит в одной папке с query.py")
        sys.exit(1)

    try:
        result = subprocess.run(
            [sys.executable, str(ingest_path)],   # используем абсолютный путь
            cwd=SCRIPT_DIR,                       # запускаем с правильной рабочей директорией
            check=True,
            capture_output=False,
            text=True
        )
        print("✅ ingest.py завершился успешно")
    except subprocess.CalledProcessError as e:
        print(f"❌ Ошибка при выполнении ingest.py (код {e.returncode})")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        sys.exit(1)

    print("\n🤖 База знаний готова. Введите 'exit' для выхода.")
    print("-" * 70)

    # ====================== ИНТЕРАКТИВНЫЙ ЧАТ ======================
    while True:
        try:
            question = input("\n❓ Ваш вопрос: ").strip()
            if question.lower() in ("exit", "quit", "выход", "q", ""):
                break
            if not question:
                continue

            print("🤔 Генерация ответа...")

            # Простой промпт (можно позже заменить на полноценный RAG)
            prompt = f"""Ты — помощник по базе знаний. Используй только информацию из загруженных документов.
Ответь точно и по делу на вопрос пользователя.

Вопрос: {question}

Ответ:"""

            resp = requests.post(
                f"{OLLAMA_URL}/api/generate",
                json={"model": LLM_MODEL, "prompt": prompt, "stream": False},
                timeout=120
            )
            resp.raise_for_status()
            answer = resp.json().get("response", "Нет ответа от модели.").strip()

            print(f"\n💡 Ответ:\n{answer}\n")

            # Сохраняем в output_pending.json
            output_data = {
                "UsedID": str(uuid.uuid4()),
                "OutPut": answer
            }
            with open(SCRIPT_DIR / "output_pending.json", "w", encoding="utf-8") as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)

            print("📄 Ответ сохранён в output_pending.json")

        except KeyboardInterrupt:
            print("\n👋 Выход")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")