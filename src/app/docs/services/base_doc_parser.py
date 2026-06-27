from pathlib import Path

from src.app.docs.processors import (
    AsyncDocxLoaderWrapper,
    AsyncDocxParagraphExtractorWrapper,
    AsyncHeadingOneChapterSplitterWrapper,
    DocxLoader,
    DocxParagraphExtractor,
    HeadingOneChapterSplitter,
)
from src.app.docs.processors.base.abstraction import (
    AsyncDocumentLoader,
    AsyncParagraphExtractor,
    AsyncChapterSplitter,
    DocumentLoader,
    ParagraphExtractor,
    ChapterSplitter,
)
from src.app.docs.utils import normalize_doc_source
from src.core.typing.docs.meta import DocSource
from src.core.typing.docs.pages import ParsedDocument


class BaseDocumentParserService:
    """
    Parses a document into a ParsedDocument.

    Accepts str, Path, bytes, or io.BytesIO as the document source —
    normalization to BytesIO is handled transparently before loading.
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

    def parse(self, source: DocSource) -> ParsedDocument:
        stream = normalize_doc_source(source)
        source_path = str(source) if isinstance(source, (str, Path)) else ""

        raw_doc = self._loader.load(stream)
        paragraphs = self._extractor.extract(raw_doc)
        preamble, chapters = self._splitter.split(paragraphs)

        return ParsedDocument(
            source_path=source_path,
            preamble_paragraphs=preamble,
            chapters=chapters,
        )


class AsyncBaseDocumentParserService:
    """
    Parses a document into a ParsedDocument asynchronously.

    Accepts str, Path, bytes, or io.BytesIO as the document source.
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

    async def parse(self, source: DocSource) -> ParsedDocument:
        stream = normalize_doc_source(source)
        source_path = str(source) if isinstance(source, (str, Path)) else ""

        raw_doc = await self._loader.load(stream)
        paragraphs = await self._extractor.extract(raw_doc)
        preamble, chapters = await self._splitter.split(paragraphs)

        return ParsedDocument(
            source_path=source_path,
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
        loader=AsyncDocxLoaderWrapper(),
        extractor=AsyncDocxParagraphExtractorWrapper(),
        splitter=AsyncHeadingOneChapterSplitterWrapper(),
    )
