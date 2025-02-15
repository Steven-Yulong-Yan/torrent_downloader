"""Test version information."""

from torrent_downloader import __version__


def test_version():
    """Test that version is a string."""
    assert isinstance(__version__, str)
    assert __version__ == "1.0.14" 