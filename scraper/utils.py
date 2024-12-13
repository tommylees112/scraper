from pathlib import Path


def create_title_from_url(url: str) -> str:
    path = Path(url)
    parts = [p.replace("-", "_").lower() for p in path.parts]
    meaningful_parts = [p for p in parts if p][-3:]
    return "_".join(meaningful_parts)


def convert_to_absolute_url(href: str) -> str:
    if href.startswith("/"):
        return f"https://www.palantir.com{href}"
    return href
