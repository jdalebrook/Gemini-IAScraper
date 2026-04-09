# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_all, collect_data_files

# ── Assets de solo lectura que van dentro del bundle ──────────────────────────
datas = [
    ('app/templates', 'app/templates'),
    ('app/static',    'app/static'),
]

# google-genai tiene imports dinámicos; collect_all captura todo
genai_d, genai_b, genai_h = collect_all('google.genai')
datas += genai_d

# feedparser necesita sus propias parsers
datas += collect_data_files('feedparser')

# ── Imports que PyInstaller no detecta solo ───────────────────────────────────
hiddenimports = [
    'flask', 'jinja2', 'werkzeug', 'click',
    'feedparser', 'sgmllib3k',
    'google.genai', 'google.generativeai',
    'google.auth', 'google.auth.transport.requests',
    'google.api_core', 'grpc',
    'ollama',
    'dotenv', 'python_dotenv',
    'sqlite3', 'requests', 'urllib3', 'certifi',
    'threading', 'webbrowser',
] + genai_h

a = Analysis(
    ['run_bundled.py'],
    pathex=['.'],
    binaries=genai_b,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    # Excluimos lo que no usamos para reducir tamaño
    excludes=['tkinter', 'matplotlib', 'PIL', 'numpy', 'pandas', 'scipy',
              'IPython', 'notebook', 'jupyter'],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='Skully',
    debug=False,
    strip=False,
    upx=True,
    console=True,           # muestra consola con el estado del procesador
    icon='app/static/icon.ico',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='Skully',
)
