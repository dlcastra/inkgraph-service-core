from docx import Document
from docx.oxml.ns import qn

from src.app.docs.processors.base.abstraction import ParagraphExtractor
from src.app.docs.processors.base.constants import HEADING_ID_RE, LEVEL_TO_HEADING, HEADING_NAME_RE
from src.core.typing.docs.pages import DocParagraph, ParagraphType, HeadingLevel


class DocxParagraphExtractor(ParagraphExtractor):
    """
    Extracts paragraphs from a python-docx Document.

    Detects headings via style name first, then falls back to the
    outline-level attribute in the underlying XML (<w:outlineLvl>) for
    documents that use custom style names.
    """

    def extract(self, document: Document) -> list[DocParagraph]:
        result: list[DocParagraph] = []

        for idx, para in enumerate(document.paragraphs):
            style_name = para.style.name if para.style else "Normal"
            heading_level = self._resolve_heading_level(para=para)

            if heading_level is not None:
                para_type = ParagraphType.HEADING
            elif not para.text.strip():
                para_type = ParagraphType.EMPTY
            else:
                para_type = ParagraphType.BODY

            result.append(
                DocParagraph(
                    index=idx,
                    text=para.text,
                    style_name=style_name,
                    paragraph_type=para_type,
                    heading_level=heading_level,
                )
            )

        return result

    def _resolve_heading_level(self, para) -> HeadingLevel | None:
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
    def _get_level_to_heading(level: int) -> HeadingLevel | None:
        try:
            return HeadingLevel(f"Heading {level}")
        except ValueError:
            return None

    @staticmethod
    def _get_outline_level_from_xml(para) -> int | None:
        pPr = para._p.find(qn("w:pPr"))
        if pPr is None:
            return None
        outlineLvl = pPr.find(qn("w:outlineLvl"))
        if outlineLvl is None:
            return None
        val = outlineLvl.get(qn("w:val"))
        return int(val) if val is not None else None
