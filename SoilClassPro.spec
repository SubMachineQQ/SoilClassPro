import re
import sys

from PyInstaller.utils.hooks import collect_data_files

with open('soilclass/version.py', encoding='utf-8') as f:
    VERSION = re.search(r'__version__\s*=\s*"([^"]+)"', f.read()).group(1)
NUMBERS = tuple(int(n) for n in VERSION.split('.')) + (0,)

WINDOWS = sys.platform == 'win32'
MACOS = sys.platform == 'darwin'
ICON = 'build/SoilClassPro.icns' if MACOS else 'soilclass/assets/logo.ico'

version_info = None
if WINDOWS:
    from PyInstaller.utils.win32.versioninfo import (FixedFileInfo, StringFileInfo,
                                                     StringStruct, StringTable,
                                                     VarFileInfo, VarStruct,
                                                     VSVersionInfo)
    version_info = VSVersionInfo(
        ffi=FixedFileInfo(filevers=NUMBERS, prodvers=NUMBERS),
        kids=[
            StringFileInfo([StringTable('040904B0', [
                StringStruct('CompanyName', 'Batuhan Baris Doger, Erol Boz, Furkan Kagan Ekici'),
                StringStruct('FileDescription', 'SoilClass Pro'),
                StringStruct('FileVersion', VERSION),
                StringStruct('InternalName', 'SoilClassPro'),
                StringStruct('LegalCopyright', 'Copyright (c) 2026 - MIT License'),
                StringStruct('OriginalFilename', 'SoilClassPro.exe'),
                StringStruct('ProductName', 'SoilClass Pro'),
                StringStruct('ProductVersion', VERSION),
            ])]),
            VarFileInfo([VarStruct('Translation', [1033, 1200])]),
        ],
    )

datas = [('soilclass/assets', 'soilclass/assets')]
datas += collect_data_files('matplotlib')


a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=['openpyxl', 'xlrd'],
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
    name='SoilClassPro',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=[ICON],
    version=version_info,
)

if MACOS:
    app = BUNDLE(
        exe,
        name='SoilClassPro.app',
        icon=ICON,
        bundle_identifier='com.soilclasspro.app',
        info_plist={
            'CFBundleShortVersionString': VERSION,
            'CFBundleVersion': VERSION,
            'NSHighResolutionCapable': True,
        },
    )
