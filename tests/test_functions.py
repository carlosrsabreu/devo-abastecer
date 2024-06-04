import unittest
from functions import (
    retrieve_week_by_date,
    return_next_week_by_date,
    replace_gas_keys_names,
)


class TestFunctions(unittest.TestCase):

    def test_retrieve_week_by_date(self):
        date = datetime.datetime(2024, 5, 20)
        start, end = retrieve_week_by_date(date)
        self.assertEqual(start, "2024-05-20")
        self.assertEqual(end, "2024-05-26")

    def test_return_next_week_by_date(self):
        date = datetime.datetime(2024, 5, 20)
        next_week = return_next_week_by_date(date)
        self.assertEqual(next_week, datetime.datetime(2024, 5, 27))

    def test_replace_gas_keys_names(self):
        gas_prices = {
            "Gasolina super sem chumbo IO 95": "1,641",
            "Gasóleo rodoviário": "1,336",
            "Gasóleo colorido e marcado": "1,017",
        }
        replaced = replace_gas_keys_names(gas_prices)
        self.assertIn("Gasolina IO95", replaced)
        self.assertIn("Gasóleo Rodoviário", replaced)
        self.assertIn("Gasóleo Colorido e Marcado", replaced)


if __name__ == "__main__":
    unittest.main()
