import json

import requests as req
from bs4 import BeautifulSoup

from keys import *

# Requesting for the website
Web = req.get('https://www.madeira.gov.pt/drett')

# Creating a BeautifulSoup object and specifying the parser
S = BeautifulSoup(Web.text, 'html.parser')

# Find the id with gas info
spanWithGasInfo = S.find('span', {'id': 'dnn_ctr9883_View_D1_dlstInformacaoOne_Conteudo_0'})

# Get the text without html tags
gasInfo = spanWithGasInfo.get_text('\n', strip=True)
arr_info = gasInfo.split('\n')

# Parse the data
dict_prices = {}
last_id = 0
i = 0
while i < len(arr_info) - 1:
    # Get date
    add_date = i == 0 or arr_info[i].startswith(NEW_DATE_KEY)
    if arr_info[i].startswith(NEW_DATE_KEY):
        i += 1
        last_id += 1
    if add_date:
        start_date, end_date = arr_info[i].replace('.', '-').split('\xa0a ')
        dict_prices[last_id] = {START_DATE_KEY: start_date, END_DATE_KEY: end_date, GAS_KEY: []}
        i += 1
    # Gas information
    else:
        gas = arr_info[i]
        price = float(arr_info[i + 1][:-1].replace(',', '.'))
        dict_prices[last_id][GAS_KEY].append({GAS_NAME_KEY: gas, GAS_PRICE_KEY: price})
        i += 2

# Print the information
print(json.dumps(dict_prices, indent=1, ensure_ascii=False))
