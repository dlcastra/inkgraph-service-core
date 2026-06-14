from typing import Optional

from src.app.docs.processors.base.abstraction import ChapterSplitter
from src.core.typing.docs.pages import DocParagraph, Chapter, ParagraphType


class HeadingOneChapterSplitter(ChapterSplitter):
    """
    Splits paragraphs into chapters whenever a Heading-1 paragraph is met.
    Everything before the first heading goes into the preamble.
    """

    def split(
        self,
        paragraphs: list[DocParagraph],
        chapter_heading_map: Optional[frozenset[str]] = None,
    ) -> tuple[list[DocParagraph], list[Chapter]]:
        preamble: list[DocParagraph] = []
        chapters: list[Chapter] = []
        current_chapter: Chapter | None = None

        for para in paragraphs:
            if self._is_chapter_boundary(para, chapter_heading_map):
                if current_chapter is not None:
                    chapters.append(current_chapter)
                current_chapter = Chapter(
                    number=len(chapters) + 1,
                    title=para.text.strip() or f"Chapter {len(chapters) + 1}",
                    heading_paragraph=para,
                )
            elif current_chapter is None:
                preamble.append(para)
            else:
                current_chapter.body_paragraphs.append(para)

        if current_chapter is not None:
            chapters.append(current_chapter)

        return preamble, chapters

    @staticmethod
    def _is_chapter_boundary(para: DocParagraph, chapter_heading_map: Optional[frozenset[str]]) -> bool:
        if chapter_heading_map is not None:
            return para.paragraph_type == ParagraphType.HEADING and para.style_name in chapter_heading_map
        return para.paragraph_type == ParagraphType.HEADING
