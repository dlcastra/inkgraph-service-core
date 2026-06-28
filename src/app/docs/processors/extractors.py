import asyncio
from typing import Optional

from docx import Document
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from loguru import logger as _base_logger

from src.app.docs.processors.base.abstraction import ParagraphExtractor, AsyncParagraphExtractor
from src.app.docs.processors.base.constants import HEADING_ID_RE, LEVEL_TO_HEADING, HEADING_NAME_RE
from src.core.typing.docs.pages import DocParagraph, ParagraphType, HeadingLevel
from src.core.typing.protocols.logging import LoggerProtocol


class DocxParagraphExtractor(ParagraphExtractor):
    """
    Extracts paragraphs from a python-docx Document.

    Detects headings via style name first, then falls back to the
    outline-level attribute in the underlying XML (<w:outlineLvl>) for
    documents that use custom style names.
    """

    def __init__(self, logger: Optional[LoggerProtocol] = None) -> None:
        self.__logger = logger or _base_logger

    def extract(self, document: Document) -> list[DocParagraph]:
        result: list[DocParagraph] = []

        self.__logger.info(f"Start parsing document paragraphs, paragraphs count: {len(document.paragraphs)}")
        for idx, para in enumerate(document.paragraphs):
            style_name = para.style.name if para.style else "Normal"
            heading_level = self._resolve_heading_level(para=para)

            if heading_level is not None:
                para_type = ParagraphType.HEADING
            elif not para.text.strip():
                para_type = ParagraphType.EMPTY
            else:
                para_type = ParagraphType.BODY

            font_size = self._resolve_font_size(para, document)
            result.append(
                DocParagraph(
                    index=idx,
                    text=para.text,
                    style_name=style_name,
                    paragraph_type=para_type,
                    heading_level=heading_level,
                    font_size=font_size,
                )
            )

        self.__logger.info(f"Finished parsing document paragraphs, extracted paragraphs count: {len(result)}")
        return result

    def _resolve_font_size(self, para: Paragraph, document: Document) -> float | None:
        """
        Check paragraph runs for font size, then check paragraph style, then check Normal style.
        This method is used to analyze a paragraph in order to determine the font size.

        :param para: Instance of docx.Document paragraph.
        :param document: Instance of docx.Document.
        :return: Font size in float or None if no font size is found.
        """

        for run in para.runs:
            if run.font.size is not None:
                return run.font.size.pt

        style = para.style
        while style is not None:
            if style.font.size is not None:
                return style.font.size.pt
            style = style.base_style

        try:
            normal_style = document.styles["Normal"]
            if normal_style.font.size is not None:
                return normal_style.font.size.pt
        except KeyError:
            pass

        return None

    def _resolve_heading_level(self, para: Paragraph) -> HeadingLevel | None:
        """
        Check paragraph with regular expression schemas to determine if it is a heading
        and return the corresponding HeadingLevel.

        :param para: Instance of docx.Document paragraph.
        :return: LEVEL_TO_HEADING (ex: Heading 1, Heading 2, etc.) or None if not a heading.
        """

        style = para.style
        if not style:
            return None

        match = HEADING_ID_RE.match(style.style_id or "")
        if match:
            return LEVEL_TO_HEADING.get(int(match.group(1)))

        match = HEADING_NAME_RE.match(style.name or "")
        if match:
            return LEVEL_TO_HEADING.get(int(match.group(1)))

        outline_level = self._get_outline_level_from_xml(para)
        if outline_level is not None:
            return LEVEL_TO_HEADING.get(outline_level + 1)

        return None

    @staticmethod
    def _get_outline_level_from_xml(para: Paragraph) -> int | None:
        """
        Check outline level from the underlying XML of the paragraph.

        :param para: instance of docx.Document paragraph.
        :return: Heading level as an integer or None if not found.
        """

        pPr = para._p.find(qn("w:pPr"))
        if pPr is None:
            return None
        outlineLvl = pPr.find(qn("w:outlineLvl"))
        if outlineLvl is None:
            return None
        val = outlineLvl.get(qn("w:val"))
        return int(val) if val is not None else None


class AsyncDocxParagraphExtractorWrapper(AsyncParagraphExtractor):
    def __init__(self, sync_extractor: Optional[DocxParagraphExtractor] = None) -> None:
        self._sync_extractor = sync_extractor or DocxParagraphExtractor()

    async def extract(self, document: Document) -> list[DocParagraph]:
        return await asyncio.to_thread(self._sync_extractor.extract, document)
