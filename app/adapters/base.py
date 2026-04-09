from abc import ABC, abstractmethod

from app.schemas.domain.normalized_record import NormalizedRecordSchema
from app.schemas.domain.raw_record import RawRecord


class BaseAdapter(ABC):
    """Abstract base class for marketplace adapters.

    Each adapter knows how to fetch, parse, and normalize listings
    from a specific source (eBay, Heritage, Goldin, etc.).
    """

    source: str

    @abstractmethod
    async def fetch(self, url: str, **kwargs) -> str:
        """Fetch raw HTML from the source URL."""

    @abstractmethod
    def parse(self, raw_html: str) -> list[RawRecord]:
        """Parse raw HTML into a list of unstructured records."""

    @abstractmethod
    def normalize(self, raw_records: list[RawRecord]) -> list[NormalizedRecordSchema]:
        """Normalize raw records into structured, searchable records."""
