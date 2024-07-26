import json
import requests_mock
from unittest.mock import Mock, mock_open, patch

from src.utils import get_exchange_rates, get_load_user_setting, get_stock_prices


# Тесты для get_load_user_setting
def test_get_load_user_setting_success():
    mock_settings = {"user_currencies": ["USD", "EUR"]}
    with patch("builtins.open", mock_open(read_data=json.dumps(mock_settings))):
        settings = get_load_user_setting("dummy_path")
        assert settings == mock_settings


def test_get_load_user_setting_file_not_found():
    with patch("builtins.open", side_effect=FileNotFoundError):
        settings = get_load_user_setting("dummy_path")
        assert settings is None


def test_get_load_user_setting_other_exception():
    with patch("builtins.open", side_effect=Exception("Unexpected error")):
        settings = get_load_user_setting("dummy_path")
        assert settings is None


# Тесты для get_exchange_rates
@patch("src.utils.get_load_user_setting", return_value={"user_currencies": ["USD", "EUR"]})
@patch("src.utils.os.getenv", return_value="fake_api_key")
def test_get_exchange_rates(mock_getenv, mock_get_load_user_setting):
    with requests_mock.Mocker() as m:
        m.get(
            "https://api.apilayer.com/exchangerates_data/latest?symbols=USD,EUR&base=RUB",
            json={"rates": {"USD": 0.013, "EUR": 0.011}}
        )

        rates = get_exchange_rates()
        assert rates is not None
        assert len(rates) == 2
        assert rates[0]["currency"] == "USD"
        assert rates[0]["rate"] == 0.013
        assert rates[1]["currency"] == "EUR"
        assert rates[1]["rate"] == 0.011


@patch("src.utils.get_load_user_setting", return_value={"user_currencies": ["USD", "EUR"]})
@patch("src.utils.os.getenv", return_value=None)
def test_get_exchange_rates_no_api_key(mock_getenv, mock_get_load_user_setting):
    rates = get_exchange_rates()
    assert rates is None

# Тест для get_stock_prices
@patch("src.utils.get_load_user_setting", return_value={"user_stocks": ["AAPL", "GOOGL"]})
def test_get_stock_prices(mock_get_load_user_setting):
    api_key = "fake_api_key"
    date_str = "2021-07-01"

    with requests_mock.Mocker() as m:
        m.get(
            "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey=fake_api_key",
            json={
                "Time Series (Daily)": {
                    "2021-07-01": {"4. close": "145.11"},
                    "2021-06-30": {"4. close": "143.24"}
                }
            }
        )
        m.get(
            "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=GOOGL&apikey=fake_api_key",
            json={
                "Time Series (Daily)": {
                    "2021-07-01": {"4. close": "2700.00"},
                    "2021-06-30": {"4. close": "2680.00"}
                }
            }
        )
        prices = get_stock_prices(api_key, "settings.json", date_str)
        assert prices is not None
        assert len(prices) == 2
        assert prices[0]["stock"] == "AAPL"
        assert prices[0]["price"] == 145.11
        assert prices[1]["stock"] == "GOOGL"
        assert prices[1]["price"] == 2700.00