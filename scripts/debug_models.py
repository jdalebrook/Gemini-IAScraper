import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

print("🔍 Buscando modelos disponibles para tu cuenta...")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"✅ MODELO ENCONTRADO: {m.name}")
except Exception as e:
    print(f"❌ Error al listar modelos: {e}")
