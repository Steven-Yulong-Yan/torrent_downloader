"""Command-line interface for Torrent Downloader."""

import argparse
import importlib.util
import sys
import tkinter as tk
from pathlib import Path


def import_gui():
    """Import the GUI module dynamically."""
    # Get the path to the GUI module
    gui_path = Path(__file__).parent.parent / "torrent_downloader_gui.py"

    if not gui_path.exists():
        print("Error: GUI module not found", file=sys.stderr)
        return None

    # Import the module
    spec = importlib.util.spec_from_file_location(
        "torrent_downloader.gui",
        gui_path,
    )
    gui = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gui)
    return gui


def main():
    """Entry point for the command-line interface."""
    parser = argparse.ArgumentParser(
        description=(
            "Download torrents using magnet links. "
            "Supports both GUI and CLI modes."
        ),
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Launch in GUI mode (default if no magnet link is provided)",
    )
    parser.add_argument(
        "magnet_link",
        nargs="?",
        help="Magnet link to download (launches GUI if not provided)",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help=(
            "Directory to save downloaded files "
            "(default: ~/Downloads/TorrentDownloader)"
        ),
    )

    args = parser.parse_args()

    # Import the GUI module
    gui = import_gui()
    if not gui:
        return 1

    # Launch GUI if requested or if no magnet link provided
    if args.gui or not args.magnet_link:
        root = tk.Tk()
        app = gui.TorrentDownloaderApp(root)

        # If magnet link was provided, add it
        if args.magnet_link:
            app.magnet_entry.insert(0, args.magnet_link)
            app.add_magnet()

        # If output directory was provided, set it
        if args.output_dir:
            app.download_dir = str(Path(args.output_dir))

        root.mainloop()
        return 0

    # CLI mode - use the GUI's functionality but without the window
    try:
        # Create the download directory if specified
        if args.output_dir:
            output_dir = Path(args.output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)

        # Create a dummy root window (hidden)
        root = tk.Tk()
        root.withdraw()

        # Create the app instance
        app = gui.TorrentDownloaderApp(root)

        # Set custom output directory if specified
        if args.output_dir:
            app.download_dir = str(output_dir)

        # Add the magnet link
        app.magnet_entry.insert(0, args.magnet_link)
        app.add_magnet()

        # Update status until all downloads complete
        while True:
            app.update_status()
            if not app.tree.get_children():
                break
            root.update()

        return 0

    except KeyboardInterrupt:
        print("\nDownload cancelled.")
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
