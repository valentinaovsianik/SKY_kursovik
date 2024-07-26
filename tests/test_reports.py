import json
import os
import unittest

import pandas as pd

from src.reports import report_to_file, spending_by_category


class TestSpendingByCategory(unittest.TestCase):

    def setUp(self):
        """Создание данных для тестов"""
        self.data = {
            "Дата операции": ["01.07.2024", "10.07.2024", "15.07.2024", "20.04.2024"],
            "Категория": ["Супермаркеты", "Кафе", "Супермаркеты", "Кафе"],
            "Сумма операции": [1500, 800, 2000, 1200],
        }
        self.df = pd.DataFrame(self.data)

    def test_invalid_date_format(self):
        """Проверка обработки неверного формата даты"""
        result = spending_by_category(self.df, "Супермаркеты", "invalid_date")
        expected_result = []
        self.assertEqual(json.loads(result), expected_result)

    def test_missing_category(self):
        """Проверка обработки отсутствующей категории"""
        result = spending_by_category(self.df, "Неизвестная категория", "2024-07-15 00:00:00")
        expected_result = []
        self.assertEqual(json.loads(result), expected_result)

    def test_default_date(self):
        """Проверка использования текущей даты по умолчанию"""
        result = spending_by_category(self.df, "Супермаркеты")
        # Проверим, что результат не пустой и содержит ожидаемые значения
        self.assertGreater(len(json.loads(result)), 0)

    def test_decorator_creates_file(self):
        """Проверка, что декоратор создает файл"""
        @report_to_file(file_name="test_report.json")
        def dummy_function():
            return self.df

        dummy_function()

        self.assertTrue(os.path.isfile("test_report.json"))

        # Очистка после теста
        os.remove("test_report.json")

    def test_decorator_with_default_filename(self):
        """Проверка, что декоратор создает файл с именем по умолчанию"""
        @report_to_file()
        def dummy_function():
            return self.df

        # Запуск функции
        dummy_function()

        # Проверка, что файл с именем по умолчанию создан
        files = [f for f in os.listdir() if f.startswith('report_') and f.endswith('.json')]
        self.assertGreater(len(files), 0)

        # Очистка после теста
        for file in files:
            os.remove(file)
