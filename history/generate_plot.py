import locale

import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd

locale.setlocale(locale.LC_ALL, 'pt_PT.UTF-8')


def generate_plot_history():
    # Read history
    history = pd.read_csv('gas_info_history.csv')

    # Convert start dates and end dates to datatime
    history['start_date'] = pd.to_datetime(history['start_date'])
    history['end_date'] = pd.to_datetime(history['end_date'])

    # Plot
    plt.figure()
    ax = history.plot(x='start_date', y=['gasolina_IO95', 'gasolina_IO98', 'gasoleo_rodoviario'],
                      label=['Gasolina IO95', 'Gasolina IO98', 'Gasóleo Rodoviário'], ylabel='Preço (€)', xlabel='Data')

    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter('%.3f'))
    plt.savefig('img/plot.png', dpi=300, bbox_inches='tight')
