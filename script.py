import datetime
import json

import requests as req
from bs4 import BeautifulSoup

from add_history import add_history
from constants import CURRENT_GAS_INFO_FILE, START_DATE_KEY, ENDPOINT, SPAN_ID, NEW_DATE_KEY, END_DATE_KEY, GAS_KEY, PREVIOUS_WEEK, CURRENT_WEEK, GASOLINE_98, GASOLINE_95, DIFFERENCE_95_98_PRICE
from post_tweet import make_tweet

# Get current data to check if there is an update
with open(CURRENT_GAS_INFO_FILE) as f:
    curret_data = json.load(f)
    current_start_date_saved = curret_data[CURRENT_WEEK][START_DATE_KEY]
    current_end_date_saved = curret_data[CURRENT_WEEK][END_DATE_KEY]

# Requesting for the website
web = req.get(ENDPOINT)

# Creating a BeautifulSoup object and specifying the parser
s = BeautifulSoup(web.text, 'html.parser')

# Find the id with gas info
span_with_gas_info = s.find('span', {'id': SPAN_ID})

# Get the text without html tags
gas_info = span_with_gas_info.get_text('\n', strip=True).split('\n')

# Obtain the date positons in the request
date_positions = []
i = 0
while i < len(gas_info):
    if i == 0 or gas_info[i].startswith(NEW_DATE_KEY):
        date_positions.append(i)
    i += 1

# Parse the last available date
i = date_positions[-1]
try:
    start_date, end_date = gas_info[i].replace('.', '-').split('\xa0a ')
except Exception:
    start_date, end_date = gas_info[i].replace('.', '-').split(' a ')
start_date = datetime.datetime.strptime(start_date, '%d-%m-%Y').strftime('%Y-%m-%d')
end_date = datetime.datetime.strptime(end_date, '%d-%m-%Y').strftime('%Y-%m-%d')

# Check if we already have this date
update = start_date != current_start_date_saved and end_date != current_end_date_saved

# If we don't have the date, update
if update:
    # Prepare the dictionaire
    dict_prices = {PREVIOUS_WEEK: curret_data[CURRENT_WEEK]}
    dict_prices[CURRENT_WEEK] = {START_DATE_KEY: start_date, END_DATE_KEY: end_date, GAS_KEY: {}}
    # Parse the data
    i += 1
    while i < len(gas_info) - 1:
        gas = gas_info[i]
        price = float(gas_info[i + 1][:-1].replace(',', '.'))
        dict_prices[CURRENT_WEEK][GAS_KEY][gas] = price
        i += 2
    # Add Gasoline 98 price
    dict_prices[CURRENT_WEEK][GAS_KEY][GASOLINE_98] = round(dict_prices[CURRENT_WEEK][GAS_KEY][GASOLINE_95] + DIFFERENCE_95_98_PRICE, 3)
    # Make tweet
    make_tweet(dict_prices)
    # Add history
    add_history(dict_prices)
    # Writing JSON file
    content = json.dumps(dict_prices, indent=1, ensure_ascii=False)
    with open(CURRENT_GAS_INFO_FILE, 'w') as f:
        f.write(content)
