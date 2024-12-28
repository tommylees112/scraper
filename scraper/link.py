from dataclasses import dataclass


@dataclass(frozen=True)
class Link:
    title: str
    href: str
    text: str
    domain: str
