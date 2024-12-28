from dataclasses import dataclass
from typing import Any

import requests
from bs4 import BeautifulSoup
from scrapingant_client import ScrapingAntClient


@dataclass
class MockResponse:
    content: str


class MockClient:
    """Mock the behaviour of the ScrapingAntClient for keeping consistent API

    We need:
    self.content: the html content as a string


    requests.Response:
        ['ConnectTimeout', 'ConnectionError', 'DependencyWarning', 'FileModeWarning', 'HTTPError', 'JSONDecodeError', 'NullHandler', 'PreparedRequest', 'ReadTimeout', 'Request', 'RequestException', 'RequestsDependencyWarning', 'Response', 'Session', 'Timeout', 'TooManyRedirects', 'URLRequired', '__author__', '__author_email__', '__build__', '__builtins__', '__cached__', '__cake__', '__copyright__', '__description__', '__doc__', '__file__', '__license__', '__loader__', '__name__', '__package__', '__path__', '__spec__', '__title__', '__url__', '__version__', '_check_cryptography', '_internal_utils', 'adapters', 'api', 'auth', 'certs', 'chardet_version', 'charset_normalizer_version', 'check_compatibility', 'codes', 'compat', 'cookies', 'delete', 'exceptions', 'get', 'head', 'hooks', 'logging', 'models', 'options', 'packages', 'patch', 'post', 'put', 'request', 'session', 'sessions', 'ssl', 'status_codes', 'structures', 'urllib3', 'utils', 'warnings']
    ScrapingAntClient:
        ['__class__', '__delattr__', '__dict__', '__dir__', '__doc__', '__eq__', '__format__', '__ge__', '__getattribute__', '__getstate__', '__gt__', '__hash__', '__init__', '__init_subclass__', '__le__', '__lt__', '__module__', '__ne__', '__new__', '__reduce__', '__reduce_ex__', '__repr__', '__setattr__', '__sizeof__', '__str__', '__subclasshook__', '__weakref__', 'content', 'cookies', 'status_code', 'text']
    """

    def general_request(self, url, kwargs: dict[str, Any] = {}):
        response = requests.get(url, **kwargs)
        # Make the response match ScrapingAnt's response structure
        return MockResponse(content=response.text)


def get_content_with_requests(url: str) -> tuple[str, BeautifulSoup]:
    """Get content using requests library.

    Args:
        url (str): The URL to get content from.

    Returns:
        tuple[str, BeautifulSoup]: The content and the BeautifulSoup object.
    """
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
