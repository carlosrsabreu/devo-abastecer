import json
import logging
from add_history import add_history
from constants import (
    CURRENT_GAS_INFO_FILE,
    START_DATE_KEY,
    END_DATE_KEY,
    GAS_KEY,
    PREVIOUS_WEEK,
    CURRENT_WEEK,
    GASOLINE_98,
    GASOLINE_95,
    DIFFERENCE_95_98_PRICE,
    PDF_URL_KEY,
)

from post_bsky import make_bsky_post
from post_tweet import make_tweet
from post_facebook import make_facebook_post
from joram import retrieve_newest_pdf_gas_info
from functions import retrieve_week_by_date, return_next_week_by_date

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main():
    try:
        # Get current data to check if there is an update
        with open(CURRENT_GAS_INFO_FILE) as f:
            current_data = json.load(f)
            current_start_date_saved = current_data[CURRENT_WEEK][START_DATE_KEY]
            current_end_date_saved = current_data[CURRENT_WEEK][END_DATE_KEY]
    except (FileNotFoundError, json.JSONDecodeError, KeyError) as e:
        logging.error(f"Error reading current gas info file: {e}")
        return

    # Retrieve gas prices and creation date
    pdf_info = retrieve_newest_pdf_gas_info()
    if not pdf_info:
        logging.info("No new PDF information found.")
        return

    gas_info = pdf_info.get("gas_info")
    creation_date = pdf_info.get("creation_date")
    pdf_url = pdf_info.get("pdf_url")

    if not gas_info or not creation_date or not pdf_url:
        logging.error("Incomplete PDF information retrieved.")
        return

    logging.debug(f"gas_info = {gas_info}")
    logging.debug(f"creation_date = {creation_date}")

    # Retrieve week by creation date of the PDF
    try:
        start_date, end_date = retrieve_week_by_date(
            return_next_week_by_date(creation_date)
        )
    except Exception as e:
        logging.error(f"Error calculating dates: {e}")
        return

    # Check if we already have this date
    update = (
        start_date != current_start_date_saved or end_date != current_end_date_saved
    )

    # If we don't have the date, update
    if update:
        logging.info(f"New update found for week {start_date} to {end_date}")
        # Prepare the dictionary
        dict_prices = {
            PREVIOUS_WEEK: current_data[CURRENT_WEEK],
            CURRENT_WEEK: {
                START_DATE_KEY: start_date,
                END_DATE_KEY: end_date,
                GAS_KEY: {},
                PDF_URL_KEY: pdf_url,
            },
        }

        # Parse the data
        for key, value in gas_info.items():
            try:
                price = float(value.replace(",", "."))
                dict_prices[CURRENT_WEEK][GAS_KEY][key] = price
            except (ValueError, AttributeError) as e:
                logging.error(f"Error parsing price for {key}: {value}. Error: {e}")
                continue

        # Add Gasoline 98 price
        if GASOLINE_95 in dict_prices[CURRENT_WEEK][GAS_KEY]:
            dict_prices[CURRENT_WEEK][GAS_KEY][GASOLINE_98] = round(
                dict_prices[CURRENT_WEEK][GAS_KEY][GASOLINE_95]
                + DIFFERENCE_95_98_PRICE,
                3,
            )
        else:
            logging.warning("Gasoline 95 not found, cannot calculate Gasoline 98.")

        # Make posts
        make_tweet(dict_prices)
        make_bsky_post(dict_prices)
        make_facebook_post(dict_prices)

        # Add history
        try:
            add_history(dict_prices)
        except Exception as e:
            logging.error(f"Error adding history: {e}")

        # Writing JSON file
        try:
            content = json.dumps(dict_prices, indent=1, ensure_ascii=False)
            with open(CURRENT_GAS_INFO_FILE, "w") as f:
                f.write(content)
            logging.info(f"Updated {CURRENT_GAS_INFO_FILE} successfully.")
        except Exception as e:
            logging.error(f"Error writing to {CURRENT_GAS_INFO_FILE}: {e}")
    else:
        logging.info("Already up to date. No update needed.")


if __name__ == "__main__":
    main()
