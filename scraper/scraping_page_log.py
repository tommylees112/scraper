import csv
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional
from urllib.parse import urlparse

import pandas as pd
from loguru import logger


@dataclass
class ScrapingPage:
    """Log entry for a scraped URL"""

    timestamp: str
    url: str
    html_path: Optional[str]
    status: str
    title: str
    domain: str

    @classmethod
    def create(
        cls, url: str, html_path: Optional[str], title: str, status: str = "success"
    ) -> "ScrapingPage":
        return cls(
            timestamp=datetime.now().isoformat(),
            url=url,
            html_path=html_path,
            status=status,
            title=title,
            domain=urlparse(url).netloc,
        )


def should_skip_url(
    url: str,
    processed_pages: Optional[List[ScrapingPage]],
    overwrite: bool = False,
) -> bool:
    """
    Check if a URL should be skipped based on existing pages.

    Args:
        url: The URL to check
        processed_pages: List of already processed ScrapingPage entries
        overwrite: Whether to overwrite existing pages

    Returns:
        bool: True if the URL should be skipped, False otherwise
    """
    if processed_pages is None:
        return False

    # Find any existing pages with this URL
    existing_pages = [page for page in processed_pages if page.url == url]
    if existing_pages:
        # Only skip if there's a successful page or if we're not overwriting
        successful_pages = [page for page in existing_pages if page.status == "success"]
        if successful_pages or not overwrite:
            logger.info(f"Skipping already processed URL: {url}")
            return True

    return False


def load_or_create_page_log(log_path: Path) -> list[ScrapingPage]:
    """Load existing pages from log file or create new log file."""
    if log_path.exists():
        df = pd.read_csv(log_path)
        return [
            ScrapingPage(
                timestamp=row["timestamp"],
                url=row["url"],
                html_path=row["html_path"],
                status=row["status"],
                title=row["title"],
                domain=row["domain"],
            )
            for _, row in df.iterrows()
        ]

    # Create new log file with headers
    with open(log_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["timestamp", "url", "html_path", "status", "title", "domain"])
    return []


def append_to_page_log(log_path: Path, entry: ScrapingPage) -> None:
    """Append a new page entry to the log file."""
    with open(log_path, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(list(asdict(entry).values()))
