# -*- mode: python ; coding: utf-8 -*-
import sys
import os
from PyInstaller.utils.hooks import collect_data_files, collect_dynamic_libs

block_cipher = None

# Collect OpenCV data files and libraries
cv2_datas = collect_data_files('cv2')
cv2_binaries = collect_dynamic_libs('cv2')

a = Analysis(
    ['MagicGardenBot.py'],
    pathex=[],
    binaries=cv2_binaries,
    datas=[
        ('images', 'src/images'),  # Include your images folder
    ] + cv2_datas,
    hiddenimports=[
        'cv2',
        'numpy',
        'PIL._tkinter_finder',
        'pyautogui',
        'pynput',
        'pynput.keyboard',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='MagicGardenBot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Set to True if you want to see console for debugging
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Add icon='icon.ico' if you have one
)