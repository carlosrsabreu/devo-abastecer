import unittest
from unittest.mock import patch, mock_open, MagicMock
from joram import (
    retrieve_newest_pdf_gas_info,
    read_pdf_prices,
    retrieve_pdf_creation_date,
)


class TestJoram(unittest.TestCase):

    @patch("joram.requests.get")
    @patch("joram.replace_gas_keys_names")
    def test_retrieve_newest_pdf_gas_info(self, mock_replace, mock_get):
        # Mock responses and function return values
        mock_response = MagicMock()
        mock_response.content = b"%PDF-1.4 example content"
        mock_get.return_value = mock_response
        mock_replace.return_value = {"Gasolina IO95": "1,600"}

        # Call the function
        result = retrieve_newest_pdf_gas_info()

        # Assert the results
        self.assertIn("gas_info", result)
        self.assertIn("creation_date", result)

    @patch("joram.requests.get")
    def test_retrieve_pdf_creation_date(self, mock_get):
        # Mock PDF response content and creation date
        mock_response = MagicMock()
        mock_response.content = b"%PDF-1.4 example content"
        mock_get.return_value = mock_response
        result = retrieve_pdf_creation_date("https://example.com/pdf")

        # Assert creation date exists
        self.assertIsNotNone(result)


if __name__ == "__main__":
    unittest.main()
