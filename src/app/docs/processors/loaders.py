import io
import asyncio

from docx import Document

from src.app.docs.processors.base.abstraction import DocumentLoader, AsyncDocumentLoader


class DocxLoader(DocumentLoader):
    """Loads a .docx document from a normalized BytesIO stream."""

    def load(self, source: io.BytesIO) -> Document:
        return Document(source)


class AsyncDocxLoaderWrapper(AsyncDocumentLoader):
    """Async wrapper over DocxLoader — offloads blocking I/O to a thread."""

    def __init__(self, sync_loader: DocxLoader) -> None:
        self._sync_loader = sync_loader

    async def load(self, source: io.BytesIO) -> Document:
        return await asyncio.to_thread(self._sync_loader.load, source)
