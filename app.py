from flask import Flask, render_template, request, redirect, url_for
import sqlite3
import os

app = Flask(__name__)
DB_PATH = "noticias_ia.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Para acceder a columnas por nombre
    return conn

@app.route('/')
def index():
    conn = get_db_connection()
    # Solo mostramos noticias procesadas y que no estén ocultas
    noticias = conn.execute('''
        SELECT * FROM noticias
        WHERE titular_es IS NOT NULL AND estado != 'oculto'
        ORDER BY score_fiabilidad DESC, created_at DESC
    ''').fetchall()
    conn.close()
    return render_template('index.html', noticias=noticias)

@app.route('/accion/<int:id>/<estado>')
def cambiar_estado(id, estado):
    conn = get_db_connection()
    conn.execute('UPDATE noticias SET estado = ? WHERE id = ?', (estado, id))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)