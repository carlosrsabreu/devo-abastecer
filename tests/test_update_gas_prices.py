import datetime
import json

from unittest.mock import Mock

from update_gas_prices import main
from constants import (
    CURRENT_WEEK,
    PREVIOUS_WEEK,
    START_DATE_KEY,
    END_DATE_KEY,
    GAS_KEY,
    GASOLINE_95,
    GASOLINE_98,
    DIESEL,
    COLORED_DIESEL,
    PDF_URL_KEY,
)


def _initial_info(path, start="2024-05-20", end="2024-05-26"):
    path.write_text(
        json.dumps(
            {
                CURRENT_WEEK: {
                    START_DATE_KEY: start,
                    END_DATE_KEY: end,
                    GAS_KEY: {
                        GASOLINE_95: 1.8,
                        DIESEL: 1.5,
                        COLORED_DIESEL: 1.1,
                        GASOLINE_98: 1.95,
                    },
                    PDF_URL_KEY: "http://old.pdf",
                }
            }
        )
    )


def _patch_env(monkeypatch, tmp_path):
    info_path = tmp_path / "gas_info.json"
    _initial_info(info_path)
    monkeypatch.setattr("update_gas_prices.CURRENT_GAS_INFO_FILE", str(info_path))

    mocks = {
        "retrieve_newest_pdf_gas_info": Mock(return_value=None),
        "make_tweet": Mock(),
        "make_bsky_post": Mock(),
        "make_facebook_post": Mock(),
        "add_history": Mock(),
    }
    for name, mock in mocks.items():
        monkeypatch.setattr(f"update_gas_prices.{name}", mock)
    return info_path, mocks


def test_main_updates_and_computes_gasoline_98(monkeypatch, tmp_path):
    info_path, mocks = _patch_env(monkeypatch, tmp_path)
    mocks["retrieve_newest_pdf_gas_info"].return_value = {
        "gas_info": {
            GASOLINE_95: "1,751",
            DIESEL: "1,521",
            COLORED_DIESEL: "1,144",
        },
        "creation_date": datetime.datetime(2024, 5, 24),
        "pdf_url": "http://new.pdf",
    }

    main()

    for name in ("make_tweet", "make_bsky_post", "make_facebook_post", "add_history"):
        assert mocks[name].called

    new_data = json.loads(info_path.read_text())
    current = new_data[CURRENT_WEEK]
    assert current[START_DATE_KEY] == "2024-05-27"
    assert current[END_DATE_KEY] == "2024-06-02"
    assert current[GAS_KEY][GASOLINE_95] == 1.751
    assert current[GAS_KEY][GASOLINE_98] == 1.901  # 1.751 + 0.15
    assert current[PDF_URL_KEY] == "http://new.pdf"
    assert new_data[PREVIOUS_WEEK][START_DATE_KEY] == "2024-05-20"


def test_main_skips_when_already_up_to_date(monkeypatch, tmp_path):
    info_path, mocks = _patch_env(monkeypatch, tmp_path)
    mocks["retrieve_newest_pdf_gas_info"].return_value = {
        "gas_info": {
            GASOLINE_95: "1,751",
            DIESEL: "1,521",
            COLORED_DIESEL: "1,144",
        },
        "creation_date": datetime.datetime(2024, 5, 17),  # week of 05-20..05-26
        "pdf_url": "http://old.pdf",
    }

    main()

    for name in ("make_tweet", "make_bsky_post", "make_facebook_post", "add_history"):
        assert not mocks[name].called
    assert (
        json.loads(info_path.read_text())[CURRENT_WEEK][START_DATE_KEY] == "2024-05-20"
    )


def test_main_returns_when_no_pdf_info(monkeypatch, tmp_path):
    info_path, mocks = _patch_env(monkeypatch, tmp_path)
    mocks["retrieve_newest_pdf_gas_info"].return_value = None

    assert main() is None
    for name in ("make_tweet", "make_bsky_post", "make_facebook_post", "add_history"):
        assert not mocks[name].called


def test_main_reposts_same_week_correction(monkeypatch, tmp_path):
    info_path, mocks = _patch_env(monkeypatch, tmp_path)
    mocks["retrieve_newest_pdf_gas_info"].return_value = {
        "gas_info": {
            GASOLINE_95: "1,751",
            DIESEL: "1,521",
            COLORED_DIESEL: "1,144",
        },
        "creation_date": datetime.datetime(2024, 5, 17),  # same week as saved
        "pdf_url": "http://corrected.pdf",
    }

    main()

    for name in ("make_tweet", "make_bsky_post", "make_facebook_post", "add_history"):
        assert mocks[name].called
    new_data = json.loads(info_path.read_text())
    assert new_data[CURRENT_WEEK][START_DATE_KEY] == "2024-05-20"
    assert new_data[CURRENT_WEEK][PDF_URL_KEY] == "http://corrected.pdf"


def test_main_returns_when_info_file_missing(tmp_path, monkeypatch):
    missing_path = tmp_path / "missing.json"
    mocks = {
        "retrieve_newest_pdf_gas_info": Mock(return_value=None),
        "make_tweet": Mock(),
        "make_bsky_post": Mock(),
        "make_facebook_post": Mock(),
        "add_history": Mock(),
    }
    monkeypatch.setattr("update_gas_prices.CURRENT_GAS_INFO_FILE", str(missing_path))
    for name, mock in mocks.items():
        monkeypatch.setattr(f"update_gas_prices.{name}", mock)

    assert main() is None
    assert not mocks["make_tweet"].called
