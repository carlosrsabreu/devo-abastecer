import datetime

import pytest

from functions import (
    retrieve_week_by_date,
    return_next_week_by_date,
    replace_gas_keys_names,
    parse_price,
    csv_row,
    get_gas_prices_message,
    format_social_media_message,
)
from constants import (
    GASOLINE_95,
    DIESEL,
    COLORED_DIESEL,
    GASOLINE_98,
    GAS_KEY,
    CURRENT_WEEK,
    PREVIOUS_WEEK,
    START_DATE_KEY,
    END_DATE_KEY,
)

GAS = {GASOLINE_95: 1.8, DIESEL: 1.5, COLORED_DIESEL: 1.1, GASOLINE_98: 1.95}


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


def test_retrieve_week_by_date_invalid():
    with pytest.raises(ValueError):
        retrieve_week_by_date("2024-05-20")


def test_return_next_week_by_date():
    date = datetime.datetime(2024, 5, 20)
    expected_next_week = datetime.datetime(2024, 5, 27)
    assert return_next_week_by_date(date) == expected_next_week


def test_return_next_week_by_date_invalid():
    with pytest.raises(ValueError):
        return_next_week_by_date("2024-05-20")


def test_replace_gas_keys_names():
    input_prices = {
        "Gasolina super sem chumbo IO 95": "1.751",
        "Gasóleo rodoviário": "1.521",
        "Gasóleo colorido e marcado": "1.144",
    }
    expected_output = {
        GASOLINE_95: "1.751",
        DIESEL: "1.521",
        COLORED_DIESEL: "1.144",
    }
    assert replace_gas_keys_names(input_prices) == expected_output


def test_replace_gas_keys_names_with_variations():
    input_prices = {
        "Gasolina  super  sem  chumbo  IO  95": "1.751",
        "Gasóleo rodoviário": "1.521",
        "Gasóleo colorido e marcado": "1.144",
    }
    expected_output = {
        GASOLINE_95: "1.751",
        DIESEL: "1.521",
        COLORED_DIESEL: "1.144",
    }
    assert replace_gas_keys_names(input_prices) == expected_output


def test_replace_gas_keys_names_missing_key():
    input_prices = {
        "Gasolina super sem chumbo IO 95": "1.751",
        "Gasóleo colorido e marcado": "1.144",
    }
    result = replace_gas_keys_names(input_prices)
    assert DIESEL not in result
    assert result[GASOLINE_95] == "1.751"
    assert result[COLORED_DIESEL] == "1.144"


def test_parse_price():
    assert parse_price("1,751") == 1.751
    assert parse_price("1.751") == 1.751
    with pytest.raises(ValueError):
        parse_price("abc")


def test_csv_row():
    row = csv_row(
        "2024-05-20",
        "2024-05-26",
        {GASOLINE_95: "1.8", DIESEL: "1.5", COLORED_DIESEL: "1.1", GASOLINE_98: "1.95"},
        "http://pdf",
    )
    assert row == "2024-05-20,2024-05-26,1.8,1.5,1.1,1.95,http://pdf\n"


def test_csv_row_missing_keys():
    row = csv_row("2024-05-20", "2024-05-26", {}, "http://pdf")
    assert row == "2024-05-20,2024-05-26,,,,,http://pdf\n"


def test_get_gas_prices_message():
    assert "2.000" in get_gas_prices_message(2.0, 1.5)
    assert "1.500" in get_gas_prices_message(2.0, 1.5)
    assert "2.000" in get_gas_prices_message(1.5, 2.0)
    assert "=" in get_gas_prices_message(1.5, 1.5)
    assert get_gas_prices_message(None, 1.5) == "N/A"
    assert get_gas_prices_message("abc", 1.5) == "abc€   ?   1.5€"


def test_format_social_media_message():
    dict_prices = {
        CURRENT_WEEK: {
            START_DATE_KEY: "2024-05-20",
            END_DATE_KEY: "2024-05-26",
            GAS_KEY: {DIESEL: "1.5", GASOLINE_95: "1.8", GASOLINE_98: "1.95"},
        },
        PREVIOUS_WEEK: {
            START_DATE_KEY: "2024-05-13",
            END_DATE_KEY: "2024-05-19",
            GAS_KEY: {DIESEL: "1.4", GASOLINE_95: "1.7", GASOLINE_98: "1.85"},
        },
    }
    message = format_social_media_message(dict_prices)
    assert "2024-05-20" in message
    assert "2024-05-13" in message
    assert "1.500" in message
    assert "1.400" in message


def test_format_social_media_message_missing_key():
    assert format_social_media_message({}) is None