# Torrent Downloader (Python)

A modern, user-friendly torrent downloader application built with Python and libtorrent.

## Features

- Simple command-line interface
- Cross-platform support (Windows, macOS, Linux)
- Easy-to-use magnet link support
- Built with libtorrent for reliable downloads

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

```bash
# Download using a magnet link
torrent-downloader "magnet:?xt=urn:btih:..."
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

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

This software is for downloading legal torrents only. The authors are not responsible for any misuse of this software. 