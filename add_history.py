import json

from keys import NEXT_WEEK, START_DATE_KEY

# Get the last udate

with open('gas_info.json', encoding='utf-8') as f:
    next_week = json.load(f)[NEXT_WEEK]
    key_next_week = next_week[START_DATE_KEY]

# Get history
with open('gas_info_history.json', encoding='utf-8') as f:
    history_dict = json.load(f)
    history_dict[key_next_week] = next_week

# Print the information
print(json.dumps(history_dict, indent=1, ensure_ascii=False))
