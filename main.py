import os
from pathlib import Path
from typing import Optional

import click
from bs4 import BeautifulSoup
from loguru import logger
from scrapingant_client import ScrapingAntClient  # type: ignore
from tqdm import tqdm

from scraper.cli import create_cli_options, format_options_overview
from scraper.config import LinkConfig, TextConfig
from scraper.content_scraper import save_content
from scraper.content_scrapers import MockClient
from scraper.link_scraper import extract_links
from scraper.scraping_ant_utils import save_scraping_response
from scraper.scraping_page_log import (
    ScrapingPage,
    append_to_page_log,
    load_or_create_page_log,
)
from scraper.utils import create_dir_name_from_netloc, create_title_from_url


@click.command()
@click.argument("url", type=str)
@create_cli_options
def main(
    url: str,
    api_key: str,
    output_dir: Path,
    link_tag: str,
    link_class_name: Optional[str],
    link_class_contains: Optional[str],
    link_id: Optional[str],
    save_html: bool,
    overwrite: bool,
    use_scraping_ant: bool,
    text_tag: str,
    text_class_name: Optional[str],
    text_class_contains: Optional[str],
    text_id: Optional[str],
    text_role: Optional[str],
) -> None:
    """
    Scrape documentation from a given URL.

    URL should be a valid documentation page, e.g.:
    https://moz.com/beginners-guide-to-seo

    The output will be saved to your Downloads folder by default.
    """
    # Log options overview at the start
    # Get all local variables except api_key
    options = {
        k: v or "Not specified" if v is None else v
        for k, v in locals().items()
        if k != "api_key"  # Exclude sensitive information
    }

    logger.info(format_options_overview(**options))

    # 1. SCRAPING ANT TO GET THE BASE PAGE
    # get api key from os.environ if None
    if not api_key:
        api_key = os.environ.get("SCRAPING_ANT_API_KEY")

    # Validate API key if using ScrapingAnt
    if use_scraping_ant and not api_key:
        raise click.UsageError(
            "ScrapingAnt API key is required when using --use-scraping-ant. Set it via --api-key or SCRAPING_ANT_API_KEY environment variable."
        )

    # Setup client for initial page scraping
    if use_scraping_ant:
        client = ScrapingAntClient(token=api_key) if use_scraping_ant else None
    else:
        # set teh client to have a general_request() method that uses requests. Mock this behaviour
        client = MockClient()

    # 2. SETUP THE directory, logging, txt output file
    # Create domain-specific directory inside output_dir
    dir_name = create_dir_name_from_netloc(url)
    domain_dir = output_dir / dir_name
    try:
        domain_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise click.ClickException(
            f"Permission denied: Cannot create directory {domain_dir}"
        )

    # Initialize log file
    log_path = domain_dir / "logs.csv"
    processed_pages = load_or_create_page_log(log_path)

    # Log if we're reprocessing an already processed URL
    if any(page.url == url for page in processed_pages):
        logger.info("Reprocessing previously scraped URL due to --overwrite flag")

    # Log the base URL scraping
    base_html_title = create_title_from_url(url)
    output_path = domain_dir / f"{base_html_title}.txt"
    logger.info(f"Output will be saved to: {output_path}")

    # Initialize output file - write to txt file
    try:
        with open(output_path, "w") as f:
            f.write("SCRAPED CONTENT\n\n")
    except PermissionError:
        raise click.ClickException(f"Permission denied: Cannot write to {output_path}")

    # Setup the html directory
    html_dir = domain_dir / "html" if save_html else None
    if html_dir:
        html_dir.mkdir(parents=True, exist_ok=True)

    # 3. GET LINKS FROM BASE PAGE
    # Get links using ScrapingAnt API or requests
    if not client:
        if use_scraping_ant:
            raise click.ClickException("ScrapingAnt client not initialized")
        else:
            # html_content, soup = get_content_with_requests(url)
            response = client.general_request(url)
    else:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"
        }
        response = client.general_request(url, kwargs=dict(headers=headers))

    # Save response for debugging
    if html_dir:
        debug_path = save_scraping_response(
            response=response,
            title="BASE_" + base_html_title,
            output_dir=html_dir,
        )
    else:
        debug_path = None

    # Log the base URL scraping
    base_page = ScrapingPage.create(
        url=url,
        html_path=str(debug_path) if html_dir else None,
        title=base_html_title,
    )
    append_to_page_log(log_path, base_page)
    processed_pages.append(base_page)

    # parse it as a BeautifulSoup object
    soup = BeautifulSoup(response.content, "html.parser")

    config = LinkConfig(
        tag=link_tag,
        class_name=link_class_name,
        class_contains=link_class_contains,
        id=link_id,
    )

    text_config = TextConfig(
        tag=text_tag,
        class_name=text_class_name,
        class_contains=text_class_contains,
        id=text_id,
        role=text_role,
    )

    # extract links from the base page
    links = extract_links(soup, url)

    if not links:
        raise click.ClickException(
            f"No navigation links found on the page.\nCheck: {debug_path}"
        )

    # 4. SAVE CONTENT FROM EACH LINK
    for link in tqdm(links, desc="Extracting content"):
        try:
            save_content(
                link,
                output_path,
                text_config,
                html_dir,
                use_scraping_ant=use_scraping_ant,
                client=client if use_scraping_ant else None,
                processed_pages=processed_pages,
                log_path=log_path,
                overwrite=overwrite,
            )
        except Exception as e:
            # Log failed scraping
            logger.error(f"Failed to scrape {link.href}: {str(e)}")
            page_entry = ScrapingPage.create(
                url=link.href,
                html_path=None,
                title=link.title,
                status="failed",
            )
            append_to_page_log(log_path, page_entry)
            processed_pages.append(page_entry)


if __name__ == "__main__":
    main()
