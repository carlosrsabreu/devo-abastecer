import locale
import logging
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import pandas as pd
import numpy as np
from scipy.interpolate import make_interp_spline

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

# Set locale for Portuguese date formatting
try:
    locale.setlocale(locale.LC_ALL, "pt_PT.UTF-8")
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, "pt_PT")
    except locale.Error:
        logging.warning("Portuguese locale not available. Using default.")


def generate_plot_history(plot_path):
    # Load history data
    history = pd.read_csv(CURRENT_GAS_HISTORY_CSV_FILE)
    history[COLUMN_START_DATE] = pd.to_datetime(history[COLUMN_START_DATE])
    history.set_index(COLUMN_START_DATE, inplace=True)
    history.sort_index(inplace=True)

    # Filter out any non-numeric or missing data for interpolation
    history = history.dropna(
        subset=[COLUMN_GASOLINA_IO95, COLUMN_GASOLINA_IO98, COLUMN_GASOLEO_RODOVIARIO]
    )

    # Clean, Modern Plot Design
    plt.style.use("default")

    # Create the figure
    fig, ax = plt.subplots(figsize=(14, 8), dpi=300, facecolor="#161B22")
    ax.set_facecolor("#161B22")

    # Provided palette: Vibrant Red (Primary), Royal Blue (Secondary), Emerald (Accent)
    colors = {
        COLUMN_GASOLINA_IO95: "#F85149",  # Primary: Vibrant Red
        COLUMN_GASOLINA_IO98: "#3B82F6",  # Secondary: Royal Blue
        COLUMN_GASOLEO_RODOVIARIO: "#10B981",  # Accent: Emerald Green
    }

    labels = {
        COLUMN_GASOLINA_IO95: HISTORY_PLOT_LABEL_GASOLINA_IO95,
        COLUMN_GASOLINA_IO98: HISTORY_PLOT_LABEL_GASOLINA_IO98,
        COLUMN_GASOLEO_RODOVIARIO: HISTORY_PLOT_LABEL_GASOLEO_RODOVIARIO,
    }

    columns_to_plot = [
        COLUMN_GASOLINA_IO95,
        COLUMN_GASOLINA_IO98,
        COLUMN_GASOLEO_RODOVIARIO,
    ]

    # Convert dates to numbers for interpolation
    x = history.index.map(pd.Timestamp.to_julian_date).values
    x_smooth = np.linspace(x.min(), x.max(), 500)

    # Plot each line with specific styling
    for col in columns_to_plot:
        if col in history.columns:
            y = history[col].values

            # Spline interpolation for smooth lines
            spl = make_interp_spline(x, y, k=3)
            y_smooth = spl(x_smooth)

            # Plot the smooth line
            ax.plot(
                pd.to_datetime(x_smooth, origin="julian", unit="D"),
                y_smooth,
                label=labels[col],
                color=colors[col],
                linewidth=2,
                alpha=1.0,
                zorder=3,
            )

            # Add markers at original data points (refined and small to keep the look clean)
            ax.scatter(
                history.index,
                y,
                color=colors[col],
                edgecolor="#161B22",
                linewidth=0.5,
                s=12,  # Refined size
                zorder=4,
                alpha=0.6,
            )

    # Title and Labels
    ax.set_title(
        "HISTÓRICO DE PREÇOS DE COMBUSTÍVEIS (MADEIRA)",
        fontsize=18,
        fontweight="bold",
        pad=30,
        color="#F0F6FC",
        alpha=0.9,
    )
    ax.set_ylabel(HISTORY_PLOT_Y_LABEL, fontsize=12, labelpad=15, color="#8B949E")
    ax.set_xlabel(HISTORY_PLOT_X_LABEL, fontsize=12, labelpad=15, color="#8B949E")

    # Formatting Y-axis
    ax.yaxis.set_major_formatter(mtick.FormatStrFormatter("%.3f€"))

    # Customize ticks and grid
    ax.tick_params(axis="both", which="major", labelsize=10, colors="#8B949E", length=0)
    ax.grid(True, linestyle="-", alpha=0.1, color="#484F58", zorder=0)

    # Remove top and right spines, and style others
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_color("#30363D")
    ax.spines["bottom"].set_linewidth(1)

    # Legend styling
    legend = ax.legend(
        loc="upper center",
        bbox_to_anchor=(0.5, -0.1),
        ncol=3,
        fontsize=10,
        frameon=False,
        handlelength=1.5,
    )
    for text in legend.get_texts():
        text.set_color("#F0F6FC")

    # Add source info at the bottom right
    plt.text(
        1.0,
        -0.12,
        "Fonte: JORAM | Devo Abastecer",
        transform=ax.transAxes,
        fontsize=9,
        color="#8B949E",
        ha="right",
        va="top",
    )

    # Adjust layout
    plt.tight_layout()

    # Save plot
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    plt.close(fig)

    start_date, end_date = history.index.min(), history.index.max()
    return start_date, end_date


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )
    try:
        start_date, end_date = generate_plot_history(CURRENT_GAS_HISTORY_PLOT_FILE)
        logging.info(
            f"Plot generated successfully for range: {start_date} to {end_date}"
        )
    except Exception as e:
        logging.error(f"Error generating history plot: {e}")
