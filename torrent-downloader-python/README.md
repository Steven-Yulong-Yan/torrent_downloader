# Torrent Downloader (Python)

A modern, user-friendly torrent downloader application built with Python and libtorrent.

## Features

- Flexible interface with both GUI and CLI modes
- Cross-platform support (Windows, macOS, Linux)
- Easy-to-use magnet link support
- Built with libtorrent for reliable downloads
- Real-time progress tracking
- Smart download directory management

## Installation

```bash
# Install system dependencies first:

# macOS
brew install libtorrent-rasterbar

# Ubuntu/Debian
sudo apt-get install python3-libtorrent

# Fedora
sudo dnf install rb_libtorrent-python3

# Then install the package
pip install torrent-downloader-python
```

## Usage

The application supports both GUI and CLI modes:

### GUI Mode
```bash
# Launch the GUI
torrent-downloader

# Launch GUI with a pre-filled magnet link
torrent-downloader "magnet:?xt=urn:btih:..."

# Launch GUI with custom download directory
torrent-downloader --gui -o "/custom/path"
```

### CLI Mode
```bash
# Download a torrent in headless mode
torrent-downloader "magnet:?xt=urn:btih:..." -o "/custom/path"
```

### Command Line Options
```
usage: torrent-downloader [-h] [--gui] [-o OUTPUT_DIR] [magnet_link]

Download torrents using magnet links. Supports both GUI and CLI modes.

positional arguments:
  magnet_link           Magnet link to download (launches GUI if not provided)

options:
  -h, --help           show this help message and exit
  --gui                Launch in GUI mode (default if no magnet link is provided)
  -o, --output-dir     Directory to save downloaded files
                       (default: ~/Downloads/TorrentDownloader)
```

## Development

1. Clone the repository:
```bash
git clone https://github.com/yourusername/torrent-downloader.git
cd torrent-downloader/torrent-downloader-python
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run tests:
```bash
pytest
```

## Building from Source

```bash
python -m build
pip install dist/torrent-downloader-*.whl
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for downloading legal torrents only. The authors are not responsible for any misuse of this software. 