import pytest
from unittest.mock import patch, MagicMock
from joram import retrieve_newest_pdf_gas_info, retrieve_pdf_creation_date


@patch("joram.requests.get")
@patch("joram.replace_gas_keys_names")
def test_retrieve_newest_pdf_gas_info(mock_replace, mock_get):
    # Mock responses and function return values
    mock_response = MagicMock()
    mock_response.content = (
        b"%PDF-1.4\n%..."  # Mock a simple valid PDF header
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj\n"
        b"4 0 obj << /Length 44 >> stream\nBT /F1 24 Tf 100 700 Td (Hello World) Tj ET endstream endobj\n"
        b"xref\n0 5\n0000000000 65535 f\n0000000010 00000 n\n0000000079 00000 n\n0000000179 00000 n\n0000000273 00000 n\n"
        b"trailer << /Size 5 /Root 1 0 R >>\nstartxref\n349\n%%EOF"
    )
    mock_get.return_value = mock_response
    mock_replace.return_value = {"Gasolina IO95": "1,600"}

    # Call the function
    result = retrieve_newest_pdf_gas_info()
    assert result == {"Gasolina IO95": "1,600"}


@patch("joram.requests.get")
def test_retrieve_pdf_creation_date(mock_get):
    # Mock PDF response content and creation date
    mock_response = MagicMock()
    mock_response.content = (
        b"%PDF-1.4\n%..."  # Mock a simple valid PDF header
        b"1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n"
        b"2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n"
        b"3 0 obj << /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R >> endobj\n"
        b"4 0 obj << /Length 44 >> stream\nBT /F1 24 Tf 100 700 Td (Hello World) Tj ET endstream endobj\n"
        b"xref\n0 5\n0000000000 65535 f\n0000000010 00000 n\n0000000079 00000 n\n0000000179 00000 n\n0000000273 00000 n\n"
        b"trailer << /Size 5 /Root 1 0 R >>\nstartxref\n349\n%%EOF"
    )
    mock_get.return_value = mock_response

    result = retrieve_pdf_creation_date("https://example.com/pdf")
    assert result == datetime.datetime(
        2024,
        5,
        31,
        15,
        51,
        21,
        tzinfo=datetime.timezone(datetime.timedelta(seconds=3600)),
    )
