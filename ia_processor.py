import google.generativeai as genai
import sqlite3
import os
import json
import time
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)
DB_PATH = "noticias_ia.db"

def procesar_con_gemini():
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row # IMPORTANTE: Para leer categorías por nombre
        cursor = conn.cursor()

        # Seleccionamos la categoría también para dársela a la IA
        cursor.execute('SELECT id, titulo_original, url, categoria FROM noticias WHERE titular_es IS NULL LIMIT 10')
        filas = cursor.fetchall()

        if not filas:
            return False

        print(f"🤖 [{datetime.now().strftime('%H:%M')}] Procesando lote de {len(filas)} noticias...")

        for fila in filas:
            id_noticia = fila['id']
            # Prompt dinámico según la categoría
            prompt = f"""
            Actúa como un experto en {fila['categoria']}.
            Analiza esta noticia y responde estrictamente en JSON:
            Título: {fila['titulo_original']}
            URL: {fila['url']}

            Estructura:
            {{
                "titular_es": "Titular profesional en español",
                "resumen_es": "Resumen de 2 frases",
                "score": 1-10,
                "razon": "Explicación breve de la fiabilidad"
            }}
            """

            try:
                response = model.generate_content(prompt)
                data = json.loads(response.text)

                cursor.execute('''
                    UPDATE noticias SET titular_es = ?, resumen_es = ?, score_fiabilidad = ?, analisis_objetivo = ?
                    WHERE id = ?
                ''', (data['titular_es'], data['resumen_es'], data['score'], data['razon'], id_noticia))
                conn.commit()

                print(f"✅ [{fila['categoria']}] {data['titular_es']}")
                time.sleep(20) # Seguridad 3 RPM

            except Exception as e:
                if "429" in str(e):
                    print("🛑 Cuota alcanzada. Enfriando 5 minutos...")
                    time.sleep(300)
                continue
    return True

if __name__ == "__main__":
    print("🚀 Procesador Multi-Temático iniciado...")
    while True:
        hubo_trabajo = procesar_con_gemini()
        if not hubo_trabajo:
            print("☕ Sin noticias nuevas. Reintentando en 10 minutos...")
            time.sleep(600)