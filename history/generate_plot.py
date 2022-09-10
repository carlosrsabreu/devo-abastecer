import locale

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

from constants import COLUMN_START_DATE, COLUMN_GASOLINA_IO95, COLUMN_GASOLINA_IO98, COLUMN_GASOLEO_RODOVIARIO, HISTORY_PLOT_LABEL_GASOLINA_IO95, HISTORY_PLOT_LABEL_GASOLINA_IO98, HISTORY_PLOT_LABEL_GASOLEO_RODOVIARIO, HISTORY_PLOT_Y_LABEL, HISTORY_PLOT_X_LABEL

locale.setlocale(locale.LC_ALL, 'pt_PT.UTF-8')


def generate_plot_history(history_file, plot_location):

    history = pd.read_csv(history_file)
    history[COLUMN_START_DATE] = pd.to_datetime(history[COLUMN_START_DATE])

    # Select the last 6 months of data
    history.set_index(COLUMN_START_DATE, inplace=True)
    history = history.last('6M').copy()

    plt.figure()
    ax = history.plot(y=[COLUMN_GASOLINA_IO95, COLUMN_GASOLINA_IO98, COLUMN_GASOLEO_RODOVIARIO],
                      label=[HISTORY_PLOT_LABEL_GASOLINA_IO95, HISTORY_PLOT_LABEL_GASOLINA_IO98, HISTORY_PLOT_LABEL_GASOLEO_RODOVIARIO], ylabel=HISTORY_PLOT_Y_LABEL, xlabel=HISTORY_PLOT_X_LABEL)

    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.3f'))
    plt.savefig(plot_location, dpi=300, bbox_inches='tight')
