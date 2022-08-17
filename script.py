import datetime
import json

import requests as req
from bs4 import BeautifulSoup

from add_history import add_history
from constants import CURRENT_GAS_INFO_FILE, START_DATE_KEY, ENDPOINT, SPAN_ID, NEW_DATE_KEY, END_DATE_KEY, GAS_KEY, PREVIOUS_WEEK, CURRENT_WEEK, GASOLINE_98, GASOLINE_95, DIFFERENCE_95_98_PRICE, CURRENT_GAS_HISTORY_CSV_FILE, CURRENT_GAS_HISTORY_PLOT
from history.generate_plot import generate_plot_history
from post_tweet import make_tweet

# Get current data there is an update
with open(CURRENT_GAS_INFO_FILE) as f:
    curret_data = json.load(f)
    last_start_date_saved = curret_data[CURRENT_WEEK][START_DATE_KEY]

# Assumes that we need to update the file
update = True

# Requesting for the website
web = req.get(ENDPOINT)

# Creating a BeautifulSoup object and specifying the parser
s = BeautifulSoup(web.text, 'html.parser')

# Find the id with gas info
span_with_gas_info = s.find('span', {'id': SPAN_ID})

# Get the text without html tags
gas_info = span_with_gas_info.get_text('\n', strip=True).split('\n')

# Parse the data
dict_prices = {}
last_key = PREVIOUS_WEEK
i = 0
while i < len(gas_info) - 1:
    # Get date
    add_date = i == 0 or gas_info[i].startswith(NEW_DATE_KEY)
    if gas_info[i].startswith(NEW_DATE_KEY):
        i += 1
        last_key = CURRENT_WEEK
    if add_date:
        try:
            start_date, end_date = gas_info[i].replace('.', '-').split('\xa0a ')
        except Exception:
            start_date, end_date = gas_info[i].replace('.', '-').split(' a ')
        # Parse date
        start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y').strftime('%Y-%m-%d')
        # Check if we already have this data
        if start_date == last_start_date_saved:
            update = False
            break
        end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y').strftime('%Y-%m-%d')
        dict_prices[last_key] = {START_DATE_KEY: start_date, END_DATE_KEY: end_date, GAS_KEY: {}}
        i += 1
    # Gas information
    else:
        gas = gas_info[i]
        price = float(gas_info[i + 1][:-1].replace(',', '.'))
        dict_prices[last_key][GAS_KEY][gas] = price
        i += 2

# If necessary, update the JSON file, save history and save make tweet
if update:
    # Add Gasoline 98 price
    dict_prices[PREVIOUS_WEEK][GAS_KEY][GASOLINE_98] = round(dict_prices[PREVIOUS_WEEK][GAS_KEY][GASOLINE_95] + DIFFERENCE_95_98_PRICE, 3)
    dict_prices[CURRENT_WEEK][GAS_KEY][GASOLINE_98] = round(dict_prices[CURRENT_WEEK][GAS_KEY][GASOLINE_95] + DIFFERENCE_95_98_PRICE, 3)
    # Make tweet
    make_tweet(dict_prices)
    # Add history
    add_history(dict_prices)
    # Generate history plot
    generate_plot_history(CURRENT_GAS_HISTORY_CSV_FILE, CURRENT_GAS_HISTORY_PLOT)
    # Writing JSON file
    content = json.dumps(dict_prices, indent=1, ensure_ascii=False)
    with open(CURRENT_GAS_INFO_FILE, 'w') as f:
        f.write(content)
