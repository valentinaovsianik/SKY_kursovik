import json

import pytest

from src.services import search_transactions


@pytest.fixture
def sample_transactions():
    """Создание тестовых данных в формате списка словарей"""
    return [
        {
            "Дата операции": "31.12.2021 16:44:00",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": "-160,89",
            "Валюта операции": "RUB",
            "Сумма платежа": "-160,89",
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Супермаркеты",
            "MCC": "5411",
            "Описание": "Колхоз",
        },
        {
            "Дата операции": "31.12.2021 16:42:04",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": "-64,00",
            "Валюта операции": "RUB",
            "Сумма платежа": "-64,00",
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Супермаркеты",
            "MCC": "5411",
            "Описание": "Колхоз",
        }
    ]

def test_search_transactions(sample_transactions):
    """Тестирование функции поиска транзакций"""
    search_query = "Колхоз"
    expected_result = [
        {
            "Дата операции": "31.12.2021 16:44:00",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": "-160,89",
            "Валюта операции": "RUB",
            "Сумма платежа": "-160,89",
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Супермаркеты",
            "MCC": "5411",
            "Описание": "Колхоз",
        },
        {
            "Дата операции": "31.12.2021 16:42:04",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": "-64,00",
            "Валюта операции": "RUB",
            "Сумма платежа": "-64,00",
            "Валюта платежа": "RUB",
            "Кэшбэк": "",
            "Категория": "Супермаркеты",
            "MCC": "5411",
            "Описание": "Колхоз",
        }
    ]
    expected_json = json.dumps(expected_result, ensure_ascii=False, indent=4)

    result = search_transactions(sample_transactions, search_query)

    assert result == expected_json

def test_search_transactions_no_results(sample_transactions):
    """Тестирование поиска транзакций без результатов"""
    search_query = "Не существует"
    expected_result = []
    expected_json = json.dumps(expected_result, ensure_ascii=False, indent=4)

    result = search_transactions(sample_transactions, search_query)

    assert result == expected_json

def test_search_transactions_missing_columns():
    """Тестирование поиска транзакций при отсутствии необходимых колонок"""
    transactions = [
        {
            "Дата операции": "31.12.2021 16:44:00",
            "Дата платежа": "31.12.2021",
            "Номер карты": "*7197",
            "Статус": "OK",
            "Сумма операции": "-160,89",
            "Валюта операции": "RUB",
            "Сумма платежа": "-160,89",
            "Валюта платежа": "RUB",
            "Кэшбэк": ""
        }
    ]

    search_query = "Колхоз"
    expected_result = {"error": "Отсутствуют необходимые колонки в данных"}
    expected_json = json.dumps(expected_result, ensure_ascii=False, indent=4)

    result = search_transactions(transactions, search_query)

    assert result == expected_json