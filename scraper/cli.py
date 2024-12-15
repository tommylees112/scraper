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
        click.option(
            "--tag", default="nav", help="HTML tag to use for extracting the links"
        ),
        click.option("--class-name", help="Exact class name to match"),
        click.option(
            "-c",
            "--class-contains",
            help="String that should be contained in the class name",
        ),
        click.option("--id", help="ID of the element"),
        click.option(
            "--save-html",
            is_flag=True,
            help="Save HTML content for each scraped page",
        ),
        click.option(
            "--overwrite-html",
            is_flag=True,
            help="Overwrite existing HTML files even if they exist",
        ),
        click.option(
            "--use-scraping-ant",
            is_flag=True,
            help="Use ScrapingAnt for content scraping (requires API key)",
        ),
        click.option(
            "--text-tag", default="div", help="HTML tag to use for text extraction"
        ),
        click.option(
            "--text-class-name", help="Exact class name to match for text extraction"
        ),
        click.option(
            "--text-class-contains",
            help="String that should be contained in the text element's class name",
        ),
        click.option("--text-id", help="ID of the text element"),
        click.option("--text-role", help="Role attribute of the text element"),
    ]

    for option in options:
        command = option(command)

    return command
