import json

import pytest

from src.main import main


@pytest.fixture
def mock_dependencies(mocker):
    # Настройка моков
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

    # Патчи для функций
    mocker.patch("src.main.get_greeting", return_value=mock_greeting)
    mocker.patch("src.main.analyze_transactions", return_value=json.dumps(mock_cards_analysis))
    mocker.patch("src.main.get_top_transactions", return_value=json.dumps(mock_top_transactions))
    mocker.patch("src.main.get_exchange_rates", return_value=mock_exchange_rates)
    mocker.patch("src.main.get_stock_prices", return_value=mock_stock_prices)


def test_main(mock_dependencies):
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

    result = main(date_time)
    result_dict = json.loads(result)

    assert result_dict == expected_result
