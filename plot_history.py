import os
import locale
import tempfile

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

from constants import (
    TWEET_HISTORY,
    CURRENT_GAS_HISTORY_CSV_FILE,
    COLUMN_START_DATE,
    COLUMN_GASOLINA_IO95,
    COLUMN_GASOLINA_IO98,
    COLUMN_GASOLEO_RODOVIARIO,
    HISTORY_PLOT_LABEL_GASOLINA_IO95,
    HISTORY_PLOT_LABEL_GASOLINA_IO98,
    HISTORY_PLOT_LABEL_GASOLEO_RODOVIARIO,
    HISTORY_PLOT_Y_LABEL,
    HISTORY_PLOT_X_LABEL,
)
from post_tweet import post_image

locale.setlocale(locale.LC_ALL, "pt_PT.UTF-8")


def generate_plot_history():
    # Select the last 6 months of data
    history = pd.read_csv(CURRENT_GAS_HISTORY_CSV_FILE)
    history[COLUMN_START_DATE] = pd.to_datetime(history[COLUMN_START_DATE])
    history.set_index(COLUMN_START_DATE, inplace=True)
    history = history.last("6M").copy()

    # Get start and end dates
    start_date, end_date = history.index.min(), history.index.max()

    # Generate plot
    plt.figure()
    plot = history.plot(
        y=[COLUMN_GASOLINA_IO95, COLUMN_GASOLINA_IO98, COLUMN_GASOLEO_RODOVIARIO],
        label=[
            HISTORY_PLOT_LABEL_GASOLINA_IO95,
            HISTORY_PLOT_LABEL_GASOLINA_IO98,
            HISTORY_PLOT_LABEL_GASOLEO_RODOVIARIO,
        ],
        ylabel=HISTORY_PLOT_Y_LABEL,
        xlabel=HISTORY_PLOT_X_LABEL,
    )

    plot.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.3f"))

    # Save plot to history directory
    history_dir = os.path.join(os.getcwd(), "history")
    if not os.path.exists(history_dir):
        os.makedirs(history_dir)

    plot_path = os.path.join(history_dir, "fuel_history.png")
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")

    return start_date, end_date, plot_path


# Generate history plot
start_date, end_date, plot_path = generate_plot_history()

print("Fuel history plot saved at:", plot_path)
print("Start Date:", start_date)
print("End Date:", end_date)
