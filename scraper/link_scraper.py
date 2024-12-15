from typing import List, Set
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from .link import Link


def extract_links(html: str, base_url: str) -> List[Link]:
    """Extract links from the HTML content."""
    soup = BeautifulSoup(html, "html.parser")
    links: Set[Link] = set()

    for a_tag in soup.find_all("a", href=True):
        href = a_tag.get("href")  # This returns str, not Sequence[str]
        if href:
            # Fix the type error by ensuring href is str
            absolute_url = urljoin(base_url, str(href))
            parsed_url = urlparse(str(absolute_url))

            # Create Link object with proper string type
            link = Link(
                href=str(absolute_url),
                text=a_tag.get_text(strip=True),
                domain=parsed_url.netloc,
            )
            links.add(link)

    return list(links)
