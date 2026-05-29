# -*- mode: python ; coding: utf-8 -*-
#
# PyInstaller spec for CA FirmHub
# Compatible with Python 3.9 – 3.13
#

from PyInstaller.utils.hooks import collect_data_files, collect_submodules

block_cipher = None

# ── Data files bundled inside the exe ─────────────────────────
datas = []
datas += collect_data_files('flask')
datas += collect_data_files('jinja2')
datas += collect_data_files('docx')
datas += collect_data_files('openpyxl')
datas += collect_data_files('waitress')

# App source files — needed by runpy.run_path in launcher.py
datas += [
    ('main.py',               '.'),
    ('auth.py',               '.'),
    ('database.py',           '.'),
    ('config.py',             '.'),
    ('booklet_generator.py',  '.'),
    ('seed_data.py',          '.'),
    ('static',                'static'),
    ('firm_identity.json',    '.'),
]

# ── Hidden imports ─────────────────────────────────────────────
hiddenimports = (
    collect_submodules('flask') +
    collect_submodules('jinja2') +
    collect_submodules('werkzeug') +
    collect_submodules('waitress') +
    collect_submodules('docx') +
    collect_submodules('openpyxl') +
    [
        'jwt',
        'jwt.algorithms',
        '_cffi_backend',
        'sqlite3',
        'email.mime.text',
        'email.mime.multipart',
        'runpy',
    ]
)

# ── Analysis ───────────────────────────────────────────────────
a = Analysis(
    ['launcher.py'],
    pathex=['.'],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter', 'matplotlib', 'numpy', 'pandas',
        'PIL', 'scipy', 'PyQt5', 'PyQt6', 'wx',
        'test', 'unittest',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CAFirmHub',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='CAFirmHub',
)
