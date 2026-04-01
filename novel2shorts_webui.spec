# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['webui\\main_fixed.py'],
    pathex=[],
    binaries=[],
    datas=[('webui/templates/*', 'webui/templates'), ('config.example.yaml', '.'), ('scripts/*', 'scripts')],
    hiddenimports=['fastapi', 'uvicorn', 'jinja2', 'yaml', 'requests', 'tqdm'],
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
    [],
    exclude_binaries=True,
    name='novel2shorts_webui',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='novel2shorts_webui',
)
