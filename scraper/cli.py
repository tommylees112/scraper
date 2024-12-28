# scraper/cli.py
from pathlib import Path

import click

from scraper.utils import get_default_downloads_dir


def format_options_overview(**kwargs) -> str:
    """Format all options into a single string overview."""
    options = ["\nRunning scraper with options:", "---------------------------"]
    options.extend(f"{k:15} {v}" for k, v in kwargs.items())
    options.append("---------------------------")
    return "\n".join(options)


def create_cli_options(command: click.Command) -> click.Command:
    """Add CLI options to the command."""
    options = [
        click.option(
            "--api-key",
            envvar="SCRAPING_ANT_API_KEY",
            help="ScrapingAnt API key. Can also be set via SCRAPING_ANT_API_KEY environment variable.",
        ),
        click.option(
            "--output-dir",
            type=click.Path(file_okay=False, dir_okay=True, path_type=Path),
            default=get_default_downloads_dir(),
            show_default="Downloads folder",
            help="Directory to save the output file.",
        ),
        # Link extraction options (for finding navigation links on the base page)
        click.option(
            "--link-tag",
            default="nav",
            help="HTML tag to use for finding navigation links on the base page (e.g., 'nav' for navigation menus)",
        ),
        click.option(
            "--link-class-name",
            help="Exact class name to match when finding navigation links (e.g., 'main-nav' or 'sidebar-menu')",
        ),
        click.option(
            "-c",
            "--link-class-contains",
            help="String that should be contained in the class name when finding navigation links",
        ),
        click.option(
            "--link-id",
            help="ID of the element containing navigation links (e.g., 'main-navigation')",
        ),
        click.option(
            "--save-html",
            is_flag=True,
            help="Save HTML content for each scraped page",
        ),
        click.option(
            "--overwrite",
            is_flag=True,
            help="Overwrite existing HTML files even if they exist",
        ),
        click.option(
            "--use-scraping-ant",
            is_flag=True,
            help="Use ScrapingAnt for content scraping (requires API key)",
        ),
        # Text extraction options (for extracting content from linked pages)
        click.option(
            "--text-tag",
            default="div",
            help="HTML tag to use for extracting text content from linked pages (e.g., 'article' or 'main')",
        ),
        click.option(
            "--text-class-name",
            help="Exact class name to match when extracting text content (e.g., 'content' or 'article-body')",
        ),
        click.option(
            "--text-class-contains",
            help="String that should be contained in the class name when extracting text content",
        ),
        click.option(
            "--text-id",
            help="ID of the element containing the main text content (e.g., 'main-content')",
        ),
        click.option(
            "--text-role",
            help="ARIA role attribute of the text content element (e.g., 'main' or 'article')",
        ),
    ]

    for option in options:
        command = option(command)

    return command
