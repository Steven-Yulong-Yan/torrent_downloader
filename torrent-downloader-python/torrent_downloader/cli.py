"""Command-line interface for Torrent Downloader."""

import argparse
import sys


def main():
    """Entry point for the command-line interface."""
    parser = argparse.ArgumentParser(
        description="Download torrents using magnet links."
    )
    parser.add_argument(
        "magnet_link",
        help="Magnet link to download",
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        help="Directory to save downloaded files",
        default=".",
    )

    args = parser.parse_args()
    print(f"Downloading from: {args.magnet_link}")
    print(f"Saving to: {args.output_dir}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
