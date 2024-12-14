from bs4 import BeautifulSoup, Tag
from loguru import logger

from .link import Link
from .utils import convert_to_absolute_url, create_title_from_url


def extract_navigation_links(soup: BeautifulSoup, base_url: str) -> list[Link]:
    nav = soup.find("nav", class_=lambda x: x and "sideBar" in x)
    if not nav or not isinstance(nav, Tag):
        logger.error("Navigation sidebar not found.")
        return []
    else:
        class_name = nav.get("class")
        logger.info(f"Navigation sidebar found. {class_name}")

    links = []
    for link in nav.find_all("a", href=True):
        text = link.get_text(strip=True)
        href = convert_to_absolute_url(link["href"], base_url)
        page_title = create_title_from_url(href)
        links.append(Link(page_title, href, text))

    return links
