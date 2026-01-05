# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

# Main application
main_analysis = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('config.template.json', '.'),
    ],
    hiddenimports=[
        'serial',
        'requests',
        'json',
        'tkinter',
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

main_pyz = PYZ(main_analysis.pure, main_analysis.zipped_data, cipher=block_cipher)

main_exe = EXE(
    main_pyz,
    main_analysis.scripts,
    [],
    exclude_binaries=True,
    name='waybridge_agent',
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
    icon=None,
)

# Settings GUI
settings_analysis = Analysis(
    ['settings_gui.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
        ('config.template.json', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'json',
        'requests',
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

settings_pyz = PYZ(settings_analysis.pure, settings_analysis.zipped_data, cipher=block_cipher)

settings_exe = EXE(
    settings_pyz,
    settings_analysis.scripts,
    [],
    exclude_binaries=True,
    name='waybridge_settings',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI application - no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# Launcher
launcher_analysis = Analysis(
    ['launcher.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('config.json', '.'),
    ],
    hiddenimports=[
        'tkinter',
        'json',
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

launcher_pyz = PYZ(launcher_analysis.pure, launcher_analysis.zipped_data, cipher=block_cipher)

launcher_exe = EXE(
    launcher_pyz,
    launcher_analysis.scripts,
    [],
    exclude_binaries=True,
    name='waybridge_launcher',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # GUI application - no console window
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)

# Collect all files
coll = COLLECT(
    main_exe,
    main_analysis.binaries,
    main_analysis.zipfiles,
    main_analysis.datas,
    settings_exe,
    settings_analysis.binaries,
    settings_analysis.zipfiles,
    settings_analysis.datas,
    launcher_exe,
    launcher_analysis.binaries,
    launcher_analysis.zipfiles,
    launcher_analysis.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='waybridge_agent',
)
