import unittest
from datetime import datetime, timedelta

# Add the path to the source files
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import functions


class TestFunctions(unittest.TestCase):
    def test_replace_gas_keys_names(self):
        gas_prices = {
            "Gasolina super sem chumbo IO 95": "1.641",
            "Gasóleo rodoviário": "1.336",
            "Gasóleo colorido e marcado": "1.017",
        }
        result = functions.replace_gas_keys_names(gas_prices)
        self.assertIn("Gasolina IO95", result)
        self.assertIn("Gasóleo Rodoviário", result)
        self.assertIn("Gasóleo Colorido e Marcado", result)

    def test_retrieve_week_by_date(self):
        date = datetime(2024, 5, 20)
        result = functions.retrieve_week_by_date(date)
        self.assertEqual(result[0], "2024-05-20")
        self.assertEqual(result[1], "2024-05-26")

    def test_return_next_week_by_date(self):
        date = datetime(2024, 5, 20)
        result = functions.return_next_week_by_date(date)
        self.assertEqual(result.strftime("%Y-%m-%d"), "2024-05-27")


if __name__ == "__main__":
    unittest.main()
