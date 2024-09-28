import pytest
import datetime
from functions import (
    retrieve_week_by_date,
    return_next_week_by_date,
    replace_gas_keys_names,
)


def test_retrieve_week_by_date():
    date = datetime.datetime(2024, 5, 15)
    start_date, end_date = retrieve_week_by_date(date)
    assert start_date == "2024-05-13"
    assert end_date == "2024-05-19"


def test_return_next_week_by_date():
    date = datetime.datetime(2024, 5, 15)
    next_week = return_next_week_by_date(date)
    assert next_week == date + datetime.timedelta(weeks=1)


def test_replace_gas_keys_names():
    gas_prices = {
        "Gasolina super sem chumbo IO 95": "1,630",
        "Gasóleo rodoviário": "1,323",
        "Gasóleo colorido e marcado": "1,005",
    }
    replaced_gas_prices = replace_gas_keys_names(gas_prices)
    assert "Gasolina IO95" in replaced_gas_prices
    assert "Gasóleo Rodoviário" in replaced_gas_prices
    assert "Gasóleo Colorido e Marcado" in replaced_gas_prices
    assert replaced_gas_prices["Gasolina IO95"] == "1,630"
    assert replaced_gas_prices["Gasóleo Rodoviário"] == "1,323"
    assert replaced_gas_prices["Gasóleo Colorido e Marcado"] == "1,005"
