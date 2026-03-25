import pytest
from unittest.mock import patch, MagicMock
from joram import get_sorted_pdf_links, read_pdf_prices, retrieve_pdf_creation_date


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


@patch("joram.PdfReader")
@patch("requests.get")
def test_read_pdf_prices(mock_get, mock_pdf_reader):
    mock_get.return_value.status_code = 200
    mock_get.return_value.content = b"fake pdf content"

    mock_page = MagicMock()
    mock_page.extract_text.return_value = (
        "Gasolina super sem chumbo IO 95... 1,751\n"
        "Gasóleo rodoviário... 1,521\n"
        "Gasóleo colorido e marcado... 1,144\n"
    )
    mock_pdf_reader.return_value.pages = [mock_page]

    prices = dict(read_pdf_prices("http://example.com/test.pdf"))

    assert len(prices) == 3
    assert prices["Gasolina super sem chumbo IO 95"] == "1,751"
    assert prices["Gasóleo rodoviário"] == "1,521"
    assert prices["Gasóleo colorido e marcado"] == "1,144"


@patch("joram.PdfReader")
@patch("requests.get")
def test_retrieve_pdf_creation_date(mock_get, mock_pdf_reader):
    mock_get.return_value.content = b"fake pdf content"
    mock_reader_instance = mock_pdf_reader.return_value
    mock_reader_instance.metadata.creation_date = "2024-05-20"

    date = retrieve_pdf_creation_date("http://example.com/test.pdf")
    assert date == "2024-05-20"
