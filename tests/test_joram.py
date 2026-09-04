import datetime

import pytest
from unittest.mock import patch, MagicMock

import requests

from joram import (
    get_sorted_pdf_links,
    read_pdf_prices,
    fetch_pdf_bytes,
    pdf_creation_date,
    extract_gas_prices,
    retrieve_newest_pdf_gas_info,
)
from constants import GASOLINE_95, DIESEL, COLORED_DIESEL

PDF_TEXT = (
    "Gasolina super sem chumbo IO 95... 1,751\n"
    "Gasóleo rodoviário... 1,521\n"
    "Gasóleo colorido e marcado... 1,144\n"
)


def test_get_sorted_pdf_links():
    mock_html = """
    <html>
        <body>
            <a href="http://example.com/2024-05-20.pdf">Link 1</a>
            <a href="http://example.com/2024-05-21.pdf">Link 2</a>
            <a href="http://example.com/not-a-pdf.html">Link 3</a>
        </body>
    </html>
    """
    with patch("requests.get") as mock_get:
        mock_get.return_value.text = mock_html
        links = get_sorted_pdf_links("http://example.com")

        assert len(links) == 2
        assert links[0]["href"] == "http://example.com/2024-05-20.pdf"
        assert links[1]["href"] == "http://example.com/2024-05-21.pdf"


def test_get_sorted_pdf_links_network_error():
    with patch("requests.get", side_effect=requests.exceptions.ConnectionError):
        assert get_sorted_pdf_links("http://example.com") == []


def test_fetch_pdf_bytes_encodes_url():
    with patch("requests.get") as mock_get:
        mock_get.return_value.raise_for_status.return_value = None
        mock_get.return_value.content = b"pdf"
        assert fetch_pdf_bytes("https://x/Ano de 2024/file.pdf") == b"pdf"
        assert "Ano%20de" in mock_get.call_args.args[0]


def _pdf_reader_mock(text):
    mock_page = MagicMock()
    mock_page.extract_text.return_value = text
    return MagicMock(pages=[mock_page])


@patch("joram.PdfReader")
@patch("requests.get")
def test_read_pdf_prices(mock_get, mock_pdf_reader):
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b"fake pdf content"
    mock_pdf_reader.return_value = _pdf_reader_mock(PDF_TEXT)

    prices = dict(read_pdf_prices("http://example.com/test.pdf"))

    assert len(prices) == 3
    assert prices["Gasolina super sem chumbo IO 95"] == "1,751"
    assert prices["Gasóleo rodoviário"] == "1,521"
    assert prices["Gasóleo colorido e marcado"] == "1,144"


@patch("requests.get", side_effect=requests.exceptions.ConnectionError)
def test_read_pdf_prices_network_error_returns_empty(mock_get):
    assert read_pdf_prices("http://example.com/test.pdf") == []


@patch("joram.PdfReader")
def test_extract_gas_prices_split_lines(mock_pdf_reader):
    # 2008-era PDFs put the price on a separate line from the fuel name
    mock_pdf_reader.return_value = _pdf_reader_mock(
        "Gasolina super sem chumbo IO 95\n1,751\n"
        "Gasóleo rodoviário\n1,521\n"
        "Gasóleo colorido e marcado\n1,144\n"
    )
    assert extract_gas_prices(b"bytes") == [
        ("Gasolina super sem chumbo IO 95", "1,751"),
        ("Gasóleo rodoviário", "1,521"),
        ("Gasóleo colorido e marcado", "1,144"),
    ]


@patch("joram.PdfReader")
def test_pdf_creation_date(mock_pdf_reader):
    mock_reader_instance = mock_pdf_reader.return_value
    mock_reader_instance.metadata.creation_date = "2024-05-20"
    assert pdf_creation_date(b"bytes") == "2024-05-20"


@patch("joram.PdfReader")
def test_pdf_creation_date_missing_metadata(mock_pdf_reader):
    mock_pdf_reader.return_value.metadata = None
    assert pdf_creation_date(b"bytes") is None


@patch("joram.get_sorted_pdf_links")
@patch("joram.pdf_creation_date")
@patch("joram.extract_gas_prices")
@patch("joram.fetch_pdf_bytes")
def test_retrieve_newest_pdf_gas_info_skips_empty_pdfs_and_reuses_bytes(
    mock_fetch, mock_extract, mock_creation, mock_links
):
    # Newest PDF (popped last) has no prices; the older one has them all.
    mock_links.return_value = [
        {"href": ".../2024-05-20.pdf"},
        {"href": ".../2024-05-27.pdf"},
    ]
    mock_fetch.side_effect = [b"newest", b"older"]
    mock_extract.side_effect = [
        [],
        [
            ("Gasolina super sem chumbo IO 95", "1,751"),
            ("Gasóleo rodoviário", "1,521"),
            ("Gasóleo colorido e marcado", "1,144"),
        ],
    ]
    mock_creation.return_value = datetime.datetime(2024, 5, 21)

    result = retrieve_newest_pdf_gas_info()

    assert mock_fetch.call_count == 2  # one fetch per PDF checked
    assert result["pdf_url"].endswith("2024-05-20.pdf")
    assert result["creation_date"] == datetime.datetime(2024, 5, 21)
    assert result["gas_info"] == {
        GASOLINE_95: "1,751",
        DIESEL: "1,521",
        COLORED_DIESEL: "1,144",
    }
    # The same bytes used for prices must be reused for the creation date,
    # proving the PDF is fetched only once.
    assert mock_creation.call_args.args[0] == mock_extract.call_args_list[1].args[0]


@patch("joram.get_sorted_pdf_links")
@patch("joram.pdf_creation_date")
@patch("joram.extract_gas_prices")
@patch("joram.fetch_pdf_bytes")
def test_retrieve_newest_pdf_gas_info_defaults_creation_date_to_today(
    mock_fetch, mock_extract, mock_creation, mock_links
):
    mock_links.return_value = [{"href": ".../2024-05-27.pdf"}]
    mock_fetch.return_value = b"bytes"
    mock_extract.return_value = [
        ("Gasolina super sem chumbo IO 95", "1,751"),
        ("Gasóleo rodoviário", "1,521"),
        ("Gasóleo colorido e marcado", "1,144"),
    ]
    mock_creation.return_value = None  # PDF has no embedded creation metadata

    result = retrieve_newest_pdf_gas_info()

    now = datetime.datetime.now()
    assert (now - result["creation_date"]).total_seconds() < 60
    assert result["gas_info"][GASOLINE_95] == "1,751"


@patch("joram.get_sorted_pdf_links")
@patch("joram.fetch_pdf_bytes")
@patch("joram.extract_gas_prices")
def test_retrieve_newest_pdf_gas_info_none_when_no_prices(
    mock_extract, mock_fetch, mock_links
):
    mock_links.return_value = [{"href": ".../2024-05-27.pdf"}]
    mock_fetch.return_value = b"bytes"
    mock_extract.return_value = []
    assert retrieve_newest_pdf_gas_info() is None


@patch("joram.get_sorted_pdf_links")
@patch("joram.fetch_pdf_bytes", side_effect=requests.exceptions.ConnectionError)
@patch("joram.extract_gas_prices")
def test_retrieve_newest_pdf_gas_info_fetch_error_moves_on(
    mock_extract, mock_fetch, mock_links
):
    mock_links.return_value = [
        {"href": ".../2024-05-20.pdf"},
        {"href": ".../2024-05-27.pdf"},
    ]
    assert retrieve_newest_pdf_gas_info() is None
