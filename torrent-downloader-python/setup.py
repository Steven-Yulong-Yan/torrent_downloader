from setuptools import setup, find_packages
import sys

# Define platform-specific dependencies
if sys.platform == 'win32':
    libtorrent_requires = ['libtorrent>=2.0.0']
else:
    # On macOS and Linux, libtorrent should be installed via system package manager
    libtorrent_requires = []

setup(
    name="torrent-downloader-python",
    version="1.0.6",
    packages=find_packages(),
    package_data={
        'torrent_downloader': ['torrent_downloader_gui.py'],
    },
    install_requires=libtorrent_requires,
    entry_points={
        "console_scripts": [
            "torrent-downloader=torrent_downloader.cli:main",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="A modern, user-friendly torrent downloader application",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    keywords="torrent, downloader, p2p, bittorrent, libtorrent",
    url="https://github.com/yourusername/torrent-downloader",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/torrent-downloader/issues",
        "Documentation": "https://github.com/yourusername/torrent-downloader#readme",
        "Source Code": "https://github.com/yourusername/torrent-downloader",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Internet :: WWW/HTTP",
    ],
    python_requires=">=3.8",
) 