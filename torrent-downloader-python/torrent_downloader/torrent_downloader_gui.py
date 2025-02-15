import tkinter as tk
from tkinter import scrolledtext, messagebox, ttk
import sys
import time
import os
import logging
import traceback

# Set up platform-specific paths
def get_app_data_dir():
    """Get the appropriate directory for application data based on platform."""
    if sys.platform == 'win32':
        app_data = os.getenv('LOCALAPPDATA')
        if app_data is None:
            app_data = os.path.expanduser('~')
        return os.path.join(app_data, 'TorrentDownloader')
    elif sys.platform == 'darwin':
        return os.path.expanduser('~/Library/Application Support/TorrentDownloader')
    else:  # Linux and other Unix-like
        return os.path.expanduser('~/.local/share/TorrentDownloader')

def get_log_dir():
    """Get the appropriate directory for logs based on platform."""
    if sys.platform == 'win32':
        return os.path.join(get_app_data_dir(), 'Logs')
    elif sys.platform == 'darwin':
        return os.path.expanduser('~/Library/Logs/TorrentDownloader')
    else:  # Linux and other Unix-like
        return os.path.join(get_app_data_dir(), 'logs')

def get_cache_dir():
    """Get the appropriate directory for cache based on platform."""
    if sys.platform == 'win32':
        return os.path.join(get_app_data_dir(), 'Cache')
    elif sys.platform == 'darwin':
        return os.path.expanduser('~/Library/Caches/TorrentDownloader')
    else:  # Linux and other Unix-like
        return os.path.expanduser('~/.cache/TorrentDownloader')

def get_downloads_dir():
    """Get the appropriate directory for downloads based on platform."""
    if sys.platform == 'win32':
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
                downloads_path = winreg.QueryValueEx(key, "{374DE290-123F-4565-9164-39C4925E467B}")[0]
            return os.path.join(downloads_path, 'TorrentDownloader')
        except Exception as e:
            logging.warning(f"Failed to get Windows Downloads folder: {e}")
            try:
                # Try Documents folder instead
                with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders") as key:
                    documents_path = winreg.QueryValueEx(key, "Personal")[0]
                return os.path.join(documents_path, 'TorrentDownloader')
            except Exception as e:
                logging.warning(f"Failed to get Windows Documents folder: {e}")
                # Fallback to user's home directory
                return os.path.join(os.path.expanduser('~'), 'Downloads', 'TorrentDownloader')
    elif sys.platform == 'darwin':
        return os.path.expanduser('~/Downloads/TorrentDownloader')
    else:  # Linux and other Unix-like
        # Try XDG_DOWNLOAD_DIR first
        xdg_download_dir = os.getenv('XDG_DOWNLOAD_DIR')
        if xdg_download_dir:
            return os.path.join(xdg_download_dir, 'TorrentDownloader')
        return os.path.join(os.path.expanduser('~/Downloads'), 'TorrentDownloader')

def get_fallback_downloads_dir():
    """Get the fallback directory for downloads if primary location fails."""
    if sys.platform == 'win32':
        return os.path.join(get_app_data_dir(), 'Downloads')
    elif sys.platform == 'darwin':
        return os.path.join(get_cache_dir(), 'Downloads')
    else:  # Linux and other Unix-like
        return os.path.join(get_cache_dir(), 'downloads')

# Create necessary directories
app_data_dir = get_app_data_dir()
log_dir = get_log_dir()
cache_dir = get_cache_dir()

for directory in [app_data_dir, log_dir, cache_dir]:
    os.makedirs(directory, exist_ok=True)

# Set up logging to both file and stderr
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'torrentdownloader.log')),
        logging.StreamHandler(sys.stderr)
    ]
)

# Log startup information
logging.info("Application starting")
logging.debug(f"Platform: {sys.platform}")
logging.debug(f"Python executable: {sys.executable}")
logging.debug(f"Python version: {sys.version}")
logging.debug(f"Current working directory: {os.getcwd()}")
logging.debug(f"Script directory: {os.path.dirname(os.path.abspath(__file__))}")
logging.debug(f"App data directory: {app_data_dir}")
logging.debug(f"Log directory: {log_dir}")
logging.debug(f"Cache directory: {cache_dir}")

try:
    import libtorrent as lt
except ImportError as e:
    logging.error(f"Failed to import libtorrent: {e}")
    logging.error(f"Python path: {sys.path}")
    logging.error(f"Current directory: {os.getcwd()}")
    logging.error(f"Environment: {dict(os.environ)}")
    print('Error: libtorrent module not found. Please install it with pip install python-libtorrent (or similar package).')
    sys.exit(1)


