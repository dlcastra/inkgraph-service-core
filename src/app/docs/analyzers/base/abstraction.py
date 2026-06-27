from __future__ import annotations

from abc import ABC, abstractmethod

from src.core.typing.docs.pages import DocParagraph, HeadingLevel


class FontRankingStrategy(ABC):
    """Defines the base size and heading levels for a set of paragraphs based on their font sizes."""

    @abstractmethod
    def resolve(self, paragraphs: list[DocParagraph]) -> tuple[float | None, dict[float, HeadingLevel]]:
        """:return: (base_font_size, {font_size -> HeadingLevel})"""
        pass


class DocumentContentAnalyzer(ABC):
    """
    Takes a DocParagraph list (the result of the extractor),
    reclassifies `paragraph_type` and `heading_level` based on font analysis,
    and returns a new list.
    """

    @abstractmethod
    def analyze(self, paragraphs: list[DocParagraph]) -> list[DocParagraph]:
        """
        :param paragraphs: Result of  DocxParagraphExtractor.extract()
        :return: Re-marked paragraphs (new objects; the original is not modified)
        """
        pass
