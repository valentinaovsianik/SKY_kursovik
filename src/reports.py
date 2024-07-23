import os
import json
import pandas as pd
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)


def report_to_file(file_name=None):
    """Декоратор для записи результата функции в файл"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logging.info(
                f"Вызов функции {func.__name__} с аргументами: {args}, {kwargs}"
            )
            try:
                # Выполнение функции и получение результата
                result_df = func(*args, **kwargs)

                # Определение имени файла
                output_file_name = (
                    file_name if file_name else f"report_{func.__name__}.json"
                )

                # Преобразование результата в JSON и запись в файл
                result_json = result_df.to_json(
                    orient="records", force_ascii=False, indent=4
                )
                with open(output_file_name, "w", encoding="utf-8") as f:
                    f.write(result_json)
                logging.info(f"Отчет сохранен в файл {output_file_name}")

                return result_json  # Возвращаем JSON вместо DataFrame
            except Exception as e:
                logging.error(f"Ошибка в функции {func.__name__}: {e}")
                raise

        return wrapper

    return decorator


@report_to_file()
def spending_by_category(
    transactions: pd.DataFrame, category: str, date: Optional[str] = None
) -> pd.DataFrame:
    """Возвращает траты по категории за последние три месяца с заданной даты (или от текущей даты)"""
    logging.info(
        f"Функция spending_by_category вызвана с категорией: {category} и датой: {date}"
    )

    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    # Преобразование строки в дату
    try:
        end_date = datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        logging.error("Неверный формат даты. Используйте 'YYYY-MM-DD'.")
        raise ValueError("Неверный формат даты. Используйте 'YYYY-MM-DD'.")

    start_date = end_date - timedelta(days=90)

    # Преобразование формата даты в DataFrame
    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"], format="%d.%m.%Y"
    )

    # Фильтрация данных по категории и дате
    filtered_df = transactions[
        (transactions["Категория"].str.contains(category, case=False, na=False))
        & (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
    ]

    # Сумма трат
    total_expenses = (
        filtered_df.groupby("Категория")["Сумма операции"].sum().reset_index()
    )

    # Формирование результата
    total_expenses.columns = ["Категория", "Общая сумма"]

    logging.info(
        f"Траты по категории {category} за период с {start_date} по {end_date} успешно рассчитаны."
    )
    return total_expenses
