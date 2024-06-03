import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the path to the source files
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import joram


class TestJoram(unittest.TestCase):
    @patch("joram.requests.get")
    def test_retrieve_newest_pdf_gas_info(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = b"%PDF-1.4..."
        mock_get.return_value = mock_response

        with patch("joram.sorted_pdf_links", [{"href": "2024-05-20-some-file.pdf"}]):
            result = joram.retrieve_newest_pdf_gas_info()

        self.assertIn("gas_info", result)
        self.assertIn("creation_date", result)

    @patch("joram.requests.get")
    def test_read_pdf_prices(self, mock_get):
        mock_response = MagicMock()
        mock_response.content = b"%PDF-1.4..."
        mock_get.return_value = mock_response

        result = list(joram.read_pdf_prices("https://example.com/pdf"))
        self.assertIsInstance(result, list)


if __name__ == "__main__":
    unittest.main()
