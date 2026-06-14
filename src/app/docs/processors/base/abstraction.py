from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional

from docx import Document

from src.core.typing.docs.pages import DocParagraph, Chapter, HeadingLevel


class DocumentLoader(ABC):
    """Knows how to open a raw document from a path."""

    @abstractmethod
    def load(self, path: Path) -> Document: ...


class ParagraphExtractor(ABC):
    """Turns a raw Document into a flat list of DocParagraph models."""

    @abstractmethod
    def extract(self, document: Document) -> list[DocParagraph]: ...


class ChapterSplitter(ABC):
    """Groups a flat list of paragraphs into chapters."""

    @abstractmethod
    def split(
        self, paragraphs: list[DocParagraph], chapter_heading_map: Optional[frozenset[str]] = None
    ) -> tuple[list[DocParagraph], list[Chapter]]:
        """Returns (preamble_paragraphs, chapters)."""
        ...
