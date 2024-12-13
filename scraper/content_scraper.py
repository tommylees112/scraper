import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup

from .link import Link


def save_content(link: Link, output_path: Path) -> None:
    response = requests.get(link.href)
    soup = BeautifulSoup(response.content, "html.parser")

    with open(output_path, "a") as f:
        f.write(f"<TITLE>{link.title}</TITLE>\n\n")

        pattern = re.compile(r"markdownDoc")
        for div in soup.find_all("div", class_=pattern):
            text = div.get_text(strip=True)
            f.write(f"<CONTENT>{text}</CONTENT>\n")

        f.write("<END_OF_CONTENT></END_OF_CONTENT>\n\n")
