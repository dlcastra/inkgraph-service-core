import io
from pathlib import Path

from src.core.typing.docs.meta import DocSource


def normalize_doc_source(source: DocSource) -> io.BytesIO:
    """
    Normalize a Document source into a BytesIO stream. Accepts str, Path, bytes, or io.BytesIO.

    :param source: Document source to normalize into a BytesIO stream.
    :return: io.BytesIO stream
    :raise: TypeError if source is not one of the accepted types.
    """

    if isinstance(source, io.BytesIO):
        source.seek(0)
        return source

    if isinstance(source, bytes):
        return io.BytesIO(source)

    if isinstance(source, (str, Path)):
        path = Path(source)

        if not path.exists():
            raise FileNotFoundError(f"Document not found: {path}")
        if path.suffix.lower() != ".docx":
            raise ValueError(f"Expected a .docx file, got: {path.suffix!r}")

        return io.BytesIO(path.read_bytes())

    raise TypeError(
        f"Unsupported document source type: {type(source).__name__!r}. " "Expected str, Path, bytes, or io.BytesIO."
    )
