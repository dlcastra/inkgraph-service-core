from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class HeadingLevel(str, Enum):
    H1 = "Heading 1"
    H2 = "Heading 2"
    H3 = "Heading 3"


class ParagraphType(str, Enum):
    HEADING = "heading"
    BODY = "body"
    EMPTY = "empty"


class DocParagraph(BaseModel):
    """Single paragraph extracted from a .docx file."""

    index: int = Field(description="Position in the original document")
    text: str
    style_name: str
    paragraph_type: ParagraphType
    heading_level: HeadingLevel | None = None

    @property
    def is_heading(self) -> bool:
        return self.paragraph_type == ParagraphType.HEADING


class Chapter(BaseModel):
    """A chapter identified by its heading and the paragraphs that follow it."""

    number: int = Field(description="1-based chapter index in the document")
    title: str
    heading_paragraph: DocParagraph
    body_paragraphs: list[DocParagraph] = Field(default_factory=list)

    @property
    def is_odd(self) -> bool:
        return self.number % 2 != 0

    @property
    def full_text(self) -> str:
        lines = [self.title] + [p.text for p in self.body_paragraphs if p.text.strip()]
        return "\n\n".join(lines)

    @property
    def word_count(self) -> int:
        return len(self.full_text.split())


class ParsedDocument(BaseModel):
    """Full parsed representation of a .docx file."""

    source_path: str
    chapters: list[Chapter] = Field(default_factory=list)
    preamble_paragraphs: list[DocParagraph] = Field(
        default_factory=list,
        description="Paragraphs before the first heading",
    )

    @property
    def chapter_count(self) -> int:
        return len(self.chapters)
