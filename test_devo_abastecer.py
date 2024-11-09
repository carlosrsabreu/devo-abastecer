import pytest
from unittest.mock import patch, MagicMock
import json
from update_gas_prices import fetch_html_content, parse_html_content, update_gas_info
from post_tweet import create_tweet_content, post_tweet
from add_history import add_to_history

# Mock data for testing
MOCK_HTML_CONTENT = """
<table>
    <tr><td>Gasolina 95</td><td>1.50</td></tr>
    <tr><td>Gasóleo</td><td>1.40</td></tr>
</table>
"""

MOCK_GAS_INFO = {"Gasolina 95": "1.50", "Gasóleo": "1.40"}


@pytest.fixture
def mock_requests_get():
    with patch("requests.get") as mock_get:
        mock_get.return_value.text = MOCK_HTML_CONTENT
        yield mock_get


def test_fetch_html_content(mock_requests_get):
    content = fetch_html_content()
    assert content == MOCK_HTML_CONTENT
    mock_requests_get.assert_called_once()


def test_parse_html_content():
    parsed_data = parse_html_content(MOCK_HTML_CONTENT)
    assert parsed_data == MOCK_GAS_INFO


@patch("update_gas_prices.load_gas_info")
@patch("update_gas_prices.save_gas_info")
def test_update_gas_info(mock_save, mock_load):
    mock_load.return_value = {"Gasolina 95": "1.45", "Gasóleo": "1.35"}
    updated = update_gas_info(MOCK_GAS_INFO)
    assert updated == True
    mock_save.assert_called_once_with(MOCK_GAS_INFO)


def test_create_tweet_content():
    old_prices = {"Gasolina 95": "1.45", "Gasóleo": "1.35"}
    new_prices = MOCK_GAS_INFO
    tweet_content = create_tweet_content(old_prices, new_prices)
    assert "Gasolina 95" in tweet_content
    assert "Gasóleo" in tweet_content
    assert "1.50" in tweet_content
    assert "1.40" in tweet_content


@patch("tweepy.API")
def test_post_tweet(mock_api):
    tweet_content = "Test tweet content"
    post_tweet(tweet_content)
    mock_api.return_value.update_status.assert_called_once_with(tweet_content)


@patch("json.dump")
@patch("csv.writer")
def test_add_to_history(mock_csv_writer, mock_json_dump):
    new_prices = MOCK_GAS_INFO
    add_to_history(new_prices)
    mock_json_dump.assert_called()
    mock_csv_writer.return_value.writerow.assert_called()


@pytest.mark.integration
def test_full_process_integration():
    with patch("update_gas_prices.fetch_html_content") as mock_fetch:
        mock_fetch.return_value = MOCK_HTML_CONTENT
        with patch("update_gas_prices.load_gas_info") as mock_load:
            mock_load.return_value = {"Gasolina 95": "1.45", "Gasóleo": "1.35"}
            with patch("update_gas_prices.save_gas_info") as mock_save:
                with patch("post_tweet.post_tweet") as mock_post:
                    with patch("add_history.add_to_history") as mock_add_history:
                        # Run the full process
                        from update_gas_prices import main as update_main

                        update_main()

                        # Assert that all steps were called
                        mock_fetch.assert_called_once()
                        mock_load.assert_called_once()
                        mock_save.assert_called_once()
                        mock_post.assert_called_once()
                        mock_add_history.assert_called_once()
