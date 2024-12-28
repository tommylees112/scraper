import re
from pathlib import Path
from typing import List, Optional, Pattern, Union

from bs4 import BeautifulSoup
from scrapingant_client import ScrapingAntClient  # type: ignore

from .config import TextConfig
from .content_scrapers import get_content_with_requests, get_content_with_scraping_ant
from .link import Link
from .scraping_page_log import ScrapingPage, append_to_page_log, should_skip_url


def extract_text(soup: BeautifulSoup, config: TextConfig) -> List[str]:
    """
    Extract text from HTML based on the provided configuration.

    Args:
        soup: BeautifulSoup object containing the parsed HTML
        config: TextConfig object with extraction parameters

    Returns:
        List of extracted text strings
    """
    attrs: dict[str, Union[str, Pattern[str]]] = {}

    if config.class_name:
        attrs["class"] = config.class_name
    elif config.class_contains:
        attrs["class"] = re.compile(config.class_contains)

    if config.id:
        attrs["id"] = config.id

    if config.role:
        attrs["role"] = config.role

    elements = soup.find_all(config.tag, attrs=attrs)
    return [element.get_text(strip=True) for element in elements]


def save_content(
    link: Link,
    output_path: Path,
    text_config: TextConfig,
    html_dir: Optional[Path] = None,
    use_scraping_ant: bool = False,
    client: Optional[ScrapingAntClient] = None,
    processed_pages: Optional[List[ScrapingPage]] = None,
    log_path: Optional[Path] = None,
    overwrite: bool = False,
) -> bool:
    """
    Save content from a link to a file.

    Args:
        link: Link object containing URL and metadata
        output_path: Path to save the extracted content
        text_config: Configuration for text extraction
        html_dir: Optional directory to save raw HTML content
        use_scraping_ant: Whether to use ScrapingAnt for scraping
        client: ScrapingAnt API key (required if use_scraping_ant is True)
        processed_pages: List of already processed ScrapingPage entries
        log_path: Path to the logging CSV file
        overwrite: Whether to overwrite existing HTML files

    Returns:
        bool: True if content was processed, False if skipped
    """
    if should_skip_url(link.href, processed_pages, overwrite):
        return False

    if use_scraping_ant:
        if not client:
            raise ValueError("Client is required when using ScrapingAnt")

        assert isinstance(
            client, ScrapingAntClient
        ), f"Client is not a ScrapingAntClient: {type(client)}"
        html_content, soup = get_content_with_scraping_ant(link.href, client)
    else:
        html_content, soup = get_content_with_requests(link.href)

    # Save HTML content if html_dir is provided
    if html_dir:
        html_path = html_dir / f"{link.title}.html"
        if overwrite or not html_path.exists():
            with open(html_path, "w") as f:
                f.write(html_content)

    with open(output_path, "a") as f:
        f.write(f"<TITLE>{link.title}</TITLE>\n\n")

        extracted_texts = extract_text(soup, text_config)
        for text in extracted_texts:
            f.write(f"<CONTENT>{text}</CONTENT>\n")

        f.write("<END_OF_CONTENT></END_OF_CONTENT>\n\n")

    # Log successful scraping
    if log_path is not None and processed_pages is not None:
        page_entry = ScrapingPage.create(
            url=link.href,
            html_path=str(html_dir / f"{link.title}.html") if html_dir else None,
            title=link.title,
        )
        append_to_page_log(log_path, page_entry)
        processed_pages.append(page_entry)

    return True
