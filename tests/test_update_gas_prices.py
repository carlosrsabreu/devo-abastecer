import unittest
from unittest.mock import patch, mock_open
import json
from update_gas_prices import update_gas_prices


class TestUpdateGasPrice(unittest.TestCase):

    @patch("update_gas_prices.retrieve_newest_pdf_gas_info")
    @patch(
        "update_gas_prices.open",
        new_callable=mock_open,
        read_data='{"current": {"Start date": "2024-05-20", "End date": "2024-05-26"}}',
    )
    def test_update_gas_prices(self, mock_file, mock_retrieve_info):
        # Mock gas info
        mock_retrieve_info.return_value = {
            "gas_info": {
                "Gasolina IO95": "1,641",
                "Gasóleo Rodoviário": "1,336",
                "Gasóleo Colorido e Marcado": "1,017",
                "Gasolina IO98": "1,791",
            },
            "creation_date": "2024-05-26T00:00:00Z",
        }

        # Call function
        update_gas_prices()

        # Assert the file was opened and written
        mock_file.assert_called_with("gas_info.json", "w")


if __name__ == "__main__":
    unittest.main()
