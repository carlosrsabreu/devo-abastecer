import json
import logging
from constants import (
    CURRENT_GAS_HISTORY_JSON_FILE,
    CURRENT_WEEK,
    START_DATE_KEY,
    CURRENT_GAS_HISTORY_CSV_FILE,
    END_DATE_KEY,
    COLORED_DIESEL,
    GASOLINE_98,
    GASOLINE_95,
    DIESEL,
    GAS_KEY,
)

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def add_history(dict_prices):
    """
    Add new prices to the JSON and CSV history files.
    """
    start_date = dict_prices[CURRENT_WEEK][START_DATE_KEY]
    end_date = dict_prices[CURRENT_WEEK][END_DATE_KEY]
    gas_data = dict_prices[CURRENT_WEEK][GAS_KEY]

    # Add to JSON history
    try:
        with open(CURRENT_GAS_HISTORY_JSON_FILE, "r") as f:
            history_data = json.load(f)

        history_data[start_date] = dict_prices[CURRENT_WEEK]

        with open(CURRENT_GAS_HISTORY_JSON_FILE, "w") as f:
            json.dump(history_data, f, indent=1, ensure_ascii=False)
        logging.info(f"Added entry for {start_date} to JSON history.")
    except Exception as e:
        logging.error(f"Error updating JSON history: {e}")

    # Add to CSV history
    try:
        # Check if the start_date already exists in the CSV to avoid duplicates
        date_exists = False
        try:
            with open(CURRENT_GAS_HISTORY_CSV_FILE, "r") as f:
                for line in f:
                    if line.startswith(start_date):
                        date_exists = True
                        break
        except FileNotFoundError:
            # If CSV doesn't exist, we will create it (though we assume it exists with a header)
            pass

        if not date_exists:
            with open(CURRENT_GAS_HISTORY_CSV_FILE, "a") as f:
                # Ensure all required keys are in gas_data, use 0 or None if not
                p95 = gas_data.get(GASOLINE_95, "")
                diesel = gas_data.get(DIESEL, "")
                colored = gas_data.get(COLORED_DIESEL, "")
                p98 = gas_data.get(GASOLINE_98, "")

                f.write(f"{start_date},{end_date},{p95},{diesel},{colored},{p98}\n")
            logging.info(f"Added entry for {start_date} to CSV history.")
        else:
            logging.info(f"Entry for {start_date} already exists in CSV history.")
    except Exception as e:
        logging.error(f"Error updating CSV history: {e}")
