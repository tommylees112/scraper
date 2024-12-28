import os
import re
from pathlib import Path
from urllib.parse import urlparse


def create_title_from_url(url: str) -> str:
    path = Path(url)
    parts = [p.replace("-", "_").lower() for p in path.parts]
    meaningful_parts = [p for p in parts if p][-3:]
    return "_".join(meaningful_parts)


def convert_to_absolute_url(href: str, base_url: str) -> str:
    if href.startswith("/"):
        parsed = urlparse(base_url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        return f"{domain}{href}"
    return href


def create_dir_name_from_netloc(url: str) -> str:
    """Convert a URL's netloc into a snake_case directory name.

    Example:
        'https://moz.com/beginners-guide-to-seo' -> 'moz_com'
    """
    parsed = urlparse(url)
    netloc = parsed.netloc.lower()
    # Remove any www. prefix if present
    netloc = netloc.replace("www.", "")
    # Replace dots and other special characters with underscores
    clean_name = re.sub(r"[^a-z0-9]+", "_", netloc)
    # Remove leading/trailing underscores
    return clean_name.strip("_")


def get_default_downloads_dir() -> Path:
    """Get the default downloads directory for the current OS."""
    if os.name == "nt":  # Windows
        return Path.home() / "Downloads"
    else:  # macOS and Linux
        return Path.home() / "Downloads"
