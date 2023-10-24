import datetime

from constants import COLORED_DIESEL, DIESEL, GASOLINE_95


# We give a date, it returns the first and the last day of that week
def retrieve_week_by_date(date):
    start_of_the_week = date - datetime.timedelta(days=date.weekday())
    end_of_the_week = start_of_the_week + datetime.timedelta(days=6)
    return [
        start_of_the_week.strftime("%Y-%m-%d"),
        end_of_the_week.strftime("%Y-%m-%d"),
    ]


# We give a date, it returns the following week
def return_next_week_by_date(date):
    end_date = date + datetime.timedelta(weeks=1)
    return end_date


# Replace gas keys names. This function can be optimized
def replace_gas_keys_names(gas_prices):
    gas_prices[GASOLINE_95] = gas_prices.pop("Gasolina super sem chumbo IO 95")
    gas_prices[DIESEL] = gas_prices.pop("Gasóleo rodoviário")
    gas_prices[COLORED_DIESEL] = gas_prices.pop("Gasóleo colorido e marcado")
    return gas_prices
