import asyncio
from pathlib import Path

from docx import Document

from src.app.docs.processors.base.abstraction import DocumentLoader, AsyncDocumentLoader


class DocxLoader(DocumentLoader):
    """Loads a .docx file using python-docx."""

    def load(self, path: Path) -> Document:
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")

        if path.suffix.lower() != ".docx":
            raise ValueError(f"Expected a .docx file, got: {path.suffix}")

        return Document(str(path))


class AsyncDocxLoaderWrapper(AsyncDocumentLoader):
    """Loads a .docx file using python-docx."""

    def __init__(self, sync_loader: DocxLoader) -> None:
        self._sync_loader = sync_loader

    async def load(self, path: Path) -> Document:
        return await asyncio.to_thread(self._sync_loader.load, path)
