import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the path to the source files
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import update_gas_prices


class TestUpdateGasPrice(unittest.TestCase):
    @patch("update_gas_prices.retrieve_newest_pdf_gas_info")
    @patch("update_gas_prices.open", create=True)
    @patch("update_gas_prices.json.load")
    def test_update_gas_pricess(self, mock_json_load, mock_open, mock_retrieve_info):
        mock_open.return_value.__enter__.return_value = MagicMock()
        mock_json_load.return_value = {
            "current": {"Start date": "2024-05-20", "End date": "2024-05-26"}
        }
        mock_retrieve_info.return_value = {
            "gas_info": {
                "Gasolina IO95": "1.641",
                "Gasóleo Rodoviário": "1.336",
                "Gasóleo Colorido e Marcado": "1.017",
            },
            "creation_date": "2024-05-19T00:00:00",
        }
        with patch("update_gas_prices.add_history"), patch(
            "update_gas_prices.make_tweet"
        ):
            update_gas_prices.main()


if __name__ == "__main__":
    unittest.main()
