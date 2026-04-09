from app.adapters.ebay.normalizer import (
    _extract_card_name,
    _extract_card_number,
    _extract_grade,
    _extract_grading_company,
    _parse_price,
    _parse_sold_date,
    normalize_single,
)
from app.schemas.domain.raw_record import RawRecord


class TestExtractGradingCompany:
    def test_psa(self):
        assert _extract_grading_company("PSA 10 Charizard") == "PSA"

    def test_bgs(self):
        assert _extract_grading_company("BGS 9.5 Luffy") == "BGS"

    def test_cgc(self):
        assert _extract_grading_company("CGC 9 Pikachu VMAX") == "CGC"

    def test_sgc(self):
        assert _extract_grading_company("SGC 10 Mewtwo") == "SGC"

    def test_no_grading_company(self):
        assert _extract_grading_company("Booster Box Sealed") is None

    def test_case_insensitive(self):
        assert _extract_grading_company("psa 10 Charizard") == "PSA"


class TestExtractGrade:
    def test_integer_grade(self):
        assert _extract_grade("PSA 10 Charizard") == "10"

    def test_decimal_grade(self):
        assert _extract_grade("BGS 9.5 Luffy") == "9.5"

    def test_no_grade(self):
        assert _extract_grade("Booster Box Sealed") is None


class TestExtractCardNumber:
    def test_standard_format(self):
        assert _extract_card_number("Charizard 074/073") == "074/073"

    def test_three_digit(self):
        assert _extract_card_number("Pikachu VMAX 188/185") == "188/185"

    def test_no_number(self):
        assert _extract_card_number("Booster Box Sealed") is None

    def test_spaced_slash(self):
        assert _extract_card_number("Charizard 74 / 73") == "74/73"


class TestParsePrice:
    def test_dollar_amount(self):
        assert _parse_price("$450.00") == 450.00

    def test_no_dollar_sign(self):
        assert _parse_price("320.50") == 320.50

    def test_comma_separated(self):
        assert _parse_price("$1,250.00") == 1250.00

    def test_none(self):
        assert _parse_price(None) is None

    def test_empty_string(self):
        assert _parse_price("") is None


class TestParseSoldDate:
    def test_standard_format(self):
        dt = _parse_sold_date("Sold  Jun 15, 2025")
        assert dt is not None
        assert dt.month == 6
        assert dt.day == 15
        assert dt.year == 2025

    def test_without_sold_prefix(self):
        dt = _parse_sold_date("May 20, 2025")
        assert dt is not None
        assert dt.month == 5

    def test_none(self):
        assert _parse_sold_date(None) is None

    def test_unparseable(self):
        assert _parse_sold_date("not a date") is None


class TestExtractCardName:
    def test_strips_grading_and_number(self):
        name = _extract_card_name(
            "PSA 10 Charizard VMAX 074/073", "PSA", "10", "074/073"
        )
        assert "Charizard" in name
        assert "PSA" not in name
        assert "074/073" not in name

    def test_no_grading(self):
        name = _extract_card_name("Booster Box Sealed", None, None, None)
        assert name == "Booster Box Sealed"


class TestNormalizeSingle:
    def test_full_normalization(self):
        raw = RawRecord(
            title="PSA 10 Charizard VMAX 074/073 Champion's Path 2020 Pokemon",
            price="$450.00",
            sold_date="Sold  Jun 15, 2025",
            listing_url="https://www.ebay.com/itm/123456789",
            image_url="https://i.ebayimg.com/images/g/charizard.jpg",
            source="ebay",
        )
        result = normalize_single(raw)
        assert result is not None
        assert result.grading_company == "PSA"
        assert result.grade == "10"
        assert result.card_number == "074/073"
        assert result.price == 450.00
        assert result.source == "ebay"
        assert result.content_hash != ""
        assert result.listing_url == "https://www.ebay.com/itm/123456789"

    def test_ungraded_card(self):
        raw = RawRecord(
            title="Pokemon Booster Box Scarlet & Violet 151 SEALED",
            price="$155.00",
            sold_date="Sold  Mar 5, 2025",
            listing_url="https://www.ebay.com/itm/444555666",
            source="ebay",
        )
        result = normalize_single(raw)
        assert result is not None
        assert result.grading_company is None
        assert result.grade is None
        assert result.price == 155.00

    def test_one_piece_card(self):
        raw = RawRecord(
            title="BGS 9.5 Luffy Gear 5 OP05-119 SEC One Piece TCG",
            price="$320.50",
            sold_date="Sold  May 20, 2025",
            listing_url="https://www.ebay.com/itm/987654321",
            source="ebay",
        )
        result = normalize_single(raw)
        assert result is not None
        assert result.grading_company == "BGS"
        assert result.grade == "9.5"
        assert result.price == 320.50
