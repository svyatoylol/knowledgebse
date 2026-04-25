import subprocess
import os
import sys

REPO_URL = "https://github.com/svyatoylol/knowledgebse.git"
BRANCH = "main" 

TARGET_DIR = os.path.join("docs", "knowledgebse") 

def run_cmd(cmd, cwd=None):
    try:
        subprocess.run(cmd, cwd=cwd, check=True, text=True, capture_output=True)
    except subprocess.CalledProcessError as e:
        print(f" Ошибка при выполнении: {' '.join(cmd)}")
        print(f"Подробности: {e.stderr.strip()}")
        sys.exit(1)

def update_kb():
    print(f" Синхронизация с базой знаний...")
    
    os.makedirs(os.path.dirname(TARGET_DIR), exist_ok=True)

    if not os.path.exists(os.path.join(TARGET_DIR, ".git")):
        print(" Первичная загрузка репозитория...")
        
        run_cmd(["git", "clone", "--filter=blob:none", "--no-checkout", REPO_URL, TARGET_DIR])
        
        run_cmd(["git", "sparse-checkout", "init"], cwd=TARGET_DIR)
        run_cmd(["git", "config", "core.sparseCheckoutCone", "false"], cwd=TARGET_DIR)
        
        sparse_rules_path = os.path.join(TARGET_DIR, ".git", "info", "sparse-checkout")
        with open(sparse_rules_path, "w", encoding="utf-8") as f:
            f.write("*.md\n")
            f.write("*.png\n*.jpg\n*.jpeg\n*.gif\n*.svg\n")

        run_cmd(["git", "checkout", BRANCH], cwd=TARGET_DIR)
        print(" Первичная загрузка завершена!")
        
    else:
        print("Подтягивание свежих изменений...")
        run_cmd(["git", "pull", "origin", BRANCH], cwd=TARGET_DIR)
        print(" Обновление успешно завершено!")

if __name__ == "__main__":
    update_kb()
