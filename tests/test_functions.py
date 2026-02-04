import datetime
from functions import retrieve_week_by_date, return_next_week_by_date, replace_gas_keys_names
from constants import GASOLINE_95, DIESEL, COLORED_DIESEL

def test_retrieve_week_by_date():
    # Test with a known Monday (2024-05-20)
    date_monday = datetime.datetime(2024, 5, 20)
    expected_monday = ["2024-05-20", "2024-05-26"]
    assert retrieve_week_by_date(date_monday) == expected_monday

    # Test with a known Sunday (2024-05-26)
    date_sunday = datetime.datetime(2024, 5, 26)
    assert retrieve_week_by_date(date_sunday) == expected_monday

    # Test with a date in the middle of the week (2024-05-22, Wednesday)
    date_wednesday = datetime.datetime(2024, 5, 22)
    assert retrieve_week_by_date(date_wednesday) == expected_monday

def test_return_next_week_by_date():
    date = datetime.datetime(2024, 5, 20)
    expected_next_week = datetime.datetime(2024, 5, 27)
    assert return_next_week_by_date(date) == expected_next_week

def test_replace_gas_keys_names():
    input_prices = {
        "Gasolina super sem chumbo IO 95": "1.751",
        "Gasóleo rodoviário": "1.521",
        "Gasóleo colorido e marcado": "1.144"
    }
    expected_output = {
        GASOLINE_95: "1.751",
        DIESEL: "1.521",
        COLORED_DIESEL: "1.144"
    }
    assert replace_gas_keys_names(input_prices) == expected_output

def test_replace_gas_keys_names_with_variations():
    input_prices = {
        "Gasolina  super  sem  chumbo  IO  95": "1.751",
        "Gasóleo rodoviário": "1.521",
        "Gasóleo colorido e marcado": "1.144"
    }
    expected_output = {
        GASOLINE_95: "1.751",
        DIESEL: "1.521",
        COLORED_DIESEL: "1.144"
    }
    assert replace_gas_keys_names(input_prices) == expected_output
