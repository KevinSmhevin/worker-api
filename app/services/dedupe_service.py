import hashlib
import json

from app.core.logging import get_logger

logger = get_logger(__name__)


def compute_content_hash(data: dict, fields: list[str] | None = None) -> str:
    """Compute SHA-256 hash from selected fields of a dict.

    If fields is None, hash all keys sorted alphabetically.
    """
    if fields:
        subset = {k: data.get(k) for k in sorted(fields)}
    else:
        subset = {k: data[k] for k in sorted(data.keys())}

    canonical = json.dumps(subset, sort_keys=True, default=str)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def compute_raw_html_hash(html: str) -> str:
    """Compute SHA-256 hash of raw HTML content."""
    return hashlib.sha256(html.encode("utf-8")).hexdigest()


NORMALIZED_RECORD_HASH_FIELDS = [
    "card_name",
    "card_number",
    "grade",
    "grading_company",
    "listing_url",
    "price",
    "set_name",
    "sold_date",
    "source",
]


def compute_normalized_record_hash(record: dict) -> str:
    return compute_content_hash(record, fields=NORMALIZED_RECORD_HASH_FIELDS)
