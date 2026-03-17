import google.generativeai as genai
import sqlite3
import os
import json
import time
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")

# Configuración inicial
genai.configure(api_key=api_key)
DB_PATH = "noticias_ia.db"

def procesar_con_gemini():
    # Usamos el modelo que confirmamos que funciona en tu terminal
    model = genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        generation_config={"response_mime_type": "application/json"}
    )

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()

        # Subimos el límite a 100, ya que el código ahora sabe esperar
        cursor.execute('SELECT id, titulo_original, url FROM noticias WHERE titular_es IS NULL LIMIT 20')
        filas = cursor.fetchall()

        if not filas:
            print("☕ No hay noticias nuevas para procesar. ¡Todo al día!")
            return

        print(f"🤖 Iniciando procesamiento de {len(filas)} noticias con Gemini 2.5 Flash...")
        print("⚠️ Nota: Respetando el límite de 5 solicitudes por minuto (Plan Gratuito).")

        for id_noticia, titulo, url in filas:
            prompt = f"""
            Actúa como un editor experto en tecnología. Analiza esta noticia:
            Título original: {titulo}
            URL: {url}

            Responde con esta estructura JSON:
            {{
                "titular_es": "Titular corto y directo en español",
                "resumen_es": "Un resumen de máximo 2 líneas en español",
                "score": 1-10,
                "razon": "Breve explicación de por qué esa nota de fiabilidad"
            }}
            """

            try:
                response = model.generate_content(prompt)
                data = json.loads(response.text)

                cursor.execute('''
                    UPDATE noticias
                    SET titular_es = ?, resumen_es = ?, score_fiabilidad = ?, analisis_objetivo = ?
                    WHERE id = ?
                ''', (data['titular_es'], data['resumen_es'], data['score'], data['razon'], id_noticia))

                conn.commit()
                print(f"✅ [{id_noticia}] {data['titular_es']} (Fiabilidad: {data['score']}/10)")

                # PAUSA ESTRATÉGICA: 12.5 segundos para no exceder 5 RPM (60s / 5 = 12s)
                time.sleep(15)

            except Exception as e:
                error_str = str(e)
                if "429" in error_str:
                    print(f"🛑 Límite de cuota alcanzado. Esperando 60 segundos para resetear...")
                    time.sleep(60)
                    # Opcional: podrías re-intentar la misma noticia aquí,
                    # pero por simplicidad el script pasará a la siguiente en el próximo ciclo.
                elif "404" in error_str:
                    print(f"❌ Error de modelo: Revisa si 'gemini-2.5-flash' sigue activo.")
                    break
                else:
                    print(f"❌ Error inesperado en noticia {id_noticia}: {e}")
                    continue

    print("\n✨ Procesamiento finalizado.")

if __name__ == "__main__":
    procesar_con_gemini()