from pathlib import Path

from src.app.docs.processors import DocxLoader, DocxParagraphExtractor, HeadingOneChapterSplitter
from src.app.docs.processors.base.abstraction import DocumentLoader, ParagraphExtractor, ChapterSplitter
from src.core.typing.docs.pages import ParsedDocument


class BaseDocumentParserService:
    """
    Parses a .docx file into a ParsedDocument.

    Dependencies are injected so each piece can be swapped independently.
    """

    def __init__(
        self,
        loader: DocumentLoader,
        extractor: ParagraphExtractor,
        splitter: ChapterSplitter,
    ) -> None:
        self._loader = loader
        self._extractor = extractor
        self._splitter = splitter

    def parse(self, path: str | Path) -> ParsedDocument:
        path = Path(path)
        raw_doc = self._loader.load(path)
        paragraphs = self._extractor.extract(raw_doc)
        preamble, chapters = self._splitter.split(paragraphs)

        return ParsedDocument(
            source_path=str(path),
            preamble_paragraphs=preamble,
            chapters=chapters,
        )


def build_base_doc_parser() -> BaseDocumentParserService:
    """Factory that wires up the default production pipeline."""
    return BaseDocumentParserService(
        loader=DocxLoader(),
        extractor=DocxParagraphExtractor(),
        splitter=HeadingOneChapterSplitter(),
    )
