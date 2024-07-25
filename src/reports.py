import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

import pandas as pd
import json

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def report_to_file(file_name: Optional[str] = None):
    """Декоратор для записи результата функции в файл"""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logging.info(f"Вызов функции {func.__name__} с аргументами: {args}, {kwargs}")
            try:
                # Выполнение функции и получение результата
                result_df = func(*args, **kwargs)

                # Преобразование всех столбцов типа datetime в строки
                if not result_df.empty:
                    for col in result_df.select_dtypes(include=["datetime64[ns]"]).columns:
                        result_df[col] = result_df[col].dt.strftime("%Y-%m-%d")

                # Преобразование результата в JSON
                result_json = result_df.to_dict(orient="records")
                result_json_str = json.dumps(result_json, ensure_ascii=False, indent=4)

                # Определение имени файла
                output_file_name = file_name if file_name else f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

                # Запись JSON в файл
                with open(output_file_name, "w", encoding="utf-8") as f:
                    f.write(result_json_str)
                logging.info(f"Отчет сохранен в файл {output_file_name}")

                return result_json_str # Возвращаем JSON
            except Exception as e:
                logging.error(f"Ошибка в функции {func.__name__}: {e}")
                raise

        return wrapper

    return decorator


@report_to_file()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """Возвращает траты по категории за последние три месяца с заданной даты (или от текущей даты)"""
    logging.info(f"Функция spending_by_category вызвана с категорией: {category} и датой: {date}")

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
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y", errors="coerce")

    # Удаление строк с недопустимыми датами после преобразования
    transactions.dropna(subset=["Дата операции"], inplace=True)

    # Фильтрация данных по категории и дате
    filtered_df = transactions[
        (transactions["Категория"].str.contains(category, case=False, na=False))
        & (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
        ].copy()

    # Преобразование формата даты в строку
    filtered_df["Дата операции"] = filtered_df["Дата операции"].dt.strftime("%Y-%m-%d")

    logging.info(f"Найдено {len(filtered_df)} транзакций по категории {category} за период с {start_date} по {end_date}.")

    return filtered_df

if __name__ == "__main__":
    data = {
        "Дата операции": ["01.07.2024", "10.07.2024", "15.07.2024", "20.04.2024"],
        "Категория": ["Супермаркеты", "Кафе", "Супермаркеты", "Кафе"],
        "Сумма операции": [1500, 800, 2000, 1200]
    }

    # Создание DataFrame
    transactions_df = pd.DataFrame(data)

    # Тестирование функции spending_by_category
    try:
        # Тестирование с конкретной категорией и датой
        result_df = spending_by_category(transactions_df, "Супермаркеты", "2024-07-15")
        print("Результат для категории 'Супермаркеты' от 2024-07-15:")
        print(result_df)

        # Тестирование с категорией и текущей датой
        result_df = spending_by_category(transactions_df, "Кафе")
        print("Результат для категории 'Кафе' от текущей даты:")
        print(result_df)

    except Exception as e:
        print(f"Ошибка во время тестирования: {e}")
