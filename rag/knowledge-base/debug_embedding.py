import os
from dotenv import load_dotenv
from llama_index.embeddings.google_genai import GoogleGenAIEmbedding

load_dotenv()

print("🔍 Проверка размеров эмбеддингов:")
for model_name in ["gemini-embedding-001", "gemini-embedding-2-preview"]:
    try:
        emb = GoogleGenAIEmbedding(model_name=model_name, api_key=os.getenv("GEMINI_API_KEY"))
        vec = emb.get_text_embedding("test")
        print(f"  • {model_name}: {len(vec)} dim")
    except Exception as e:
        print(f"  • {model_name}: ❌ {e}")
