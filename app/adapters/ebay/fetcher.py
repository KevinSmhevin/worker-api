from app.adapters.base import BaseAdapter
from app.adapters.ebay.constants import DEFAULT_SOLD_PARAMS, EBAY_SOLD_SEARCH_URL
from app.adapters.ebay.normalizer import normalize_records
from app.adapters.ebay.parser import parse_sold_listings
from app.core.constants import Source
from app.schemas.domain.normalized_record import NormalizedRecordSchema
from app.schemas.domain.raw_record import RawRecord
from app.services.requests_service import fetch_url


class EbayAdapter(BaseAdapter):
    source = Source.EBAY

    async def fetch(self, url: str, **kwargs) -> str:
        seller = kwargs.get("seller")
        page = kwargs.get("page", 1)

        params = {**DEFAULT_SOLD_PARAMS}

        if seller:
            params["_ssn"] = seller

        if page > 1:
            params["_pgn"] = str(page)

        if url == EBAY_SOLD_SEARCH_URL or "sch/i.html" in url:
            return await fetch_url(url, params=params)

        return await fetch_url(url)

    def parse(self, raw_html: str) -> list[RawRecord]:
        return parse_sold_listings(raw_html)

    def normalize(self, raw_records: list[RawRecord]) -> list[NormalizedRecordSchema]:
        return normalize_records(raw_records)
