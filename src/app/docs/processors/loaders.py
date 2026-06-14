from pathlib import Path

from docx import Document

from src.app.docs.processors.base.abstraction import DocumentLoader


class DocxLoader(DocumentLoader):
    """Loads a .docx file using python-docx."""

    def load(self, path: Path) -> Document:
        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")

        if path.suffix.lower() != ".docx":
            raise ValueError(f"Expected a .docx file, got: {path.suffix}")

        return Document(str(path))
