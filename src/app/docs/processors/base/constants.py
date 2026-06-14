import re

from src.core.typing.docs.pages import HeadingLevel

HEADING_ID_RE = re.compile(r"^Heading(\d+)$")
HEADING_NAME_RE = re.compile(r"^[Hh]eading\s+(\d+)$")

LEVEL_TO_HEADING: dict[int, HeadingLevel] = {
    1: HeadingLevel.H1,
    2: HeadingLevel.H2,
    3: HeadingLevel.H3,
}
