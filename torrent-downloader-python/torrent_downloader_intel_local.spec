# -*- mode: python ; coding: utf-8 -*-

import os
import sys
import tkinter
from PyInstaller.utils.hooks import collect_dynamic_libs

block_cipher = None

# Get Python paths
python_path = sys.executable
python_home = os.path.dirname(os.path.dirname(python_path))

# Get Tcl/Tk paths from system frameworks
tcl_lib = '/System/Library/Frameworks/Tcl.framework/Versions/Current/Resources'
tk_lib = '/System/Library/Frameworks/Tk.framework/Versions/Current/Resources'

# Create a runtime hook for Tkinter initialization
with open('tk_runtime_hook.py', 'w') as f:
    f.write("""
import os
import sys
import platform

def _fix_tkinter():
    if sys.platform == 'darwin':
        # Get the base directory (where the .app bundle is)
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
            
            # Set Tk/Tcl library paths relative to the app bundle
            os.environ['TK_LIBRARY'] = os.path.join(base_dir, 'Frameworks', 'tk', 'Resources')
            os.environ['TCL_LIBRARY'] = os.path.join(base_dir, 'Frameworks', 'tcl', 'Resources')
            os.environ['TKPATH'] = os.path.join(base_dir, 'Frameworks')
            
            # Force disable all menu-related features
            os.environ['TK_SILENCE_DEPRECATION'] = '1'
            os.environ['TK_NO_NATIVE_MENUBAR'] = '1'
            os.environ['TKPATH'] = '/System/Library/Frameworks'
            
            # Use system Tcl/Tk frameworks
            os.environ['TCL_LIBRARY'] = '/System/Library/Frameworks/Tcl.framework/Versions/Current/Resources'
            os.environ['TK_LIBRARY'] = '/System/Library/Frameworks/Tk.framework/Versions/Current/Resources'
            
            # Additional environment variables to control Tk behavior
            os.environ['TK_COCOA_FORCE_WINDOW_MENU'] = '0'
            os.environ['TK_COCOA_USE_SYSTEM_MENUBAR'] = '0'
            os.environ['TK_COCOA_DISABLE_MENUBAR'] = '1'
            
            # Patch Tkinter's _tkinter module to prevent menu creation
            try:
                import _tkinter
                def _patched_call(*args, **kwargs):
                    cmd = args[0] if args else ''
                    if isinstance(cmd, str) and ('menu' in cmd.lower() or 'menubar' in cmd.lower()):
                        return None
                    return original_call(*args, **kwargs)
                
                if hasattr(_tkinter, 'TkappType'):
                    if hasattr(_tkinter.TkappType, 'call'):
                        original_call = _tkinter.TkappType.call
                        _tkinter.TkappType.call = _patched_call
            except Exception as e:
                print("Failed to patch Tkinter:", e)
        
        # Additional debug info
        print("Python executable:", sys.executable)
        print("TK_LIBRARY:", os.environ.get('TK_LIBRARY'))
        print("TCL_LIBRARY:", os.environ.get('TCL_LIBRARY'))
        print("TKPATH:", os.environ.get('TKPATH'))
        print("TK_NO_NATIVE_MENUBAR:", os.environ.get('TK_NO_NATIVE_MENUBAR'))

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
    ['torrent_downloader/torrent_downloader_gui.py'],
    pathex=[
        '/usr/local/lib',
        os.path.join(python_home, 'lib'),
        os.path.dirname(python_path),
        '/usr/local/lib/python3.13/site-packages',
        '/usr/local/Cellar/libtorrent-rasterbar/2.0.11/lib',
        '/usr/local/Cellar/libtorrent-rasterbar/2.0.11/lib/python3.13/site-packages',
        '/usr/local/opt/python-tk@3.13/libexec',
    ],
    binaries=[
        ('/usr/local/Cellar/libtorrent-rasterbar/2.0.11/lib/libtorrent-rasterbar.2.0.11.dylib', 'Frameworks/libtorrent'),
        ('/usr/local/Cellar/libtorrent-rasterbar/2.0.11/lib/python3.13/site-packages/libtorrent.cpython-313-darwin.so', 'Frameworks/libtorrent'),
        ('/usr/local/opt/python-tk@3.13/libexec/_tkinter.cpython-313-darwin.so', 'lib-dynload'),
    ],
    datas=[
        (tcl_lib, 'tcl'),
        (tk_lib, 'tk'),
    ],
    hiddenimports=[
        'libtorrent',
        'tkinter',
        'tkinter.ttk',
        '_tkinter',
        'tkinter.messagebox',
        'tkinter.filedialog',
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
            'TCL_LIBRARY': '/System/Library/Frameworks/Tcl.framework/Versions/Current/Resources',
            'TK_LIBRARY': '/System/Library/Frameworks/Tk.framework/Versions/Current/Resources',
            'DYLD_LIBRARY_PATH': '@executable_path/../Frameworks/libtorrent:@executable_path/../Frameworks',
            'TKPATH': '/System/Library/Frameworks',
            'TK_SILENCE_DEPRECATION': '1',
            'TK_NO_NATIVE_MENUBAR': '1',
            'TK_COCOA_FORCE_WINDOW_MENU': '0',
            'TK_COCOA_USE_SYSTEM_MENUBAR': '0',
            'TK_COCOA_DISABLE_MENUBAR': '1'
        },
    }
) 