import sqlite3

DB_PATH = "noticias_ia.db"

def marcar_noticia(id_noticia, nuevo_estado):
    """Estados: 'favorito', 'oculto', 'importante', 'archivado'"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE noticias SET estado = ? WHERE id = ?', (nuevo_estado, id_noticia))
        conn.commit()
    print(f"✅ Noticia {id_noticia} marcada como {nuevo_estado}.")

def listar_top_noticias(min_score=8):
    """Muestra las noticias más fiables según Gemini"""
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT id, titular_es, score_fiabilidad
            FROM noticias
            WHERE score_fiabilidad >= ? AND estado != 'oculto'
            ORDER BY score_fiabilidad DESC, created_at DESC
            LIMIT 20
        ''', (min_score,))

        print(f"\n--- TOP NOTICIAS (Fiabilidad >= {min_score}) ---")
        for fila in cursor.fetchall():
            print(f"[{fila[0]}] ⭐ {fila[2]}/10 - {fila[1]}")

if __name__ == "__main__":
    # Prueba listando lo que ya procesaste
    listar_top_noticias()