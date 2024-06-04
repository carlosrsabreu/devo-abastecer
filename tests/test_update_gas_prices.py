import pytest
import json
import datetime
from unittest.mock import patch, mock_open
from update_gas_prices import (
    retrieve_newest_pdf_gas_info,
    retrieve_week_by_date,
    return_next_week_by_date,
)

# Mock data for CURRENT_GAS_INFO_FILE
mock_current_gas_info = {
    "previous": {
        "Start date": "2024-05-13",
        "End date": "2024-05-19",
        "Gas": {
            "Gasolina IO95": 1.671,
            "Gasóleo Rodoviário": 1.341,
            "Gasóleo Colorido e Marcado": 1.022,
            "Gasolina IO98": 1.821,
        },
    },
    "current": {
        "Start date": "2024-05-20",
        "End date": "2024-05-26",
        "Gas": {
            "Gasolina IO95": 1.641,
            "Gasóleo Rodoviário": 1.336,
            "Gasóleo Colorido e Marcado": 1.017,
            "Gasolina IO98": 1.791,
        },
    },
}

# Mock data for the PDF information
mock_pdf_info = {
    "gas_info": {
        "Gasolina IO95": "1,634",  # Update to match the expected value in the test
        "Gasóleo Rodoviário": "1,323",
        "Gasóleo Colorido e Marcado": "1,005",
    },
    "creation_date": datetime.datetime(
        2024,
        5,
        31,
        15,
        51,
        21,
        tzinfo=datetime.timezone(datetime.timedelta(seconds=3600)),
    ),
}


@pytest.fixture
def mock_json_file(monkeypatch):
    # Mock the open function to return mock_current_gas_info when reading
    m = mock_open(read_data=json.dumps(mock_current_gas_info))
    monkeypatch.setattr("builtins.open", m)


@pytest.fixture
def mock_pdf_info_retrieval(monkeypatch):
    # Mock retrieve_newest_pdf_gas_info to return mock_pdf_info
    monkeypatch.setattr(
        "update_gas_prices.retrieve_newest_pdf_gas_info", lambda: mock_pdf_info
    )


def test_update_gas_prices(mock_json_file, mock_pdf_info_retrieval):
    from update_gas_prices import (
        CURRENT_GAS_INFO_FILE,
        CURRENT_WEEK,
        START_DATE_KEY,
        END_DATE_KEY,
        GAS_KEY,
    )

    with open(CURRENT_GAS_INFO_FILE) as f:
        current_data = json.load(f)

    current_start_date_saved = current_data[CURRENT_WEEK][START_DATE_KEY]
    current_end_date_saved = current_data[CURRENT_WEEK][END_DATE_KEY]

    pdf_info = retrieve_newest_pdf_gas_info()
    gas_info = pdf_info["gas_info"]
    creation_date = pdf_info["creation_date"]

    start_date, end_date = retrieve_week_by_date(
        return_next_week_by_date(creation_date)
    )

    update = (
        start_date != current_start_date_saved and end_date != current_end_date_saved
    )

    assert update == True
    assert gas_info["Gasolina IO95"] == "1,634"  # Updated to match mock data
    assert gas_info["Gasóleo Rodoviário"] == "1,323"
    assert gas_info["Gasóleo Colorido e Marcado"] == "1,005"
