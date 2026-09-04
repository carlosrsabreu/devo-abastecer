import json
import logging
import os
from constants import (
    CURRENT_GAS_HISTORY_JSON_FILE,
    CURRENT_GAS_HISTORY_CSV_FILE,
    CURRENT_WEEK,
    START_DATE_KEY,
    END_DATE_KEY,
    GAS_KEY,
    PDF_URL_KEY,
    CSV_HEADER,
)
from functions import csv_row

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
        row = csv_row(
            start_date,
            end_date,
            gas_data,
            dict_prices[CURRENT_WEEK].get(PDF_URL_KEY, ""),
        )
        prefix = f"{start_date},"

        if os.path.exists(CURRENT_GAS_HISTORY_CSV_FILE):
            with open(CURRENT_GAS_HISTORY_CSV_FILE, "r") as f:
                lines = f.readlines()
            if any(line.startswith(prefix) for line in lines):
                # A same-week correction supersedes the existing row
                lines = [row if line.startswith(prefix) else line for line in lines]
                with open(CURRENT_GAS_HISTORY_CSV_FILE, "w") as f:
                    f.writelines(lines)
                logging.info(f"Updated entry for {start_date} in CSV history.")
                return
        else:
            # First time the CSV is created, add the header
            with open(CURRENT_GAS_HISTORY_CSV_FILE, "a") as f:
                f.write(CSV_HEADER)

        with open(CURRENT_GAS_HISTORY_CSV_FILE, "a") as f:
            f.write(row)
        logging.info(f"Added entry for {start_date} to CSV history.")
    except Exception as e:
        logging.error(f"Error updating CSV history: {e}")
