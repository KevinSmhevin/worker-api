from bs4 import BeautifulSoup

from app.adapters.ebay import selectors
from app.core.constants import Source
from app.core.exceptions import ParsingError
from app.core.logging import get_logger
from app.schemas.domain.raw_record import RawRecord

logger = get_logger(__name__)


def parse_sold_listings(raw_html: str) -> list[RawRecord]:
    """Parse eBay sold listings HTML into a list of RawRecords."""
    try:
        soup = BeautifulSoup(raw_html, "lxml")
    except Exception as exc:
        raise ParsingError("Failed to parse HTML with lxml") from exc

    items = soup.select(selectors.LISTING_ITEM)
    if not items:
        logger.warning("ebay_no_items_found")
        return []

    records: list[RawRecord] = []

    for item in items:
        try:
            record = _parse_single_item(item)
            if record:
                records.append(record)
        except Exception:
            logger.warning("ebay_item_parse_error", exc_info=True)
            continue

    logger.info("ebay_parsed_items", count=len(records))
    return records


def _parse_single_item(item) -> RawRecord | None:
    title_el = item.select_one(selectors.LISTING_TITLE)
    if not title_el:
        return None

    title = title_el.get_text(strip=True)
    if title.lower() in ("shop on ebay", ""):
        return None

    price = None
    price_el = item.select_one(selectors.LISTING_PRICE)
    if price_el:
        price = price_el.get_text(strip=True)

    sold_date = None
    date_el = item.select_one(selectors.LISTING_SOLD_DATE)
    if date_el:
        sold_date = date_el.get_text(strip=True)

    listing_url = None
    link_el = item.select_one(selectors.LISTING_LINK)
    if link_el:
        listing_url = link_el.get("href")

    image_url = None
    img_el = item.select_one(selectors.LISTING_IMAGE)
    if img_el:
        image_url = img_el.get("src")

    return RawRecord(
        title=title,
        price=price,
        sold_date=sold_date,
        listing_url=listing_url,
        image_url=image_url,
        source=Source.EBAY,
    )
