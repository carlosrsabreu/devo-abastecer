import locale
import tempfile

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

from constants import (
    CURRENT_GAS_HISTORY_CSV_FILE,
    CURRENT_GAS_HISTORY_PLOT_FILE,
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

locale.setlocale(locale.LC_ALL, "pt_PT.UTF-8")


def generate_plot_history(plot_path):
    history = pd.read_csv(CURRENT_GAS_HISTORY_CSV_FILE)
    history[COLUMN_START_DATE] = pd.to_datetime(history[COLUMN_START_DATE])
    history.set_index(COLUMN_START_DATE, inplace=True)

    # Select the last 6 months of data
    # history = history.last("6M").copy()

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

    # Save plot
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")

    return start_date, end_date, plot


# Generate history plot
start_date, end_date, _ = generate_plot_history(CURRENT_GAS_HISTORY_PLOT_FILE)
