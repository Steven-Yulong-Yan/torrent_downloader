from setuptools import setup, find_packages

setup(
    name="torrent-downloader-python",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "libtorrent>=2.0.0",
    ],
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