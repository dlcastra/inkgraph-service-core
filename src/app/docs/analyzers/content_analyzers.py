from collections import Counter
from typing import Optional

from loguru import logger as _base_logger

from src.app.docs.analyzers.base.abstraction import FontRankingStrategy, DocumentContentAnalyzer
from src.core.typing.docs.pages import HeadingLevel, DocParagraph, ParagraphType
from src.core.typing.protocols.logging import LoggerProtocol


class FrequencyFontRankingStrategy(FontRankingStrategy):
    """Determines the base font size and heading hierarchy from paragraph font sizes.

    Strategy:
        - Base size: the most frequent size among the smallest tercile of
        sizes (body text dominates by count and is the smallest).

        - Heading sizes: sizes strictly above base that appear more than once AND
        whose frequency is at least `min_heading_share` of the
        most-common heading size.  Singletons (title page, cover
        lines, captions) are demoted to a separate "rare" bucket
        and never enter the structural heading map.

        - From H1 to H3: surviving heading sizes sorted largest-first.

    Rationale for the singleton filter
    """

    _HEADING_LEVELS = [HeadingLevel.H1, HeadingLevel.H2, HeadingLevel.H3]
    _MIN_HEADING_FREQ: int = 2

    def resolve(self, paragraphs: list[DocParagraph]) -> tuple[float | None, dict[float, HeadingLevel]]:
        sizes = [p.font_size for p in paragraphs if p.font_size is not None and p.paragraph_type != ParagraphType.EMPTY]

        if not sizes:
            return None, {}

        counter = Counter(sizes)
        unique_sizes = sorted(counter)
        tercile_cutoff = max(1, len(unique_sizes) // 3)
        smallest_tercile = unique_sizes[:tercile_cutoff]
        base_size: float = max(smallest_tercile, key=lambda s: counter[s])

        above_base = {s for s in unique_sizes if s > base_size}
        rare_sizes = {s for s in above_base if counter[s] < self._MIN_HEADING_FREQ}
        heading_sizes = sorted(above_base - rare_sizes, reverse=True)

        if rare_sizes:
            _base_logger.debug(
                f"Skipped rare font sizes (likely cover/title page): " f"{sorted(rare_sizes, reverse=True)}"
            )

        heading_map: dict[float, HeadingLevel] = {
            size: level for size, level in zip(heading_sizes, self._HEADING_LEVELS)
        }

        return base_size, heading_map


class FontSizeDocumentAnalyzer(DocumentContentAnalyzer):
    def __init__(
        self,
        strategy: Optional[FontRankingStrategy] = None,
        logger: Optional[LoggerProtocol] = None,
    ) -> None:
        self._strategy = strategy or FrequencyFontRankingStrategy()
        self._logger = logger or _base_logger

    def analyze(self, paragraphs: list[DocParagraph]) -> list[DocParagraph]:
        """
        Analyzes paragraphs based on font size and heading hierarchy.
        Remarks paragraphs as HEADING or BODY based on the resolved font sizes.

        :param paragraphs: List of DocParagraphs to analyze
        :return: Remarked list of DocParagraphs
        """

        self._logger.info(f"Starting font-size analysis, paragraphs count: {len(paragraphs)}")

        base_size, heading_map = self._strategy.resolve(paragraphs)

        self._logger.info(f"Resolved base font size: {base_size}pt, heading map: {heading_map}")

        result = [self._remark(para, heading_map) for para in paragraphs]
        self._logger.info(f"Font-size analysis complete, remarked paragraphs: {len(result)}")
        return result

    def _remark(
        self,
        para: DocParagraph,
        heading_map: dict[float, HeadingLevel],
    ) -> DocParagraph:
        if para.paragraph_type == ParagraphType.EMPTY:
            return para

        if para.font_size is not None and para.font_size in heading_map:
            resolved_level = heading_map[para.font_size]
            return para.model_copy(
                update={
                    "paragraph_type": ParagraphType.HEADING,
                    "heading_level": resolved_level,
                }
            )

        if para.paragraph_type == ParagraphType.HEADING:
            return para

        return para.model_copy(update={"paragraph_type": ParagraphType.BODY, "heading_level": None})
