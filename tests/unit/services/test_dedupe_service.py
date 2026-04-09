from app.services.dedupe_service import (
    compute_content_hash,
    compute_normalized_record_hash,
    compute_raw_html_hash,
)


class TestComputeContentHash:
    def test_deterministic(self):
        data = {"a": 1, "b": "hello"}
        h1 = compute_content_hash(data)
        h2 = compute_content_hash(data)
        assert h1 == h2

    def test_different_data_different_hash(self):
        h1 = compute_content_hash({"a": 1})
        h2 = compute_content_hash({"a": 2})
        assert h1 != h2

    def test_order_independent(self):
        h1 = compute_content_hash({"b": 2, "a": 1})
        h2 = compute_content_hash({"a": 1, "b": 2})
        assert h1 == h2

    def test_with_fields_filter(self):
        data = {"a": 1, "b": 2, "c": 3}
        h_full = compute_content_hash(data)
        h_partial = compute_content_hash(data, fields=["a", "b"])
        assert h_full != h_partial

    def test_sha256_length(self):
        h = compute_content_hash({"x": "test"})
        assert len(h) == 64


class TestComputeRawHtmlHash:
    def test_deterministic(self):
        html = "<html><body>test</body></html>"
        h1 = compute_raw_html_hash(html)
        h2 = compute_raw_html_hash(html)
        assert h1 == h2

    def test_different_html_different_hash(self):
        h1 = compute_raw_html_hash("<html>a</html>")
        h2 = compute_raw_html_hash("<html>b</html>")
        assert h1 != h2


class TestComputeNormalizedRecordHash:
    def test_uses_specified_fields(self):
        record = {
            "card_name": "Charizard",
            "card_number": "074/073",
            "grade": "10",
            "grading_company": "PSA",
            "listing_url": "https://ebay.com/123",
            "price": 450.0,
            "set_name": "Champion's Path",
            "sold_date": "2025-06-15",
            "source": "ebay",
            "irrelevant_field": "should not affect hash",
        }
        h1 = compute_normalized_record_hash(record)

        record2 = {**record, "irrelevant_field": "different value"}
        h2 = compute_normalized_record_hash(record2)

        assert h1 == h2

    def test_different_relevant_fields_different_hash(self):
        base = {
            "card_name": "Charizard",
            "card_number": "074/073",
            "grade": "10",
            "grading_company": "PSA",
            "listing_url": "https://ebay.com/123",
            "price": 450.0,
            "set_name": "Champion's Path",
            "sold_date": "2025-06-15",
            "source": "ebay",
        }
        h1 = compute_normalized_record_hash(base)

        modified = {**base, "price": 500.0}
        h2 = compute_normalized_record_hash(modified)

        assert h1 != h2
