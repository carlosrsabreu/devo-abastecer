import json

from add_history import add_history
from constants import (
    CURRENT_WEEK,
    START_DATE_KEY,
    END_DATE_KEY,
    GAS_KEY,
    GASOLINE_95,
    GASOLINE_98,
    DIESEL,
    COLORED_DIESEL,
    PDF_URL_KEY,
)


def sample_week():
    return {
        CURRENT_WEEK: {
            START_DATE_KEY: "2024-05-27",
            END_DATE_KEY: "2024-06-02",
            GAS_KEY: {
                GASOLINE_95: 1.751,
                DIESEL: 1.521,
                COLORED_DIESEL: 1.144,
                GASOLINE_98: 1.901,
            },
            PDF_URL_KEY: "http://pdf",
        }
    }


def _files(tmp_path, monkeypatch):
    json_file = tmp_path / "history.json"
    csv_file = tmp_path / "history.csv"
    json_file.write_text("{}")
    csv_file.write_text("start_date,end_date,p95,diesel,colorido,p98,url\n")
    monkeypatch.setattr("add_history.CURRENT_GAS_HISTORY_JSON_FILE", str(json_file))
    monkeypatch.setattr("add_history.CURRENT_GAS_HISTORY_CSV_FILE", str(csv_file))
    return json_file, csv_file


def test_add_history_writes_json_and_csv(tmp_path, monkeypatch):
    json_file, csv_file = _files(tmp_path, monkeypatch)

    add_history(sample_week())

    history = json.loads(json_file.read_text())
    assert "2024-05-27" in history
    assert history["2024-05-27"][GAS_KEY][GASOLINE_95] == 1.751
    assert history["2024-05-27"][PDF_URL_KEY] == "http://pdf"

    rows = csv_file.read_text().splitlines()
    assert rows[-1] == "2024-05-27,2024-06-02,1.751,1.521,1.144,1.901,http://pdf"


def test_add_history_does_not_duplicate_csv_entry(tmp_path, monkeypatch):
    json_file, csv_file = _files(tmp_path, monkeypatch)

    add_history(sample_week())
    add_history(sample_week())

    assert csv_file.read_text().count("2024-05-27,") == 1


def test_add_history_creates_missing_csv(tmp_path, monkeypatch):
    json_file = tmp_path / "history.json"
    json_file.write_text("{}")
    csv_file = tmp_path / "history.csv"
    monkeypatch.setattr("add_history.CURRENT_GAS_HISTORY_JSON_FILE", str(json_file))
    monkeypatch.setattr("add_history.CURRENT_GAS_HISTORY_CSV_FILE", str(csv_file))

    add_history(sample_week())

    # Append-only, matching the existing implementation: no header is written
    assert csv_file.read_text() == "2024-05-27,2024-06-02,1.751,1.521,1.144,1.901,http://pdf\n"