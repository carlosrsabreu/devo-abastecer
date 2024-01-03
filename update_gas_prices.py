import json

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
)

from post_tweet import make_tweet
from joram import retrieve_newest_pdf_gas_info
from functions import retrieve_week_by_date, return_next_week_by_date

# Get current data to check if there is an update
with open(CURRENT_GAS_INFO_FILE) as f:
    current_data = json.load(f)
    current_start_date_saved = current_data[CURRENT_WEEK][START_DATE_KEY]
    current_end_date_saved = current_data[CURRENT_WEEK][END_DATE_KEY]

# Retrieve gas prices and creation date
pdf_info = retrieve_newest_pdf_gas_info()
print("🐞Debug: pdf_info =", pdf_info, "\n")
gas_info = pdf_info["gas_info"]
print("🐞Debug: gas_info =", gas_info, "\n")
creation_date = pdf_info["creation_date"]
print("🐞Debug: creation_date =", creation_date, "\n")

# Retrieve week by creation date of the PDF
start_date, end_date = retrieve_week_by_date(return_next_week_by_date(creation_date))


# Check if we already have this date
update = start_date != current_start_date_saved and end_date != current_end_date_saved

# If we don't have the date, update
if update:
    # Prepare the dictionaire
    dict_prices = {
        PREVIOUS_WEEK: current_data[CURRENT_WEEK],
        CURRENT_WEEK: {
            START_DATE_KEY: start_date,
            END_DATE_KEY: end_date,
            GAS_KEY: gas_info,
        },
    }

    # Parse the data
    for key, value in gas_info.items():
        price = None
        # skip to next line in case fuelPrice is not a float
        while price is None:
            try:
                price = float(value.replace(",", "."))
            except ValueError:
                continue

        dict_prices[CURRENT_WEEK][GAS_KEY][key] = price

    # Add Gasoline 98 price
    dict_prices[CURRENT_WEEK][GAS_KEY][GASOLINE_98] = round(
        dict_prices[CURRENT_WEEK][GAS_KEY][GASOLINE_95] + DIFFERENCE_95_98_PRICE, 3
    )

    # Make tweet
    make_tweet(dict_prices)
    # Add history
    add_history(dict_prices)
    # Writing JSON file
    content = json.dumps(dict_prices, indent=1, ensure_ascii=False)
    with open(CURRENT_GAS_INFO_FILE, "w") as f:
        f.write(content)
