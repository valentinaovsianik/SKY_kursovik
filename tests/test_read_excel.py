import os
import tempfile

import pandas as pd
import pytest

from src.read_excel import read_excel_file


@pytest.fixture
def temp_excel_file():
    """Создает временный Excel-файл для тестов и удаляет его после выполнения"""
    # Создаем временный файл
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp_file:
        file_name = tmp_file.name

    # Создаем DataFrame с тестовыми данными
    df = pd.DataFrame(
        {
            "Номер карты": ["1234567812345678", "8765432187654321"],
            "Сумма операции": [-1500.00, 500.00],
            "Дата операции": ["01.01.2024 10:00:00", "02.01.2024 11:00:00"],
        }
    )

    # Записываем DataFrame в Excel-файл
    df.to_excel(file_name, index=False)

    yield file_name

    # Удаляем временный файл после выполнения теста
    if os.path.exists(file_name):
        os.remove(file_name)


def test_read_excel_file_success(temp_excel_file):
    """Тест успешного чтения данных из временного Excel-файла"""
    result = read_excel_file(temp_excel_file)

    # Ожидаемый результат
    df = pd.read_excel(temp_excel_file)
    expected_result = df.to_dict(orient="records")

    assert result == expected_result


def test_read_excel_file_failure():
    """Тест на случай ошибки при чтении данных из несуществующего файла"""
    # Проверяем, что функция выбрасывает исключение
    non_existent_file = "non_existent_file.xlsx"
    with pytest.raises(RuntimeError, match=f"Ошибка при чтении файла {non_existent_file}:"):
        read_excel_file(non_existent_file)
