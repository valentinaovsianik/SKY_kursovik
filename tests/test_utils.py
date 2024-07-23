import pytest
import json
import os
from unittest.mock import patch, Mock, mock_open
from requests.exceptions import RequestException

from src.utils import get_load_user_setting, get_load_user_setting, get_exchange_rates

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
    """Фикстура для установки переменной окружения API_KEY."""
    with patch.dict("os.environ", {"API_KEY": "test_api_key"}):
        yield


def test_get_exchange_rates_success(mock_env_vars):
    """Тест успешного получения данных о курсах валют."""
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
    """Тест на случай ошибки запроса."""
    # Создаем mock для requests.get
    with patch("requests.get") as mock_get:
        mock_get.side_effect = RequestException("Connection error")
        result = get_exchange_rates()
        assert result is None
