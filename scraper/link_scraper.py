from typing import List, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from scraper.utils import create_title_from_url

from .link import Link


def extract_links(html: str | BeautifulSoup, base_url: str) -> List[Link]:
    """Extract links (<a> tags!) from the HTML content."""
    if isinstance(html, str):
        soup = BeautifulSoup(html, "html.parser")
    else:
        soup = html
    links: Set[Link] = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag.get("href")  # This returns str, not Sequence[str]
        if href:
            # join the relative href with the base_url to get an absolute url
            absolute_url = urljoin(base_url, str(href))
            parsed_url = urlparse(str(absolute_url))

            # Create Link object with proper string type
            link = Link(
                title=create_title_from_url(absolute_url),
                href=str(absolute_url),
                text=a_tag.get_text(strip=True),
                domain=parsed_url.netloc,
            )
            links.add(link)

    return list(links)
