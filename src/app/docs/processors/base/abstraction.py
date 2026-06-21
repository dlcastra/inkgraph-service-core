from __future__ import annotations

import io
from abc import ABC, abstractmethod
from typing import Optional

from docx import Document

from src.core.typing.docs.pages import DocParagraph, Chapter


class DocumentLoader(ABC):
    """Knows how to open a raw document from a source."""

    @abstractmethod
    def load(self, source: io.BytesIO) -> Document:
        """Accepts a normalized BytesIO stream produced by normalize_doc_source()."""
        pass


class ParagraphExtractor(ABC):
    """Turns a raw Document into a flat list of DocParagraph models."""

    @abstractmethod
    def extract(self, document: Document) -> list[DocParagraph]:
        pass


class ChapterSplitter(ABC):
    """Groups a flat list of paragraphs into chapters."""

    @abstractmethod
    def split(
        self, paragraphs: list[DocParagraph], chapter_heading_map: Optional[frozenset[str]] = None
    ) -> tuple[list[DocParagraph], list[Chapter]]:
        """Returns (preamble_paragraphs, chapters)."""
        pass


class AsyncDocumentLoader(ABC):
    """Knows how to open a raw document from a source (async)."""

    @abstractmethod
    async def load(self, source: io.BytesIO) -> Document:
        """Accepts a normalized BytesIO stream produced by normalize_doc_source()."""
        pass


class AsyncParagraphExtractor(ABC):
    """Turns a raw Document into a flat list of DocParagraph models."""

    @abstractmethod
    async def extract(self, document: Document) -> list[DocParagraph]:
        pass


class AsyncChapterSplitter(ABC):
    """Groups a flat list of paragraphs into chapters."""

    @abstractmethod
    async def split(
        self, paragraphs: list[DocParagraph], chapter_heading_map: Optional[frozenset[str]] = None
    ) -> tuple[list[DocParagraph], list[Chapter]]:
        """Returns (preamble_paragraphs, chapters)."""
        pass
