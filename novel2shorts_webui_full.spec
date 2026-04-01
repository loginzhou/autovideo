# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['webui\\main_fixed.py'],
    pathex=[],
    binaries=[],
    datas=[('webui/templates/*', 'webui/templates'), ('config.example.yaml', '.'), ('scripts/**', 'scripts')],
    hiddenimports=['fastapi', 'uvicorn', 'jinja2', 'yaml', 'requests', 'tqdm', 'pydantic', 'starlette', 'click', 'h11', 'anyio', 'idna', 'sniffio', 'typing_extensions', 'python_multipart'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='novel2shorts_webui_full',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
