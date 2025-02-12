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
        os.environ['TK_LIBRARY'] = os.path.join(base_dir, 'Frameworks', 'tk', 'Resources')
        os.environ['TCL_LIBRARY'] = os.path.join(base_dir, 'Frameworks', 'tcl', 'Resources')
        os.environ['TKPATH'] = os.path.join(base_dir, 'Frameworks')

_fix_tkinter()
""")

# Create a runtime hook for libtorrent
with open('libtorrent_runtime_hook.py', 'w') as f:
    f.write("""
import os
import sys

def _fix_libtorrent():
    if sys.platform == 'darwin':
        # Get the base directory (where the .app bundle is)
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
        
        # Add all possible library paths
        library_paths = [
            os.path.join(base_dir, 'Frameworks'),
            os.path.join(base_dir, 'Resources'),
            os.path.join(base_dir, 'Resources', 'lib'),
            os.path.join(base_dir, 'Frameworks', 'libtorrent'),
            os.path.join(base_dir, 'Resources', 'libtorrent'),
        ]
        
        # Set DYLD_LIBRARY_PATH
        os.environ['DYLD_LIBRARY_PATH'] = ':'.join(
            path for path in library_paths if os.path.exists(path)
        )
        
        # Add to Python path
        for path in library_paths:
            if os.path.exists(path) and path not in sys.path:
                sys.path.insert(0, path)
        
        # Print debug info
        print("Python path:", sys.path)
        print("DYLD_LIBRARY_PATH:", os.environ.get('DYLD_LIBRARY_PATH'))
        print("Current directory:", os.getcwd())
        print("Executable path:", sys.executable)
        
        # Try to locate libtorrent files
        for path in library_paths:
            if os.path.exists(path):
                print(f"Contents of {path}:")
                try:
                    print(os.listdir(path))
                except Exception as e:
                    print(f"Error listing {path}: {e}")

_fix_libtorrent()
""")

a = Analysis(
    ['torrent_downloader_gui.py'],
    pathex=[
        '/usr/local/lib',
        os.path.join(python_home, 'lib'),
        os.path.dirname(python_path),
        '/usr/local/lib/python3.13/site-packages',
    ],
    binaries=[
        ('/usr/local/lib/libtorrent-rasterbar.2.0.11.dylib', 'Frameworks/libtorrent'),
        ('/usr/local/lib/python3.13/site-packages/libtorrent.cpython-313-darwin.so', 'Frameworks/libtorrent'),
        ('/usr/local/lib/libtorrent-rasterbar.2.0.dylib', 'Frameworks/libtorrent'),
        ('/usr/local/lib/libtorrent-rasterbar.dylib', 'Frameworks/libtorrent'),
    ],
    datas=[
        (tcl_lib, 'Frameworks/tcl/Resources'),
        (tk_lib, 'Frameworks/tk/Resources'),
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
    name='TorrentDownloader-Intel',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Disable console output now that it's working
    disable_windowed_traceback=False,
    argv_emulation=True,
    target_arch='x86_64',
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
    name='TorrentDownloader-Intel'
)

app = BUNDLE(
    coll,
    name='TorrentDownloader-Intel.app',
    icon='icon.icns',
    bundle_identifier='com.torrentdownloader.app',
    info_plist={
        'LSMinimumSystemVersion': '10.13.0',
        'NSHighResolutionCapable': True,
        'CFBundleShortVersionString': '1.0.0',
        'CFBundleVersion': '1.0.0',
        'NSHumanReadableCopyright': 'MIT License',
        'CFBundleName': 'Torrent Downloader (Intel)',
        'CFBundleDisplayName': 'Torrent Downloader (Intel)',
        'CFBundleGetInfoString': 'Torrent Downloader (Intel)',
        'CFBundleIdentifier': 'com.torrentdownloader.app',
        'NSRequiresAquaSystemAppearance': 'No',
        'LSEnvironment': {
            'PYTHONHOME': '@executable_path/../Resources',
            'PYTHONPATH': '@executable_path/../Resources:@executable_path/../Frameworks/libtorrent',
            'TCL_LIBRARY': '@executable_path/../Frameworks/tcl/Resources',
            'TK_LIBRARY': '@executable_path/../Frameworks/tk/Resources',
            'DYLD_LIBRARY_PATH': '@executable_path/../Frameworks/libtorrent:@executable_path/../Frameworks',
            'TKPATH': '@executable_path/../Frameworks'
        },
    }
) 