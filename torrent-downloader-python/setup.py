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
    version="1.0.14",
    description='A Torrent Downloader with a graphical user interface built using Tkinter and libtorrent',
    author='Your Name',
    author_email='your_email@example.com',
    py_modules=['torrent_downloader_gui'],
    install_requires=[
        'python-libtorrent'
    ] + libtorrent_requires,
    entry_points={
        'console_scripts': [
            'torrent-downloader = torrent_downloader_gui:main'
        ]
    }
) 