from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)

# --- CONFIGURACIÓN DE RUTAS INTELIGENTE ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Busca la DB en la raíz o en una carpeta /data si decides moverla luego
DB_PATH = os.path.join(BASE_DIR, "noticias_ia.db")
if not os.path.exists(DB_PATH):
    DB_PATH = os.path.join(BASE_DIR, "data", "noticias_ia.db")
# ------------------------------------------

def get_db_connection():
    """Establece conexión con la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    categoria_filtro = request.args.get('cat')
    # Nuevo filtro: ¿Queremos ver solo lo mejor? (Ej: /?top=1)
    solo_top = request.args.get('top') == '1'

    conn = get_db_connection()

    # 1. Generación dinámica de pestañas (esto evita que "IA" desaparezca)
    categorias_rows = conn.execute(
        'SELECT DISTINCT categoria FROM noticias WHERE categoria IS NOT NULL ORDER BY categoria'
    ).fetchall()

    # 2. Construcción de la consulta con Filtro de Calidad
    query = 'SELECT * FROM noticias WHERE titular_es IS NOT NULL AND estado != "oculto"'
    params = []

    if categoria_filtro:
        query += ' AND categoria = ?'
        params.append(categoria_filtro)

    # Si activamos el modo 'top', solo mostramos noticias con score >= 7
    if solo_top:
        query += ' AND score_fiabilidad >= 7'

    # Ordenamos por las más recientes (procesadas) y limitamos
    query += ' ORDER BY id DESC LIMIT 100'

    noticias = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        'index.html',
        noticias=noticias,
        categorias=categorias_rows,
        cat_activa=categoria_filtro,
        solo_top=solo_top
    )

@app.route('/accion/<int:id>/<estado>')
def cambiar_estado(id, estado):
    conn = get_db_connection()
    conn.execute('UPDATE noticias SET estado = ? WHERE id = ?', (estado, id))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    print(f"🌐 Panel Web iniciado usando DB en: {DB_PATH}")
    app.run(debug=True, port=5000)