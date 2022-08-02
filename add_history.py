import json

from constants import CURRENT_GAS_HISTORY_JSON_FILE, CURRENT_WEEK, START_DATE_KEY, CURRENT_GAS_HISTORY_CSV_FILE, END_DATE_KEY, COLORED_DIESEL, GASOLINE_98, GASOLINE_95, DIESEL, GAS_KEY


def add_history(dict_prices):
    # JSON
    with open(CURRENT_GAS_HISTORY_JSON_FILE, 'r') as f:
        curret_data = json.load(f)
    with open(CURRENT_GAS_HISTORY_JSON_FILE, 'w') as f:
        curret_data[dict_prices[CURRENT_WEEK][START_DATE_KEY]] = dict_prices[CURRENT_WEEK]
        content = json.dumps(curret_data, indent=1, ensure_ascii=False)
        f.write(content)
    # CSV
    with open(CURRENT_GAS_HISTORY_CSV_FILE, 'a') as f:
        f.write(f'{dict_prices[CURRENT_WEEK][START_DATE_KEY]},{dict_prices[CURRENT_WEEK][END_DATE_KEY]},{dict_prices[CURRENT_WEEK][GAS_KEY][GASOLINE_95]},{dict_prices[CURRENT_WEEK][GAS_KEY][DIESEL]},{dict_prices[CURRENT_WEEK][GAS_KEY][COLORED_DIESEL]},{dict_prices[CURRENT_WEEK][GAS_KEY][GASOLINE_98]}\n')
