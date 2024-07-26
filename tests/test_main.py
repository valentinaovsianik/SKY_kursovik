import json
import os
from unittest.mock import patch

import pandas as pd
import pytest

from src.main import main


# Фикстура для создания тестовых данных
@pytest.fixture
def sample_transactions():
    return pd.DataFrame(
        {
            "Дата операции": ["01.12.2021 12:00:00", "02.12.2021 13:00:00"],
            "Сумма операции": [100.0, 200.0],
            "Категория": ["Супермаркеты", "Рестораны"],
        }
    )


@pytest.mark.parametrize(
    "search_query, category, expected_search_results, expected_spending_by_category, expected_main_first",
    [
        (
            "Рестораны",
            "Супермаркеты",
            [{"Дата операции": "02.12.2021 13:00:00", "Сумма операции": 200.0}],
            [{"Дата операции": "02.12.2021", "Сумма операции": 200.0}],
            {"key": "value"},
        ),
        (None, "Супермаркеты", [], [{"Дата операции": "02.12.2021", "Сумма операции": 200.0}], {"key": "value"}),
        ("Рестораны", None, [{"Дата операции": "02.12.2021 13:00:00", "Сумма операции": 200.0}], [], {"key": "value"}),
        (None, None, [], [], {"key": "value"}),
    ],
)
def test_main(
    sample_transactions,
    search_query,
    category,
    expected_search_results,
    expected_spending_by_category,
    expected_main_first,
):

    with patch("src.main.search_transactions") as mock_search_transactions, patch(
        "src.main.spending_by_category"
    ) as mock_spending_by_category, patch("src.main.main_first") as mock_main_first:

        mock_search_transactions.return_value = expected_search_results
        mock_spending_by_category.return_value = "test_report.json"
        mock_main_first.return_value = json.dumps(expected_main_first)

        # Создание файла отчета
        report_data = expected_spending_by_category
        report_file_name = "test_report.json"
        with open(report_file_name, "w", encoding="utf-8") as f:
            json.dump(report_data, f)

        result = main(sample_transactions, "2021-12-01 00:00:00", search_query=search_query, category=category)

        assert result["search_transactions"] == expected_search_results
        assert result["spending_by_category"] == expected_spending_by_category
        assert result["main_first"] == expected_main_first

        os.remove(report_file_name)
