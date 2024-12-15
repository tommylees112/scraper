from dataclasses import dataclass
from typing import Optional


@dataclass
class LinkConfig:
    """Configuration for link extraction"""

    tag: str = "nav"
    class_name: Optional[str] = None
    class_contains: Optional[str] = None
    id: Optional[str] = None


@dataclass
class TextConfig:
    """Configuration for text extraction"""

    tag: str = "div"
    class_name: Optional[str] = None
    class_contains: Optional[str] = None
    id: Optional[str] = None
    role: Optional[str] = None
