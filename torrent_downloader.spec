# -*- mode: python ; coding: utf-8 -*-
import os
import sys
from PyInstaller.utils.hooks import collect_dynamic_libs

block_cipher = None

# Get Python paths
python_path = sys.executable
python_home = os.path.dirname(os.path.dirname(python_path))

# Add Tkinter dependencies
tcl_tk_root = '/System/Library/Frameworks'
tcl_lib = os.path.join(tcl_tk_root, 'Tcl.framework/Versions/Current/Resources')
tk_lib = os.path.join(tcl_tk_root, 'Tk.framework/Versions/Current/Resources')

# Create a runtime hook for Tkinter initialization
with open('tk_runtime_hook.py', 'w') as f:
    f.write("""
import os
import sys

def _fix_tkinter():
    if sys.platform == 'darwin':
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
        os.environ['TK_LIBRARY'] = os.path.join(base_dir, 'Resources', 'tk.framework', 'Versions', 'Current', 'Resources')
        os.environ['TCL_LIBRARY'] = os.path.join(base_dir, 'Resources', 'tcl.framework', 'Versions', 'Current', 'Resources')
        os.environ['TKPATH'] = os.path.join(base_dir, 'Resources')

_fix_tkinter()
""")

# Create a runtime hook for libtorrent
with open('libtorrent_runtime_hook.py', 'w') as f:
    f.write("""
import os
import sys

def _fix_libtorrent():
    if sys.platform == 'darwin':
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
        os.environ['DYLD_LIBRARY_PATH'] = os.path.join(base_dir, 'Frameworks')
        sys.path.insert(0, os.path.join(base_dir, 'Frameworks'))

_fix_libtorrent()
""")

a = Analysis(
    ['torrent_downloader_gui.py'],
    pathex=[
        '/usr/local/lib',
        os.path.join(python_home, 'lib'),
        os.path.dirname(python_path),
    ],
    binaries=[
        ('/usr/local/lib/libtorrent-rasterbar.2.0.11.dylib', 'Frameworks'),
        ('/usr/local/lib/python3.13/site-packages/libtorrent.cpython-313-darwin.so', '.'),
        ('/usr/local/lib/libtorrent-rasterbar.2.0.dylib', 'Frameworks'),
        ('/usr/local/lib/libtorrent-rasterbar.dylib', 'Frameworks'),
    ],
    datas=[
        (tcl_lib, 'tcl.framework/Versions/Current/Resources'),
        (tk_lib, 'tk.framework/Versions/Current/Resources'),
    ],
    hiddenimports=[
        'libtorrent',
        'tkinter',
        'tkinter.ttk',
        '_tkinter',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=['tk_runtime_hook.py', 'libtorrent_runtime_hook.py'],
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
    argv_emulation=True,
    target_arch='universal2',
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.icns'
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

app = BUNDLE(
    coll,
    name='TorrentDownloader.app',
    icon='icon.icns',
    bundle_identifier='com.torrentdownloader.app',
    info_plist={
        'LSMinimumSystemVersion': '10.13.0',
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHumanReadableCopyright': 'MIT License',
        'CFBundleName': 'Torrent Downloader',
        'CFBundleDisplayName': 'Torrent Downloader',
        'CFBundleGetInfoString': 'Torrent Downloader',
        'CFBundleIdentifier': 'com.torrentdownloader.app',
        'NSRequiresAquaSystemAppearance': 'No',
        'LSEnvironment': {
            'PYTHONHOME': '@executable_path/../Resources',
            'PYTHONPATH': '@executable_path/../Resources',
            'TCL_LIBRARY': '@executable_path/../Resources/tcl.framework/Versions/Current/Resources',
            'TK_LIBRARY': '@executable_path/../Resources/tk.framework/Versions/Current/Resources',
            'DYLD_LIBRARY_PATH': '@executable_path/../Resources',
            'TKPATH': '@executable_path/../Resources'
        },
    }
) 