class TorrentDownloaderApp:
    def __init__(self, master):
        self.master = master
        master.title("Torrent Downloader")
        master.geometry("1000x600")
        
        # Apply menu prevention patches
        if sys.platform == 'darwin':
            try:
                # Disable window manager decorations that might trigger menu creation
                master.overrideredirect(True)
                master.overrideredirect(False)
                
                # Apply our Tcl interpreter patches
                if hasattr(master.tk, '_patch_tcl_interpreter'):
                    master.tk._patch_tcl_interpreter(master)
                
                # Prevent any menu-related calls
                master.createcommand = lambda *args: None
                master.tk.call = lambda *args: None if 'menu' in str(args).lower() else master.tk.call(*args)
                
                # Force update to ensure changes take effect
                master.update_idletasks()
            except Exception:
                pass
        
        # Create a custom toolbar frame
        self.toolbar = ttk.Frame(master)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        
        # Add toolbar buttons
        self.open_folder_button = ttk.Button(self.toolbar, text="Open Downloads", command=self.open_download_folder)
        self.open_folder_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.help_button = ttk.Button(self.toolbar, text="Help", command=self.show_help)
        self.help_button.pack(side=tk.LEFT, padx=5, pady=5)
        
        self.quit_button = ttk.Button(self.toolbar, text="Quit", command=self.quit_app)
        self.quit_button.pack(side=tk.RIGHT, padx=5, pady=5)
        
        # Configure style
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TButton', padding=5)
        self.style.configure('TLabel', background='#f0f0f0')
        
        # Main container
        self.main_container = ttk.Frame(master, padding="10")
        self.main_container.pack(fill=tk.BOTH, expand=True)

        # Top frame for magnet link entry
        self.frame_top = ttk.Frame(self.main_container)
        self.frame_top.pack(fill=tk.X, pady=(0, 10))

        self.label = ttk.Label(self.frame_top, text="Magnet Link:")
        self.label.pack(side=tk.LEFT, padx=(0, 5))

        self.magnet_entry = ttk.Entry(self.frame_top)
        self.magnet_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

        self.add_button = ttk.Button(self.frame_top, text="Add Magnet", command=self.add_magnet)
        self.add_button.pack(side=tk.LEFT, padx=5)

        # Status frame with Treeview
        self.frame_status = ttk.Frame(self.main_container)
        self.frame_status.pack(fill=tk.BOTH, expand=True)

        # Create Treeview
        self.tree = ttk.Treeview(self.frame_status, columns=("name", "progress", "speed", "eta", "peers"), show="headings")
        
        # Define column headings and widths
        self.tree.heading("name", text="Name")
        self.tree.heading("progress", text="Progress")
        self.tree.heading("speed", text="Speed")
        self.tree.heading("eta", text="ETA")
        self.tree.heading("peers", text="Peers")
        
        # Set column widths
        self.tree.column("name", width=400, minwidth=200)
        self.tree.column("progress", width=100, minwidth=80)
        self.tree.column("speed", width=200, minwidth=150)
        self.tree.column("eta", width=100, minwidth=80)
        self.tree.column("peers", width=80, minwidth=60)

        # Add scrollbars
        vsb = ttk.Scrollbar(self.frame_status, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        # Grid layout
        self.tree.grid(column=0, row=0, sticky="nsew")
        vsb.grid(column=1, row=0, sticky="ns")
        
        # Configure grid weights
        self.frame_status.grid_columnconfigure(0, weight=1)
        self.frame_status.grid_rowconfigure(0, weight=1)

        # Setup libtorrent session
        self.ses = lt.session()
        
        # Configure session settings using the modern API
        settings = {
            'listen_interfaces': '0.0.0.0:6881,[::]:6881',  # Listen on all interfaces, both IPv4 and IPv6
            'enable_dht': True,
            'enable_lsd': True,  # Local Service Discovery
            'enable_upnp': True,
            'enable_natpmp': True,
            'outgoing_interfaces': '',  # Empty string means all interfaces
            'alert_mask': lt.alert.category_t.all_categories,
            'download_rate_limit': 0,  # 0 means unlimited
            'upload_rate_limit': 0,    # 0 means unlimited
        }
        self.ses.apply_settings(settings)
        logging.info("Configured libtorrent session with settings: %s", settings)

        # Set up download directory
        self.download_dir = get_downloads_dir()
        try:
            os.makedirs(self.download_dir, exist_ok=True)
            logging.info(f"Created download directory: {self.download_dir}")
        except OSError as e:
            logging.error(f"Failed to create downloads directory: {e}")
            # Fall back to alternative location
            self.download_dir = get_fallback_downloads_dir()
            os.makedirs(self.download_dir, exist_ok=True)
            logging.info(f"Using fallback download directory: {self.download_dir}")
            
        self.params = {
            'save_path': self.download_dir,
            'storage_mode': lt.storage_mode_t(2),
        }

        logging.info(f"Using download directory: {self.download_dir}")

        # Update help text with actual download location
        self.download_location_text = f"Downloads folder: {self.download_dir}"

        self.handles = []
        self.update_status()

    def show_help(self):
        help_text = f"""
Torrent Downloader Help

1. Enter a magnet link in the text field
2. Click 'Add Magnet' to start downloading
3. Monitor progress in the list below

{self.download_location_text}

For support, please visit:
https://github.com/yourusername/torrent_downloader
"""
        messagebox.showinfo("Help", help_text)

    def open_download_folder(self):
        """Open the downloads folder in the system file explorer."""
        try:
            if sys.platform == 'win32':
                os.startfile(self.download_dir)
            elif sys.platform == 'darwin':
                os.system(f'open "{self.download_dir}"')
            else:
                os.system(f'xdg-open "{self.download_dir}"')
        except Exception as e:
            logging.error(f"Failed to open downloads folder: {e}")
            messagebox.showerror("Error", f"Could not open downloads folder:\n{e}")

    def add_magnet(self):
        magnet_link = self.magnet_entry.get().strip()
        if magnet_link:
            try:
                handle = lt.add_magnet_uri(self.ses, magnet_link, self.params)
                self.handles.append(handle)
                self.magnet_entry.delete(0, tk.END)
            except Exception as e:
                messagebox.showerror("Error", f"Failed to add magnet: {e}")

    def quit_app(self):
        self.master.quit()

    def format_size(self, size_bytes):
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def update_status(self):
        try:
            # Clear existing items
            for item in self.tree.get_children():
                self.tree.delete(item)
                
            for i, handle in enumerate(self.handles):
                s = handle.status()
                
                if not handle.has_metadata():
                    self.tree.insert("", "end", values=(
                        "Downloading metadata...",
                        "N/A",
                        "N/A",
                        "N/A",
                        str(s.num_peers)
                    ))
                else:
                    name = handle.name()[:47] + "..." if len(handle.name()) > 47 else handle.name()
                    progress = f"{s.progress * 100:.1f}%"
                    
                    d_rate = self.format_size(s.download_rate)
                    u_rate = self.format_size(s.upload_rate)
                    speed = f"↓{d_rate}/s ↑{u_rate}/s"
                    
                    eta = "N/A"
                    if s.download_rate > 0:
                        remaining_bytes = s.total_wanted - s.total_done
                        seconds = remaining_bytes / s.download_rate
                        m, sec = divmod(int(seconds), 60)
                        h, m = divmod(m, 60)
                        eta = f"{h:d}:{m:02d}:{sec:02d}"

                    self.tree.insert("", "end", values=(
                        name,
                        progress,
                        speed,
                        eta,
                        str(s.num_peers)
                    ))

            if not self.handles:
                self.tree.insert("", "end", values=(
                    "No active torrents",
                    "",
                    "",
                    "",
                    ""
                ))
        except Exception as e:
            print(f"Error updating status: {e}")
        finally:
            self.master.after(1000, self.update_status)


def main():
    try:
        logging.info("Starting TorrentDownloader application")
        logging.debug(f"Python path: {sys.path}")
        logging.debug(f"Current directory: {os.getcwd()}")
        logging.debug(f"Environment variables: {dict(os.environ)}")
        
        root = tk.Tk()
        # Disable system menu bar on macOS
        if sys.platform == 'darwin':
            logging.info("Configuring macOS-specific settings")
            root.createcommand('::tk::mac::ShowPreferences', lambda: None)
            root.createcommand('::tk::mac::ReopenApplication', lambda: None)
            root.createcommand('::tk::mac::ShowHelp', lambda: None)
            root.createcommand('::tk::mac::Quit', lambda: None)
            
        app = TorrentDownloaderApp(root)
        root.mainloop()
    except Exception as e:
        logging.error(f"Error starting application: {e}")
        logging.error(traceback.format_exc())
        print(f"Error starting application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # This GUI version does not accept command-line arguments.
    if len(sys.argv) > 1:
        print("Error: Do not provide magnet links as command-line arguments. Use the GUI to add magnet links.")
        sys.exit(1)
    main() 