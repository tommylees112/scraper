import os
from pathlib import Path

import click
from bs4 import BeautifulSoup
from loguru import logger
from scrapingant_client import ScrapingAntClient  # type: ignore
from tqdm import tqdm

from scraper.content_scraper import save_content
from scraper.nav_scraper import extract_navigation_links
from scraper.scraping_ant_utils import save_scraping_response
from scraper.utils import create_dir_name_from_netloc, create_title_from_url


def get_default_downloads_dir() -> Path:
    """Get the default downloads directory for the current OS."""
    if os.name == "nt":  # Windows
        return Path.home() / "Downloads"
    else:  # macOS and Linux
        return Path.home() / "Downloads"


@click.command()
@click.argument("url", type=str)
@click.option(
    "--api-key",
    envvar="SCRAPING_ANT_API_KEY",
    help="ScrapingAnt API key. Can also be set via SCRAPING_ANT_API_KEY environment variable.",
)
@click.option(
    "--output-dir",
    type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
    default=get_default_downloads_dir(),
    show_default="Downloads folder",
    help="Directory to save the output file.",
)
def main(url: str, api_key: str, output_dir: Path):
    """
    Scrape documentation from a given URL.

    URL should be a valid documentation page, e.g.:
    https://www.palantir.com/docs/foundry/ontology/overview

    The output will be saved to your Downloads folder by default.
    """
    # Validate API key
    if not api_key:
        raise click.UsageError(
            "ScrapingAnt API key is required. Set it via --api-key or SCRAPING_ANT_API_KEY environment variable."
        )

    # Setup client
    client = ScrapingAntClient(token=api_key)

    # Create domain-specific directory inside output_dir
    dir_name = create_dir_name_from_netloc(url)
    domain_dir = output_dir / dir_name
    try:
        domain_dir.mkdir(parents=True, exist_ok=True)
    except PermissionError:
        raise click.ClickException(
            f"Permission denied: Cannot create directory {domain_dir}"
        )

    # Update output path to use domain directory
    base_html_title = create_title_from_url(url)
    output_path = domain_dir / f"{base_html_title}.txt"
    logger.info(f"Output will be saved to: {output_path}")

    # Initialize output file
    try:
        with open(output_path, "w") as f:
            f.write("PALANTIR API DOCUMENTATION\n\n")
    except PermissionError:
        raise click.ClickException(f"Permission denied: Cannot write to {output_path}")

    # try:
    # Get links using ScrapingAnt API
    response = client.general_request(url)

    # Save response for debugging
    debug_path = save_scraping_response(
        response=response,
        title=base_html_title,
        output_dir=domain_dir,
    )

    # parse it as a BeautifulSoup object
    soup = BeautifulSoup(response.content, "html.parser")

    # extract navigation links from the <nav> bar
    links = extract_navigation_links(soup, url)

    if not links:
        raise click.ClickException(
            f"No navigation links found on the page.\nCheck: {debug_path}"
        )

    # Save content
    for link in tqdm(links, desc="Extracting content"):
        save_content(link, output_path)

    logger.success("Content extracted successfully.")
    # except Exception as e:
    #     raise click.ClickException(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
