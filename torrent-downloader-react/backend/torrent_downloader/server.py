from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import libtorrent as lt
import os
import sys
import logging
from typing import Dict, List, Optional
import time
from pathlib import Path
import subprocess
import uvicorn
import pkg_resources

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, this will be the hosted frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve static files (the React frontend)
try:
    static_files_dir = pkg_resources.resource_filename(__name__, "static")
    app.mount("/", StaticFiles(directory=static_files_dir, html=True), name="static")
except Exception as e:
    logging.warning(f"Could not mount static files: {e}")

# Set up platform-specific paths
def get_downloads_dir() -> Path:
    if sys.platform == 'win32':
        downloads = os.path.expanduser('~/Downloads')
    elif sys.platform == 'darwin':
        downloads = os.path.expanduser('~/Downloads')
    else:  # Linux and other Unix-like
        downloads = os.path.expanduser('~/Downloads')
    
    torrent_dir = Path(downloads) / 'TorrentDownloader'
    torrent_dir.mkdir(parents=True, exist_ok=True)
    return torrent_dir

def open_folder(path: str) -> bool:
    """Open the folder using the system's default file explorer."""
    try:
        if sys.platform == 'win32':
            os.startfile(path)
        elif sys.platform == 'darwin':
            subprocess.run(['open', path], check=True)
        else:  # Linux and other Unix-like
            subprocess.run(['xdg-open', path], check=True)
        return True
    except Exception as e:
        logging.error(f"Failed to open folder: {e}")
        return False

# Initialize download directory
DOWNLOAD_PATH = get_downloads_dir()

# Initialize libtorrent session
session = lt.session()
session.listen_on(6881, 6891)

# Store active torrents
active_torrents: Dict[str, lt.torrent_handle] = {}

class TorrentRequest(BaseModel):
    magnet_link: str

class TorrentInfo(BaseModel):
    id: str
    name: str
    progress: float
    download_speed: float
    state: str
    total_size: int
    downloaded: int

@app.post("/api/torrent/add")
async def add_torrent(request: TorrentRequest):
    try:
        # Add the torrent
        params = lt.parse_magnet_uri(request.magnet_link)
        params.save_path = str(DOWNLOAD_PATH)
        handle = session.add_torrent(params)
        
        # Wait for metadata
        timeout = 30
        start_time = time.time()
        while not handle.has_metadata():
            if time.time() - start_time > timeout:
                raise HTTPException(status_code=408, detail="Timeout waiting for torrent metadata")
            time.sleep(0.1)
        
        torrent_id = str(handle.info_hash())
        active_torrents[torrent_id] = handle
        
        return {"id": torrent_id, "message": "Torrent added successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/torrent/list")
async def list_torrents() -> List[TorrentInfo]:
    result = []
    for torrent_id, handle in active_torrents.items():
        status = handle.status()
        
        # Get the state string
        state_str = "unknown"
        if status.state == lt.torrent_status.downloading:
            state_str = "downloading"
        elif status.state == lt.torrent_status.seeding:
            state_str = "seeding"
        elif status.state == lt.torrent_status.finished:
            state_str = "finished"
        elif status.state == lt.torrent_status.checking_files:
            state_str = "checking"
        
        info = TorrentInfo(
            id=torrent_id,
            name=handle.name(),
            progress=status.progress * 100,
            download_speed=status.download_rate / 1024,  # Convert to KB/s
            state=state_str,
            total_size=status.total_wanted,
            downloaded=status.total_wanted_done
        )
        result.append(info)
    
    return result

@app.delete("/api/torrent/{torrent_id}")
async def remove_torrent(torrent_id: str, delete_files: bool = False):
    if torrent_id not in active_torrents:
        raise HTTPException(status_code=404, detail="Torrent not found")
    
    handle = active_torrents[torrent_id]
    session.remove_torrent(handle, 1 if delete_files else 0)
    del active_torrents[torrent_id]
    
    return {"message": "Torrent removed successfully"}

@app.get("/api/downloads/path")
async def get_downloads_path():
    return {"path": str(DOWNLOAD_PATH)}

@app.post("/api/downloads/open")
async def open_downloads():
    success = open_folder(str(DOWNLOAD_PATH))
    if not success:
        raise HTTPException(status_code=500, detail="Failed to open downloads folder")
    return {"message": "Downloads folder opened successfully"}

def main():
    # Set up logging
    log_dir = Path.home() / ".torrent-downloader" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "torrent-downloader.log"),
            logging.StreamHandler()
        ]
    )
    
    # Start the server
    uvicorn.run(app, host="127.0.0.1", port=8000)

if __name__ == "__main__":
    main() 