import re
from datetime import datetime

from app.core.constants import Source
from app.core.logging import get_logger
from app.schemas.domain.normalized_record import NormalizedRecordSchema
from app.schemas.domain.raw_record import RawRecord
from app.services.dedupe_service import compute_normalized_record_hash

logger = get_logger(__name__)

GRADING_COMPANIES = {
    "PSA": r"\bPSA\b",
    "BGS": r"\bBGS\b",
    "CGC": r"\bCGC\b",
    "SGC": r"\bSGC\b",
    "ACE": r"\bACE\b",
}

GRADE_PATTERN = re.compile(
    r"\b(?:PSA|BGS|CGC|SGC|ACE)\s*(\d+(?:\.\d+)?)\b", re.IGNORECASE
)

CARD_NUMBER_PATTERN = re.compile(r"\b(\d{1,4}\s*/\s*\d{1,4})\b")

PRICE_PATTERN = re.compile(r"\$?([\d,]+\.?\d*)")


def normalize_records(raw_records: list[RawRecord]) -> list[NormalizedRecordSchema]:
    results: list[NormalizedRecordSchema] = []
    for raw in raw_records:
        try:
            normalized = normalize_single(raw)
            if normalized:
                results.append(normalized)
        except Exception:
            logger.warning("ebay_normalize_error", title=raw.title, exc_info=True)
            continue
    logger.info("ebay_normalized", count=len(results))
    return results


def normalize_single(raw: RawRecord) -> NormalizedRecordSchema | None:
    title = raw.title

    grading_company = _extract_grading_company(title)
    grade = _extract_grade(title)
    card_number = _extract_card_number(title)
    price = _parse_price(raw.price)
    sold_date = _parse_sold_date(raw.sold_date)

    card_name = _extract_card_name(title, grading_company, grade, card_number)

    record = NormalizedRecordSchema(
        card_name=card_name,
        set_name=None,
        card_number=card_number,
        grading_company=grading_company,
        grade=grade,
        price=price,
        currency="USD",
        sold_date=sold_date,
        listing_url=raw.listing_url,
        image_url=raw.image_url,
        source=Source.EBAY,
        raw_title=title,
    )

    record_dict = record.model_dump()
    record.content_hash = compute_normalized_record_hash(record_dict)

    return record


def _extract_grading_company(title: str) -> str | None:
    for company, pattern in GRADING_COMPANIES.items():
        if re.search(pattern, title, re.IGNORECASE):
            return company
    return None


def _extract_grade(title: str) -> str | None:
    match = GRADE_PATTERN.search(title)
    return match.group(1) if match else None


def _extract_card_number(title: str) -> str | None:
    match = CARD_NUMBER_PATTERN.search(title)
    return match.group(1).replace(" ", "") if match else None


def _parse_price(price_str: str | None) -> float | None:
    if not price_str:
        return None
    match = PRICE_PATTERN.search(price_str)
    if match:
        return float(match.group(1).replace(",", ""))
    return None


def _parse_sold_date(date_str: str | None) -> datetime | None:
    if not date_str:
        return None

    cleaned = re.sub(r"^Sold\s+", "", date_str, flags=re.IGNORECASE).strip()

    for fmt in ("%b %d, %Y", "%B %d, %Y", "%m/%d/%Y", "%d %b %Y"):
        try:
            return datetime.strptime(cleaned, fmt)
        except ValueError:
            continue
    return None


def _extract_card_name(
    title: str,
    grading_company: str | None,
    grade: str | None,
    card_number: str | None,
) -> str:
    """Best-effort extraction of the card name by stripping known tokens."""
    name = title

    if grading_company and grade:
        name = re.sub(
            rf"\b{grading_company}\s*{grade}\b", "", name, flags=re.IGNORECASE
        )
    elif grading_company:
        name = re.sub(rf"\b{grading_company}\b", "", name, flags=re.IGNORECASE)

    if card_number:
        name = name.replace(card_number, "")

    name = re.sub(r"[#\-\|]", " ", name)
    name = re.sub(r"\s+", " ", name).strip()

    return name
