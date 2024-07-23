import json
from unittest.mock import Mock, patch

import pandas as pd
import pytest

from src.views import analyze_transactions, get_greeting, get_top_transactions


# Тест для get_greeting
@pytest.mark.parametrize(
    "date_time_str, expected_greeting",
    [
        ("2023-07-23 08:00:00", "Доброе утро"),
        ("2023-07-23 13:00:00", "Добрый день"),
        ("2023-07-23 19:00:00", "Добрый вечер"),
        ("2023-07-23 23:00:00", "Доброй ночи"),
        ("2023-07-23 05:00:00", "Доброй ночи"),
    ],
)
def test_get_greeting(date_time_str, expected_greeting):
    assert get_greeting(date_time_str) == expected_greeting


# Данные для  тестирования в формате DataFrame
transactions_data = pd.DataFrame(
    {
        "Дата операции": ["31.12.2021 16:44:00", "31.12.2021 16:42:04", "31.12.2021 16:39:04"],
        "Дата платежа": ["31.12.2021", "31.12.2021", "31.12.2021"],
        "Номер карты": ["*7197", "*7197", "*7197"],
        "Статус": ["OK", "OK", "OK"],
        "Сумма операции": [-160.89, -64.00, -117.12],
        "Валюта операции": ["RUB", "RUB", "RUB"],
        "Сумма платежа": [-160.89, -64.00, -117.12],
        "Валюта платежа": ["RUB", "RUB", "RUB"],
        "Кэшбэк": ["", "", ""],
        "Категория": ["Супермаркеты", "Супермаркеты", "Супермаркеты"],
        "MCC": [5411, 5411, 5411],
        "Описание": ["Колхоз", "Колхоз", "Магнит"],
    }
)


# Тесты для analyze_transactions
# Тест с успешным результатом
@patch("src.views.read_excel_file")
def test_analyze_transactions_success(mock_read_excel_file):
    def mock_read_excel_file_success(file_name):
        return transactions_data

    mock_read_excel_file.side_effect = mock_read_excel_file_success
    result = analyze_transactions("test.xlsx", "2023-07-04")
    expected_result = {"last_digits": "7197", "total_spent": 342.01, "cashback": 3.42}
    assert json.loads(result) == expected_result


# Тест с отсутствием данных
@patch("src.views.read_excel_file")
def test_analyze_transactions_no_data(mock_read_excel_file):
    def mock_read_excel_file_no_data(file_name):
        return pd.DataFrame()  # Пустой DataFrame

    mock_read_excel_file.side_effect = mock_read_excel_file_no_data
    result = analyze_transactions("test.xlsx", "2023-07-04")
    expected_result = {"error": "Нет данных для анализа в файле test.xlsx"}
    assert json.loads(result) == expected_result


# Тест с исключением
@patch("src.views.read_excel_file")
def test_analyze_transactions_exception(mock_read_excel_file):
    def mock_read_excel_file_exception(file_name):
        raise Exception("Ошибка чтения файла")

    mock_read_excel_file.side_effect = mock_read_excel_file_exception
    result = analyze_transactions("test.xlsx", "2023-07-04")
    expected_result = {"error": "Ошибка чтения файла"}
    assert json.loads(result) == expected_result


# Тест для get_top_transactions
transactions_data = pd.DataFrame(
    {
        "Дата операции": ["31.12.2021 16:44:00", "31.12.2021 16:42:04", "31.12.2021 16:39:04"],
        "Дата платежа": ["31.12.2021", "31.12.2021", "31.12.2021"],
        "Номер карты": ["*7197", "*7197", "*7197"],
        "Статус": ["OK", "OK", "OK"],
        "Сумма операции": [-160.89, -64.00, -117.12],
        "Валюта операции": ["RUB", "RUB", "RUB"],
        "Сумма платежа": [-160.89, -64.00, -117.12],
        "Валюта платежа": ["RUB", "RUB", "RUB"],
        "Кэшбэк": ["", "", ""],
        "Категория": ["Супермаркеты", "Супермаркеты", "Супермаркеты"],
        "MCC": [5411, 5411, 5411],
        "Описание": ["Колхоз", "Колхоз", "Магнит"],
    }
)

# Ожидаемый результат
expected_result = {
    "top_transactions": [
        {"date": "31.12.2021", "amount": -64.00, "category": "Супермаркеты", "description": "Колхоз"},
        {"date": "31.12.2021", "amount": -117.12, "category": "Супермаркеты", "description": "Магнит"},
        {"date": "31.12.2021", "amount": -160.89, "category": "Супермаркеты", "description": "Колхоз"},
    ]
}


@patch("src.views.read_excel_file")
def test_get_top_transactions(mock_read_excel_file):
    mock_read_excel_file.return_value = transactions_data
    result = get_top_transactions("2021-12-31 23:59:59")
    result_dict = json.loads(result)
    assert result_dict == expected_result
