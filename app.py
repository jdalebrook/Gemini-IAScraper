from flask import Flask, render_template, request, redirect, url_for, jsonify
import sqlite3
import json
import os
import re
import sys

# En modo frozen (PyInstaller) los datos van junto al .exe; en dev, al lado de app.py
BASE_DIR    = os.path.dirname(sys.executable) if getattr(sys, 'frozen', False) else os.path.dirname(os.path.abspath(__file__))
DB_PATH     = os.path.join(BASE_DIR, "data", "noticias_ia.db")
ESTADO_PATH = os.path.join(BASE_DIR, "data", "processor.state")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "processor_config.json")
FEEDS_DIR   = os.path.join(BASE_DIR, "config", "feeds")

CONFIG_DEFAULTS = {
    "engine": "gemini",
    "gemini_mode": "free",
    "gemini_model": "gemini-2.5-flash-lite",
    "ollama_host": "http://localhost:11434",
    "ollama_model": "qwen2.5:14b",
    "ollama_temperature": 0.1,
    "batch_size": 5,
    "pause_seconds": 15,
    "energy_mode": 50,
    "schedule_enabled": False,
    "schedule_start": 2,
    "schedule_end": 7,
    "min_pending": 0,
    "scrape_interval_hours": 8,
}

app = Flask(__name__, template_folder="app/templates", static_folder="app/static")

# ── DB ─────────────────────────────────────────────────────────────────────────

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# ── Estado procesador ──────────────────────────────────────────────────────────

def get_processor_estado():
    try:
        with open(ESTADO_PATH) as f:
            return f.read().strip()
    except FileNotFoundError:
        return "stopped"

def set_processor_estado(estado):
    with open(ESTADO_PATH, "w") as f:
        f.write(estado)

# ── Config ─────────────────────────────────────────────────────────────────────

def get_config():
    try:
        with open(CONFIG_PATH) as f:
            return {**CONFIG_DEFAULTS, **json.load(f)}
    except Exception:
        return CONFIG_DEFAULTS.copy()

def save_config(data):
    merged = {**CONFIG_DEFAULTS, **data}
    with open(CONFIG_PATH, "w") as f:
        json.dump(merged, f, indent=2)
    return merged

# ── Rutas principales ──────────────────────────────────────────────────────────

@app.route("/")
def index():
    categoria_filtro = request.args.get("cat")
    solo_top = request.args.get("top") == "1"

    conn = get_db_connection()

    categorias_rows = conn.execute(
        "SELECT DISTINCT categoria FROM noticias WHERE categoria IS NOT NULL ORDER BY categoria"
    ).fetchall()

    query  = 'SELECT * FROM noticias WHERE titular_es IS NOT NULL AND estado != "oculto"'
    params = []

    if categoria_filtro:
        query += " AND categoria = ?"
        params.append(categoria_filtro)

    if solo_top:
        query += " AND score_fiabilidad >= 7"

    query += " ORDER BY id DESC LIMIT 100"

    noticias = conn.execute(query, params).fetchall()
    conn.close()

    return render_template(
        "index.html",
        noticias=noticias,
        categorias=categorias_rows,
        cat_activa=categoria_filtro,
        solo_top=solo_top,
        processor_estado=get_processor_estado(),
        config=get_config(),
    )

ESTADOS_VALIDOS = {"nuevo", "favorito", "oculto", "importante", "archivado"}

@app.route("/accion/<int:id>/<estado>")
def cambiar_estado(id, estado):
    if estado not in ESTADOS_VALIDOS:
        return redirect(request.referrer or url_for("index"))
    conn = get_db_connection()
    conn.execute("UPDATE noticias SET estado = ? WHERE id = ?", (estado, id))
    conn.commit()
    conn.close()
    return redirect(request.referrer or url_for("index"))

# ── Control procesador ─────────────────────────────────────────────────────────

@app.route("/processor/pause")
def processor_pause():
    set_processor_estado("paused")
    return redirect(request.referrer or url_for("index"))

@app.route("/processor/resume")
def processor_resume():
    set_processor_estado("running")
    return redirect(request.referrer or url_for("index"))

# ── Config API ─────────────────────────────────────────────────────────────────

@app.route("/api/config", methods=["GET"])
def api_get_config():
    return jsonify(get_config())

@app.route("/api/config", methods=["POST"])
def api_set_config():
    data = request.get_json(force=True)
    # Sanitizar tipos
    if "ollama_temperature" in data:
        data["ollama_temperature"] = float(data["ollama_temperature"])
    if "batch_size" in data:
        data["batch_size"] = int(data["batch_size"])
    if "pause_seconds" in data:
        data["pause_seconds"] = int(data["pause_seconds"])
    if "energy_mode" in data:
        data["energy_mode"] = int(data["energy_mode"])
    if "schedule_start" in data:
        data["schedule_start"] = int(data["schedule_start"])
    if "schedule_end" in data:
        data["schedule_end"] = int(data["schedule_end"])
    if "min_pending" in data:
        data["min_pending"] = int(data["min_pending"])
    if "scrape_interval_hours" in data:
        data["scrape_interval_hours"] = max(1, int(data["scrape_interval_hours"]))
    if "schedule_enabled" in data:
        data["schedule_enabled"] = bool(data["schedule_enabled"])
    saved = save_config(data)
    return jsonify({"ok": True, "config": saved})

# ── Feeds API ──────────────────────────────────────────────────────────────────

