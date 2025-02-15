# -*- mode: python ; coding: utf-8 -*-

import os
import sys
from PyInstaller.utils.hooks import collect_dynamic_libs

block_cipher = None

# Create runtime hooks
with open('runtime_hook.py', 'w') as f:
    f.write("""
import os
import sys

def _fix_paths():
    if sys.platform == 'win32':
        base_dir = os.path.dirname(os.path.dirname(sys.executable))
        os.environ['PYTHONPATH'] = os.path.join(base_dir, 'lib')
        os.environ['PATH'] = os.path.join(base_dir, 'lib') + os.pathsep + os.environ.get('PATH', '')

_fix_paths()
""")

a = Analysis(
    ['torrent_downloader/torrent_downloader_gui.py'],
    pathex=[],
    binaries=collect_dynamic_libs('libtorrent'),
    datas=[],
    hiddenimports=[
        'libtorrent',
        'tkinter',
        'tkinter.ttk',
        '_tkinter',
        'winreg',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['runtime_hook.py'],
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
    [],
    exclude_binaries=True,
    name='TorrentDownloader',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',
    version='file_version_info.txt',
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='TorrentDownloader'
)

# Create version info file
with open('file_version_info.txt', 'w') as f:
    f.write("""
VSVersionInfo(
  ffi=FixedFileInfo(
    filevers=(1, 0, 0, 0),
    prodvers=(1, 0, 0, 0),
    mask=0x3f,
    flags=0x0,
    OS=0x40004,
    fileType=0x1,
    subtype=0x0,
    date=(0, 0)
  ),
  kids=[
    StringFileInfo(
      [
        StringTable(
          u'040904B0',
          [StringStruct(u'CompanyName', u''),
           StringStruct(u'FileDescription', u'Torrent Downloader'),
           StringStruct(u'FileVersion', u'1.0.0'),
           StringStruct(u'InternalName', u'TorrentDownloader'),
           StringStruct(u'LegalCopyright', u'MIT License'),
           StringStruct(u'OriginalFilename', u'TorrentDownloader.exe'),
           StringStruct(u'ProductName', u'Torrent Downloader'),
           StringStruct(u'ProductVersion', u'1.0.0')])
      ]
    ),
    VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
  ]
)
""") 