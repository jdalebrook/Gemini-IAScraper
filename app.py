from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "noticias_ia.db"

def get_db_connection():
    """Establece conexión con la base de datos SQLite."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Permite acceder a las columnas por nombre
    return conn

@app.route('/')
def index():
    # Obtenemos la categoría desde la URL (ej: /?cat=COSMOS)
    categoria_filtro = request.args.get('cat')
    conn = get_db_connection()

    # 1. Sacamos todas las categorías únicas que existen para generar las pestañas automáticamente
    categorias = conn.execute('SELECT DISTINCT categoria FROM noticias WHERE categoria IS NOT NULL').fetchall()

    # 2. Construcción de la consulta principal
    # Solo mostramos noticias ya procesadas (titular_es no nulo) y que no estén ocultas
    query = 'SELECT * FROM noticias WHERE titular_es IS NOT NULL AND estado != "oculto"'
    params = []

    if categoria_filtro:
        query += ' AND categoria = ?'
        params.append(categoria_filtro)

    # Ordenamos por las más recientes y limitamos a 50 para no saturar el navegador
    query += ' ORDER BY created_at DESC LIMIT 100'

    noticias = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        'index.html',
        noticias=noticias,
        categorias=categorias,
        cat_activa=categoria_filtro
    )

@app.route('/accion/<int:id>/<estado>')
def cambiar_estado(id, estado):
    """
    Cambia el estado de una noticia (favorito, oculto, nuevo).
    Se llama desde los botones de la interfaz.
    """
    conn = get_db_connection()
    conn.execute('UPDATE noticias SET estado = ? WHERE id = ?', (estado, id))
    conn.commit()
    conn.close()

    # Redirige a la página anterior para no perder el filtro de categoría
    return redirect(request.referrer or url_for('index'))

if __name__ == '__main__':
    # Lanzamos el servidor en modo debug para ver errores en tiempo real
    print("🌐 Panel Web Multi-Temático iniciado en http://127.0.0.1:5000")
    app.run(debug=True)