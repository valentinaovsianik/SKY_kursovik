import json
import os

import pandas as pd
import pytest

from src.reports import spending_by_category


@pytest.fixture
def sample_data():
    """Создаем временный DataFrame с тестовыми данными"""
    data = {
        "Дата операции": ["31.12.2021", "31.12.2021", "31.12.2021"],
        "Категория": ["Супермаркеты", "Супермаркеты", "Рестораны"],
        "Сумма операции": [-160.89, -64.00, -200.00],
        "Описание": ["Магазин", "Колхоз", "Ресторан"],
    }
    df = pd.DataFrame(data)
    return df


def test_spending_by_category(sample_data):
    result_json = spending_by_category(sample_data, "Супермаркеты", "2022-01-01")

    assert result_json is not None

    result_df = pd.read_json(result_json)
    assert not result_df.empty
    assert result_df.iloc[0]["Категория"] == "Супермаркеты"
    assert "Общая сумма" in result_df.columns

    # Проверка содержимого JSON файла
    with open("report_spending_by_category.json", "r", encoding="utf-8") as f:
        result_from_file = json.load(f)

    assert isinstance(result_from_file, list)
    assert result_from_file[0]["Категория"] == "Супермаркеты"

    # Удалить временный файл отчета после теста
    os.remove("report_spending_by_category.json")
