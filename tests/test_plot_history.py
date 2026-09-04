from pathlib import Path

from plot_history import generate_plot_history

CSV = (
    "start_date,end_date,gasolina_IO95,gasoleo_rodoviario,gasoleo_colorido_marcado,"
    "gasolina_IO98,pdf_url\n"
    "2024-05-27,2024-06-02,1.751,1.521,1.144,1.901,http://pdf\n"
    "2024-06-03,2024-06-09,1.771,1.531,1.154,1.921,http://pdf\n"
)


def test_generate_plot_history_renders(tmp_path, monkeypatch):
    csv_file = tmp_path / "history.csv"
    csv_file.write_text(CSV)
    monkeypatch.setattr("plot_history.CURRENT_GAS_HISTORY_CSV_FILE", str(csv_file))

    plot_path = tmp_path / "plot.png"
    start, end = generate_plot_history(str(plot_path))

    assert Path(plot_path).exists()
    assert Path(plot_path).stat().st_size > 0
    assert str(start.date()) == "2024-05-27"
    assert str(end.date()) == "2024-06-03"
