"""Unit tests that don't hit the Anthropic API.

The deliberate choice: test the pure logic (parsing, schema, media types) without
calling Claude. API calls belong in an eval suite (Month 3), not unit tests.
"""

import pytest
from pydantic import ValidationError

from main import Invoice, media_type_for


class TestMediaType:
    def test_jpg_becomes_jpeg(self):
        assert media_type_for(".jpg") == "image/jpeg"

    def test_jpeg_stays_jpeg(self):
        assert media_type_for(".jpeg") == "image/jpeg"

    def test_png_stays_png(self):
        assert media_type_for(".png") == "image/png"

    def test_uppercase_normalised(self):
        assert media_type_for(".PNG") == "image/png"


class TestInvoiceSchema:
    def test_valid_invoice_parses(self):
        raw = (
            '{"vendor": "Acme", "invoice_number": "INV-1", "date": "2025-01-15",'
            ' "total_amount": 99.5, "currency": "USD"}'
        )
        inv = Invoice.model_validate_json(raw)
        assert inv.vendor == "Acme"
        assert inv.total_amount == 99.5

    def test_missing_field_raises(self):
        raw = '{"vendor": "Acme", "invoice_number": "INV-1", "date": "2025-01-15"}'
        with pytest.raises(ValidationError):
            Invoice.model_validate_json(raw)

    def test_wrong_type_coerces_or_raises(self):
        raw = (
            '{"vendor": "Acme", "invoice_number": "INV-1", "date": "2025-01-15",'
            ' "total_amount": "not-a-number", "currency": "USD"}'
        )
        with pytest.raises(ValidationError):
            Invoice.model_validate_json(raw)
