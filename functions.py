import datetime
import re
import logging

from constants import (
    COLORED_DIESEL,
    DIESEL,
    GASOLINE_95,
    GASOLINE_98,
    CURRENT_WEEK,
    PREVIOUS_WEEK,
    START_DATE_KEY,
    END_DATE_KEY,
    GAS_KEY,
    DIESEL_TW,
    GASOLINE_95_TW,
    GASOLINE_98_TW,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


# We give a date, it returns the first and the last day of that week
def retrieve_week_by_date(date):
    if not isinstance(date, (datetime.date, datetime.datetime)):
        raise ValueError("Input must be a date or datetime object")
    start_of_the_week = date - datetime.timedelta(days=date.weekday())
    end_of_the_week = start_of_the_week + datetime.timedelta(days=6)
    return [
        start_of_the_week.strftime("%Y-%m-%d"),
        end_of_the_week.strftime("%Y-%m-%d"),
    ]


# We give a date, it returns the following week
def return_next_week_by_date(date):
    if not isinstance(date, (datetime.date, datetime.datetime)):
        raise ValueError("Input must be a date or datetime object")
    return date + datetime.timedelta(weeks=1)


# Replace gas keys names.
def replace_gas_keys_names(gas_prices):
    # Define a mapping of keys to their corresponding regular expression patterns
    key_patterns = {
        GASOLINE_95: re.compile(
            r"Gasolina\s*super\s*sem\s*chumbo\s*IO\s*95", re.IGNORECASE
        ),
        DIESEL: re.compile(r"Gasóleo\s*rodoviário", re.IGNORECASE),
        COLORED_DIESEL: re.compile(r"Gasóleo\s*colorido\s*e\s*marcado", re.IGNORECASE),
    }

    new_gas_prices = {}
    for target_key, pattern in key_patterns.items():
        # Find the matching key using the regular expression
        matching_key = next(
            (key for key in gas_prices.keys() if pattern.search(key)), None
        )

        if matching_key:
            # If a matching key is found, use it with the target key name
            new_gas_prices[target_key] = gas_prices[matching_key]
        else:
            logging.warning(f"{target_key} key not found in the dictionary.")

    return new_gas_prices


def get_gas_prices_message(price_current, price_previous):
    """
    Returns a formatted string comparing current and previous prices with an arrow indicator.
    """
    if price_current is None or price_previous is None:
        return "N/A"

    try:
        price_current = float(price_current)
        price_previous = float(price_previous)
    except (ValueError, TypeError):
        return f"{price_current}€   ?   {price_previous}€"

    if price_current > price_previous:
        return f"{price_current:.3f}€   ⬆️   {price_previous:.3f}€"
    if price_current < price_previous:
        return f"{price_current:.3f}€   ⬇️️   {price_previous:.3f}€"
    return f"{price_current:.3f}€   =   {price_previous:.3f}€"


def format_social_media_message(dict_prices):
    """
    Formats a consistent message for all social media platforms.
    """
    try:
        current = dict_prices[CURRENT_WEEK]
        previous = dict_prices[PREVIOUS_WEEK]

        message = "— Devo abastecer? ⛽️ \n\n"
        message += (
            f"         {current[START_DATE_KEY]}  |  {previous[START_DATE_KEY]}\n"
        )
        message += "                      a         |            a\n"
        message += f"         {current[END_DATE_KEY]}  |  {previous[END_DATE_KEY]}\n\n"

        # Helper to get price safely
        def get_p(d, k):
            return d.get(GAS_KEY, {}).get(k)

        message += f"{DIESEL_TW}{get_gas_prices_message(get_p(current, DIESEL), get_p(previous, DIESEL))}\n"
        message += f"{GASOLINE_95_TW}{get_gas_prices_message(get_p(current, GASOLINE_95), get_p(previous, GASOLINE_95))}\n"
        message += f"{GASOLINE_98_TW}{get_gas_prices_message(get_p(current, GASOLINE_98), get_p(previous, GASOLINE_98))}\n"

        return message
    except KeyError as e:
        logging.error(f"Error formatting message: missing key {e}")
        return None
