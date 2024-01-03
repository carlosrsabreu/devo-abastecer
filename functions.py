import datetime
import re

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
    # Define a mapping of keys to their corresponding regular expression patterns
    key_patterns = {
        GASOLINE_95: re.compile(r"Gasolina\s*super\s*sem\s*chumbo\s*IO\s*95"),
        DIESEL: re.compile(r"Gasóleo\s*rodoviário"),
        COLORED_DIESEL: re.compile(r"Gasóleo\s*colorido\s*e\s*marcado"),
    }

    for target_key, pattern in key_patterns.items():
        # Find the matching key using the regular expression
        matching_key = next(
            (key for key in gas_prices.keys() if pattern.match(key)), None
        )

        if matching_key:
            # If a matching key is found, replace it
            gas_prices[target_key] = gas_prices.pop(matching_key)
        else:
            print(f"Error: {target_key} key not found in the dictionary.")

    return gas_prices
