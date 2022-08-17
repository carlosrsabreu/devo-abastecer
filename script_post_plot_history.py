import pandas as pd

from constants import TWEET_HISTORY, CURRENT_GAS_HISTORY_PLOT, CURRENT_GAS_HISTORY_CSV_FILE, COLUMN_START_DATE
from post_tweet import post_image

# Get start and end dates
history = pd.read_csv(CURRENT_GAS_HISTORY_CSV_FILE)
start_date, end_date = history[COLUMN_START_DATE].min(), history[COLUMN_START_DATE].max()

# Post tweet with image
post_image(TWEET_HISTORY.format(start_date=start_date, end_date=end_date), CURRENT_GAS_HISTORY_PLOT)
