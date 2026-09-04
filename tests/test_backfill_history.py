import datetime

from copy import deepcopy
from unittest.mock import Mock

import backfill_history
from backfill_history import entry_complete, process_pdf
from constants import (
    GASOLINE_95,
    GASOLINE_98,
    DIESEL,
    COLORED_DIESEL,
    START_DATE_KEY,
    END_DATE_KEY,
    GAS_KEY,
    PDF_URL_KEY,
)

COMPLETE = {
    START_DATE_KEY: "2024-05-27",
    END_DATE_KEY: "2024-06-02",
    GAS_KEY: {GASOLINE_95: 1.751, DIESEL: 1.521, COLORED_DIESEL: 1.144, GASOLINE_98: 1.901},
    PDF_URL_KEY: "http://pdf",
}


def test_entry_complete():
    assert entry_complete(COMPLETE)
    assert not entry_complete(None)
    assert not entry_complete({})


def test_entry_complete_missing_fuel():
    missing = deepcopy(COMPLETE)
    del missing[GAS_KEY][GASOLINE_98]
    assert not entry_complete(missing)


def test_entry_complete_missing_pdf_url():
    missing = deepcopy(COMPLETE)
    missing[PDF_URL_KEY] = ""
    assert not entry_complete(missing)


def _patch_state(monkeypatch):
    monkeypatch.setattr(backfill_history, "all_history", {})
    monkeypatch.setattr(backfill_history, "new_entries_count", 0)


def test_process_pdf_adds_entry(monkeypatch):
    _patch_state(monkeypatch)
    monkeypatch.setattr(
        "joram.read_pdf_prices",
        lambda url: iter(
            [
                ("Gasolina super sem chumbo IO 95", "1,751"),
                ("Gasóleo rodoviário", "1,521"),
                ("Gasóleo colorido e marcado", "1,144"),
            ]
        ),
    )

    process_pdf(2024, "IISerie-1-2024-05-20.pdf", datetime.datetime(2024, 5, 20))

    entry = backfill_history.all_history["2024-05-27"]
    assert entry[START_DATE_KEY] == "2024-05-27"
    assert entry[END_DATE_KEY] == "2024-06-02"
    assert entry[GAS_KEY][GASOLINE_95] == 1.751
    assert entry[GAS_KEY][GASOLINE_98] == 1.901  # computed from 95 + 0.15
    assert entry[PDF_URL_KEY].endswith("IISerie-1-2024-05-20.pdf")
    assert backfill_history.new_entries_count == 1


def test_process_pdf_skips_complete_entry(monkeypatch):
    _patch_state(monkeypatch)
    monkeypatch.setattr(backfill_history, "all_history", {"2024-05-27": deepcopy(COMPLETE)})
    reader = Mock()
    monkeypatch.setattr("joram.read_pdf_prices", reader)

    process_pdf(2024, "IISerie-1-2024-05-20.pdf", datetime.datetime(2024, 5, 20))

    reader.assert_not_called()
    assert backfill_history.new_entries_count == 0