# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['ocr_tool.py'],
    pathex=[],
    binaries=[],
    datas=[('C:\\Users\\Lucien\\Documents\\GitHub\\CL_Scan\\CL_Scan.ico', '.')],
    hiddenimports=['PIL._tkinter_finder', 'PIL.Image', 'PIL.ImageTk', 'PIL.ImageGrab', 'PIL.ImageEnhance', 'PIL.ImageFilter', 'pytesseract', 'pyperclip', 'customtkinter', 'tkinter', 'tkinter.ttk'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['numpy', 'pandas', 'matplotlib', 'scipy', 'pytest', 'setuptools'],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='CL_Scan',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['C:\\Users\\Lucien\\Documents\\GitHub\\CL_Scan\\CL_Scan.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='CL_Scan',
)
