import json
from pathlib import Path

from app.adapters.ebay.parser import parse_sold_listings

FIXTURES_DIR = Path(__file__).parent.parent.parent / "fixtures"


def _load_html_fixture() -> str:
    return (FIXTURES_DIR / "html" / "ebay" / "sold_listings_sample.html").read_text()


def _load_expected_json() -> list[dict]:
    return json.loads(
        (FIXTURES_DIR / "json" / "ebay" / "expected_parsed.json").read_text()
    )


class TestParseEbaySoldListings:
    def test_parses_correct_number_of_items(self):
        html = _load_html_fixture()
        records = parse_sold_listings(html)
        # 5 items in HTML, but "Shop on eBay" is filtered out
        assert len(records) == 4

    def test_filters_shop_on_ebay(self):
        html = _load_html_fixture()
        records = parse_sold_listings(html)
        titles = [r.title for r in records]
        assert "Shop on eBay" not in titles

    def test_extracts_titles(self):
        html = _load_html_fixture()
        records = parse_sold_listings(html)
        expected = "PSA 10 Charizard VMAX 074/073 Champion's Path 2020 Pokemon"
        assert expected in records[0].title
        assert "BGS 9.5 Luffy Gear 5 OP05-119 SEC One Piece TCG" in records[1].title

    def test_extracts_prices(self):
        html = _load_html_fixture()
        records = parse_sold_listings(html)
        assert records[0].price == "$450.00"
        assert records[1].price == "$320.50"
        assert records[2].price == "$89.99"

    def test_extracts_sold_dates(self):
        html = _load_html_fixture()
        records = parse_sold_listings(html)
        assert "Jun 15, 2025" in records[0].sold_date
        assert "May 20, 2025" in records[1].sold_date

    def test_extracts_listing_urls(self):
        html = _load_html_fixture()
        records = parse_sold_listings(html)
        assert records[0].listing_url == "https://www.ebay.com/itm/123456789"
        assert records[1].listing_url == "https://www.ebay.com/itm/987654321"

    def test_extracts_image_urls(self):
        html = _load_html_fixture()
        records = parse_sold_listings(html)
        assert records[0].image_url == "https://i.ebayimg.com/images/g/charizard.jpg"

    def test_source_is_ebay(self):
        html = _load_html_fixture()
        records = parse_sold_listings(html)
        for record in records:
            assert record.source == "ebay"

    def test_matches_expected_json(self):
        html = _load_html_fixture()
        records = parse_sold_listings(html)
        expected = _load_expected_json()
        assert len(records) == len(expected)
        for record, exp in zip(records, expected):
            assert record.title == exp["title"]
            assert record.price == exp["price"]
            assert record.listing_url == exp["listing_url"]

    def test_empty_html_returns_empty_list(self):
        records = parse_sold_listings("<html><body></body></html>")
        assert records == []

    def test_no_items_container_returns_empty_list(self):
        html = "<html><body><ul class='other'></ul></body></html>"
        records = parse_sold_listings(html)
        assert records == []
