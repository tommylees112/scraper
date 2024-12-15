import requests
from bs4 import BeautifulSoup
from scrapingant_client import ScrapingAntClient


def get_content_with_requests(url: str) -> tuple[str, BeautifulSoup]:
    """Get content using requests library."""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return response.text, soup


def get_content_with_scraping_ant(
    url: str, client: ScrapingAntClient
) -> tuple[str, BeautifulSoup]:
    """Get content using ScrapingAnt."""
    response = client.general_request(url)
    soup = BeautifulSoup(response.content, "html.parser")
    return response.content, soup
