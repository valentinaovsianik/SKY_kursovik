import pytest
import json
import os
import requests
from unittest.mock import patch, Mock, mock_open
from requests.exceptions import RequestException

from src.utils import get_load_user_setting, get_exchange_rates, get_stock_prices

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
@pytest.fixture
def mock_env_vars():
    """Фикстура для установки переменной окружения API_KEY"""
    with patch.dict("os.environ", {"API_KEY": "test_api_key"}):
        yield


def test_get_exchange_rates_success(mock_env_vars):
    """Тест успешного получения данных о курсах валют"""
    # Создаем mock для requests.get
    with patch("requests.get") as mock_get:
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.json = Mock(return_value={"rates": {"USD": 1.23}})
        mock_get.return_value = mock_response

        result = get_exchange_rates()

        expected_result = [{"currency": "USD", "rate": 1.23}]
        assert result == expected_result


def test_get_exchange_rates_no_api_key():
    """Тест отсутствия API-ключа."""
    # Создаем mock для функции get_load_user_setting
    with patch("src.utils.get_load_user_setting", return_value={"user_currencies": ["USD"]}), \
            patch("os.getenv", return_value=None):
        result = get_exchange_rates()
        assert result is None


def test_get_exchange_rates_request_error(mock_env_vars):
    """Тест на случай ошибки запроса"""
    # Создаем mock для requests.get
    with patch("requests.get") as mock_get:
        mock_get.side_effect = RequestException("Connection error")
        result = get_exchange_rates()
        assert result is None


# Тесты для get_stock_prices
# Функция для создания mock настроек пользователя
def mock_get_load_user_setting_success(settings_file):
    return {"user_stocks": ["AAPL", "MSFT"]}

def mock_get_load_user_setting_fail(settings_file):
    return None

# Фикстура для установки переменной окружения API_KEY
@pytest.fixture
def set_env_api_key(monkeypatch):
    monkeypatch.setenv("API_KEY", "test_api_key")

# Фикстура для создания временного файла настроек
@pytest.fixture
def mock_settings_file(tmp_path):
    settings = {"user_stocks": ["AAPL", "MSFT"]}
    settings_file = tmp_path / "test_settings.json"
    with open(settings_file, "w") as f:
        json.dump(settings, f)
    return str(settings_file)

def test_get_stock_prices_success(set_env_api_key, mock_settings_file):
    """Тест успешного получения цен акций"""
    api_key = os.getenv("API_KEY")
    date = "2024-07-22"
    settings_file = mock_settings_file

    # Mock ответ от API
    def mock_requests_get(url, params):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Time Series (Daily)": {
                "2024-07-22": {"4. close": "150.00"},
                "2024-07-21": {"4. close": "145.00"}
            }
        }
        return mock_response

    with patch("src.utils.get_load_user_setting", side_effect=mock_get_load_user_setting_success):
        with patch("requests.get", side_effect=mock_requests_get):
            result = get_stock_prices(api_key, settings_file, date)
            expected_result = {"AAPL": "150.00", "MSFT": "150.00"}
            assert result == expected_result

def test_get_stock_prices_no_user_settings(set_env_api_key, mock_settings_file):
    """Тест обработки случая, когда настройки пользователя не загружаются"""
    api_key = os.getenv("API_KEY")
    date = "2024-07-22"
    settings_file = mock_settings_file

    with patch("src.utils.get_load_user_setting", side_effect=mock_get_load_user_setting_fail):
        result = get_stock_prices(api_key, settings_file, date)
        assert result == {}

def test_get_stock_prices_request_error(set_env_api_key, mock_settings_file):
    """Тест обработки ошибки запроса к API."""
    api_key = os.getenv("API_KEY")
    date = "2024-07-22"
    settings_file = mock_settings_file

    def mock_requests_get(url, params):
        raise requests.exceptions.RequestException("Connection error")

    with patch("src.utils.get_load_user_setting", side_effect=mock_get_load_user_setting_success):
        with patch("requests.get", side_effect=mock_requests_get):
            result = get_stock_prices(api_key, settings_file, date)
            assert result == {}

def test_get_stock_prices_no_data_for_date(set_env_api_key, mock_settings_file):
    """Тест обработки случая, когда нет данных для указанной даты"""
    api_key = os.getenv("API_KEY")
    date = "2024-07-22"
    settings_file = mock_settings_file

    # Mock ответ от API без данных для указанной даты
    def mock_requests_get(url, params):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "Time Series (Daily)": {
                "2024-07-21": {"4. close": "145.00"}
            }
        }
        return mock_response

    with patch("src.utils.get_load_user_setting", side_effect=mock_get_load_user_setting_success):
        with patch("requests.get", side_effect=mock_requests_get):
            result = get_stock_prices(api_key, settings_file, date)
            expected_result = {}
            assert result == expected_result
