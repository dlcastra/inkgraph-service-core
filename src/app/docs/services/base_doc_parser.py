from pathlib import Path

from src.app.docs.processors import DocxLoader, DocxParagraphExtractor, HeadingOneChapterSplitter
from src.app.docs.processors.base.abstraction import (
    DocumentLoader,
    ParagraphExtractor,
    ChapterSplitter,
    AsyncDocumentLoader,
    AsyncParagraphExtractor,
    AsyncChapterSplitter,
)
from src.app.docs.processors.extractors import AsyncDocxParagraphExtractorWrapper
from src.app.docs.processors.loaders import AsyncDocxLoaderWrapper
from src.app.docs.processors.splitters import AsyncHeadingOneChapterSplitterWrapper
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


class AsyncBaseDocumentParserService:
    """
    Parses a .docx file into a ParsedDocument asynchronously.
    """

    def __init__(
        self,
        loader: AsyncDocumentLoader,
        extractor: AsyncParagraphExtractor,
        splitter: AsyncChapterSplitter,
    ) -> None:
        self._loader = loader
        self._extractor = extractor
        self._splitter = splitter

    async def parse(self, path: str | Path) -> ParsedDocument:
        path = Path(path)

        raw_doc = await self._loader.load(path)
        paragraphs = await self._extractor.extract(raw_doc)
        preamble, chapters = await self._splitter.split(paragraphs)

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


def build_async_doc_parser() -> AsyncBaseDocumentParserService:
    """Factory that wires up the default async production pipeline."""
    return AsyncBaseDocumentParserService(
        loader=AsyncDocxLoaderWrapper(DocxLoader()),
        extractor=AsyncDocxParagraphExtractorWrapper(DocxParagraphExtractor()),
        splitter=AsyncHeadingOneChapterSplitterWrapper(HeadingOneChapterSplitter()),
    )
