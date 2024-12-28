from datetime import datetime
from pathlib import Path
from typing import Union

import requests
from loguru import logger
from scrapingant_client.response import Response  # type: ignore


def save_scraping_response(
    response: Union[Response, requests.Response], title: str, output_dir: Path
) -> Path:
    """
    Save ScrapingAnt response to a file for debugging purposes.

    Args:
        response: The response from ScrapingAnt
        title: Title used for filename
        output_dir: Directory to save debug files

    Returns:
        Path: The path to the saved debug file

    Raises:
        IOError: If there's an error writing the debug file
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{title}_{timestamp}.html"
    output_path = output_dir / filename

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_path, "w") as f:
            f.write(response.content)

        logger.debug(f"ScrapingAnt response saved to: {output_path}")
        return output_path

    except IOError as e:
        logger.error(f"Failed to save debug file: {e}")
        raise
