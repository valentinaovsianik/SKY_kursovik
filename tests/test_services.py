import pytest
import pandas as pd
import json
import os
from src.services import search_transactions


@pytest.fixture
def sample_excel_file(tmpdir):
    """Создание временного Excel-файла с тестовыми данными"""
    file_path = os.path.join(tmpdir, "test_operations.xlsx")
    data = {
        "Дата операции": ["31.12.2021 16:44:00", "31.12.2021 16:42:04"],
        "Дата платежа": ["31.12.2021", "31.12.2021"],
        "Номер карты": ["*7197", "*7197"],
        "Статус": ["OK", "OK"],
        "Сумма операции": ["-160,89", "-64,00"],
        "Валюта операции": ["RUB", "RUB"],
        "Сумма платежа": ["-160,89", "-64,00"],
        "Валюта платежа": ["RUB", "RUB"],
        "Кэшбэк": ["", ""],
        "Категория": ["Супермаркеты", "Супермаркеты"],
        "MCC": ["5411", "5411"],
        "Описание": ["Колхоз", "Колхоз"]
    }
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)
    return file_path


def test_search_transactions(sample_excel_file):
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
            "Описание": "Колхоз"
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
            "Описание": "Колхоз"
        }
    ]
    expected_json = json.dumps(expected_result, ensure_ascii=False, indent=4)

    result = search_transactions(sample_excel_file, search_query)

    assert result == expected_json


def test_search_transactions_no_results(sample_excel_file):
    """Тестирование поиска транзакций без результатов"""
    search_query = "Не существует"
    expected_result = []
    expected_json = json.dumps(expected_result, ensure_ascii=False, indent=4)

    result = search_transactions(sample_excel_file, search_query)

    assert result == expected_json


def test_search_transactions_missing_columns(tmpdir):
    """Тестирование поиска транзакций при отсутствии необходимых колонок"""
    file_path = os.path.join(tmpdir, "test_operations_missing_columns.xlsx")
    data = {
        "Дата операции": ["31.12.2021 16:44:00"],
        "Дата платежа": ["31.12.2021"],
        "Номер карты": ["*7197"],
        "Статус": ["OK"],
        "Сумма операции": ["-160,89"],
        "Валюта операции": ["RUB"],
        "Сумма платежа": ["-160,89"],
        "Валюта платежа": ["RUB"],
        "Кэшбэк": [""],
        "Категория": ["Супермаркеты"]
    }
    df = pd.DataFrame(data)
    df.to_excel(file_path, index=False)

    search_query = "Колхоз"
    expected_result = {"error": "Отсутствуют необходимые колонки в данных"}
    expected_json = json.dumps(expected_result, ensure_ascii=False, indent=4)

    result = search_transactions(file_path, search_query)

    assert result == expected_json
