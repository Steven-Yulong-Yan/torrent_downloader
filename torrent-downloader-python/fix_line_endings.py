"""Fix line endings in Python files."""

import os


def fix_file(path):
    """Fix line endings in a file."""
    with open(path, 'r') as f:
        content = f.read().rstrip() + '\n'
    with open(path, 'w') as f:
        f.write(content)


def main():
    """Fix line endings in all Python files."""
    python_files = [
        'tests/__init__.py',
        'tests/test_version.py',
        'torrent_downloader/__init__.py',
        'torrent_downloader/cli.py',
    ]
    
    for file in python_files:
        fix_file(file)


if __name__ == '__main__':
    main() 