def _parse_source(val):
    if isinstance(val, str):
        return {"url": val, "weight": 5}
    return {"url": val.get("url", ""), "weight": int(val.get("weight", 5))}

def get_all_feeds():
    result = {}
    try:
        for filename in sorted(os.listdir(FEEDS_DIR)):
            if filename.startswith("feeds_") and filename.endswith(".json"):
                cat = filename.replace("feeds_", "").replace(".json", "")
                with open(os.path.join(FEEDS_DIR, filename), "r", encoding="utf-8") as f:
                    raw = json.load(f)
                result[cat] = {name: _parse_source(val) for name, val in raw.items()}
    except Exception:
        pass
    return result

def save_category_feeds(category, sources):
    filepath = os.path.join(FEEDS_DIR, f"feeds_{category}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(sources, f, indent=2, ensure_ascii=False)

def _safe_cat_name(raw):
    return re.sub(r"[^a-z0-9_]", "_", raw.strip().lower())

@app.route("/api/feeds", methods=["GET"])
def api_get_feeds():
    return jsonify(get_all_feeds())

@app.route("/api/feeds/source", methods=["POST"])
def api_add_feed():
    data = request.get_json(force=True)
    category = _safe_cat_name(data.get("category", ""))
    name     = data.get("name", "").strip()
    url_val  = data.get("url", "").strip()
    weight   = max(1, min(10, int(data.get("weight", 5))))
    if not category or not name or not url_val:
        return jsonify({"ok": False, "error": "Faltan campos obligatorios"}), 400
    feeds = get_all_feeds()
    cat_feeds = feeds.get(category, {})
    cat_feeds[name] = {"url": url_val, "weight": weight}
    save_category_feeds(category, cat_feeds)
    return jsonify({"ok": True})

@app.route("/api/feeds/source", methods=["PUT"])
def api_update_feed():
    data     = request.get_json(force=True)
    old_cat  = _safe_cat_name(data.get("old_category", ""))
    old_name = data.get("old_name", "").strip()
    new_cat  = _safe_cat_name(data.get("category", old_cat))
    new_name = data.get("name", old_name).strip()
    new_url  = data.get("url", "").strip()
    new_weight = max(1, min(10, int(data.get("weight", 5))))
    feeds = get_all_feeds()
    if old_cat not in feeds or old_name not in feeds[old_cat]:
        return jsonify({"ok": False, "error": "Feed no encontrado"}), 404
    del feeds[old_cat][old_name]
    save_category_feeds(old_cat, feeds[old_cat])
    target = feeds.get(new_cat, {})
    target[new_name] = {"url": new_url, "weight": new_weight}
    save_category_feeds(new_cat, target)
    return jsonify({"ok": True})

@app.route("/api/feeds/source", methods=["DELETE"])
def api_delete_feed():
    data     = request.get_json(force=True)
    category = _safe_cat_name(data.get("category", ""))
    name     = data.get("name", "").strip()
    feeds = get_all_feeds()
    if category not in feeds or name not in feeds[category]:
        return jsonify({"ok": False, "error": "Feed no encontrado"}), 404
    del feeds[category][name]
    save_category_feeds(category, feeds[category])
    return jsonify({"ok": True})

@app.route("/api/feeds/category", methods=["POST"])
def api_add_category():
    data     = request.get_json(force=True)
    category = _safe_cat_name(data.get("category", ""))
    if not category:
        return jsonify({"ok": False, "error": "Nombre vacío"}), 400
    filepath = os.path.join(FEEDS_DIR, f"feeds_{category}.json")
    if os.path.exists(filepath):
        return jsonify({"ok": False, "error": "Ya existe esa categoría"}), 409
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump({}, f, indent=2)
    return jsonify({"ok": True, "category": category})

@app.route("/api/feeds/category", methods=["PUT"])
def api_rename_category():
    data     = request.get_json(force=True)
    old_name = _safe_cat_name(data.get("old_name", ""))
    new_name = _safe_cat_name(data.get("new_name", ""))
    if not new_name:
        return jsonify({"ok": False, "error": "Nombre vacío"}), 400
    old_path = os.path.join(FEEDS_DIR, f"feeds_{old_name}.json")
    new_path = os.path.join(FEEDS_DIR, f"feeds_{new_name}.json")
    if not os.path.exists(old_path):
        return jsonify({"ok": False, "error": "Categoría no encontrada"}), 404
    if os.path.exists(new_path):
        return jsonify({"ok": False, "error": "Ya existe una categoría con ese nombre"}), 409
    os.rename(old_path, new_path)
    return jsonify({"ok": True, "category": new_name})

@app.route("/api/feeds/category", methods=["DELETE"])
def api_delete_category():
    data     = request.get_json(force=True)
    category = _safe_cat_name(data.get("category", ""))
    filepath = os.path.join(FEEDS_DIR, f"feeds_{category}.json")
    if not os.path.exists(filepath):
        return jsonify({"ok": False, "error": "Categoría no encontrada"}), 404
    os.remove(filepath)
    return jsonify({"ok": True})

@app.route("/api/ollama/models")
def api_ollama_models():
    """Devuelve los modelos instalados en Ollama."""
    try:
        import ollama
        host = get_config().get("ollama_host", "http://localhost:11434")
        client = ollama.Client(host=host)
        models = [m.model for m in client.list().models]
        return jsonify({"ok": True, "models": models})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "models": []})

if __name__ == "__main__":
    print(f"🌐 Panel Web iniciado | DB: {DB_PATH}")
    app.run(debug=False, port=5000)