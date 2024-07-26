import json

import pandas as pd
import pytest

from src.views import analyze_transactions, get_greeting, get_top_transactions, main_first


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
transactions_data = pd.DataFrame(
    {
        "Номер карты": ["1234567812345678", "8765432187654321", "1234567812345678"],
        "Сумма операции": [-100.00, -200.00, -42.01],
    }
)


# Тест с отсутствием данных
def test_analyze_transactions_no_data():
    result = analyze_transactions(pd.DataFrame(), "2023-07-04")
    expected_result = {"error": "Нет данных для анализа"}
    assert json.loads(result) == expected_result


# Тест с отсутствием необходимых колонок
def test_analyze_transactions_missing_columns():
    df_missing_columns = pd.DataFrame(
        {
            "Номер карты": ["1234567812345678"],
            # Отсутствует "Сумма операции"
        }
    )
    result = analyze_transactions(df_missing_columns, "2023-07-04")
    expected_result = {"error": "Необходимые колонки отсутствуют в данных"}
    assert json.loads(result) == expected_result


# Тест с отсутствием номеров карт (чтобы проверить что происходит, если DataFrame имеет только одну колонку)
def test_analyze_transactions_missing_card_numbers():
    df_missing_card_numbers = pd.DataFrame({"Сумма операции": [-100.00, -200.00, -42.01]})
    result = analyze_transactions(df_missing_card_numbers, "2023-07-04")
    expected_result = {"error": "Необходимые колонки отсутствуют в данных"}
    assert json.loads(result) == expected_result


# Тест для get_top_transactions
transactions_data = pd.DataFrame(
    {
        "Дата операции": [
            "2024-07-01 10:00:00",
            "2024-07-05 12:00:00",
            "2024-07-10 09:00:00",
            "2024-07-15 14:00:00",
            "2024-07-20 16:00:00",
            "2024-07-25 11:00:00",
        ],
        "Сумма операции": [150.00, 200.00, 50.00, 300.00, 400.00, 250.00],
        "Категория": ["Еда", "Транспорт", "Одежда", "Кафе", "Развлечения", "Путешествия"],
        "Описание": [
            "Покупка продуктов",
            "Такси",
            "Новая куртка",
            "Обед с друзьями",
            "Билет в кино",
            "Поездка в горы",
        ],
    }
)


# Тест с отсутствием данных в диапазоне
def test_get_top_transactions_no_data_in_range():
    df_no_data = pd.DataFrame(
        {
            "Дата операции": ["2024-06-01 10:00:00", "2024-06-15 12:00:00"],
            "Сумма операции": [150.00, 200.00],
            "Категория": ["Еда", "Транспорт"],
            "Описание": ["Покупка продуктов", "Такси"],
        }
    )
    result = get_top_transactions(df_no_data, "2024-07-01 10:00:00")
    expected_result = {"top_transactions": []}
    assert json.loads(result) == expected_result


# Тест с некорректным форматом даты
def test_get_top_transactions_invalid_date_format():
    result = get_top_transactions(transactions_data, "2024-07-25")
    expected_result = {"error": "time data '2024-07-25' does not match format '%Y-%m-%d %H:%M:%S'"}
    assert json.loads(result) == expected_result


# Тест для main_first
@pytest.fixture
def mock_dependencies(mocker):
    mock_greeting = "Добрый день"
    mock_cards_analysis = {"last_digits": "7197", "total_spent": 9965776.83, "cashback": 99657.77}
    mock_top_transactions = {
        "top_transactions": [
            {"date": "23.07.2024", "amount": -150.0, "category": "Супермаркеты", "description": "Покупка"},
            {"date": "23.07.2024", "amount": -120.0, "category": "Кафе", "description": "Ужин"},
            {"date": "23.07.2024", "amount": -100.0, "category": "Транспорт", "description": "Такси"},
        ]
    }
    mock_exchange_rates = [{"currency": "USD", "rate": 1.1}, {"currency": "EUR", "rate": 0.9}]
    mock_stock_prices = [{"symbol": "AAPL", "price": 150.0}, {"symbol": "GOOGL", "price": 2800.0}]

    mocker.patch("src.views.get_greeting", return_value=mock_greeting)
    mocker.patch("src.views.analyze_transactions", return_value=json.dumps(mock_cards_analysis))
    mocker.patch("src.views.get_top_transactions", return_value=json.dumps(mock_top_transactions))
    mocker.patch("src.views.get_exchange_rates", return_value=mock_exchange_rates)
    mocker.patch("src.views.get_stock_prices", return_value=mock_stock_prices)


@pytest.fixture
def sample_df():
    """Создает DataFrame для тестирования"""
    return pd.DataFrame(
        {
            "Дата операции": [
                "2024-07-01 10:00:00",
                "2024-07-05 12:00:00",
                "2024-07-10 09:00:00",
                "2024-07-15 14:00:00",
                "2024-07-20 16:00:00",
                "2024-07-25 11:00:00",
            ],
            "Сумма операции": [150.00, 200.00, 50.00, 300.00, 400.00, 250.00],
            "Категория": ["Еда", "Транспорт", "Одежда", "Кафе", "Развлечения", "Путешествия"],
            "Описание": [
                "Покупка продуктов",
                "Такси",
                "Новая куртка",
                "Обед с друзьями",
                "Билет в кино",
                "Поездка в горы",
            ],
        }
    )


def test_main_first(mock_dependencies, sample_df):
    date_time = "2024-07-23 14:30:00"
    expected_result = {
        "greeting": "Добрый день",
        "cards": {"last_digits": "7197", "total_spent": 9965776.83, "cashback": 99657.77},
        "top_transactions": [
            {"date": "23.07.2024", "amount": -150.0, "category": "Супермаркеты", "description": "Покупка"},
            {"date": "23.07.2024", "amount": -120.0, "category": "Кафе", "description": "Ужин"},
            {"date": "23.07.2024", "amount": -100.0, "category": "Транспорт", "description": "Такси"},
        ],
        "currency_rates": [{"currency": "USD", "rate": 1.1}, {"currency": "EUR", "rate": 0.9}],
        "stock_prices": [{"symbol": "AAPL", "price": 150.0}, {"symbol": "GOOGL", "price": 2800.0}],
    }

    result = main_first(sample_df, date_time)
    result_dict = json.loads(result)

    assert result_dict == expected_result
