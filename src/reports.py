import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Optional

import pandas as pd

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
                output_file_name = (
                    file_name
                    if file_name
                    else f"report_{func.__name__}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                )

                # Запись JSON в файл
                with open(output_file_name, "w", encoding="utf-8") as f:
                    f.write(result_json_str)
                logging.info(f"Отчет сохранен в файл {output_file_name}")

                return result_json_str  # Возвращаем JSON
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
        date = datetime.now().strftime("%Y.%m.%d %H:%M:%S")

    # Попробуйте преобразовать строку даты в datetime объект
    try:
        # Попытайтесь преобразовать входную дату в формат YYYY.MM.DD HH:MM:SS
        end_date = datetime.strptime(date, "%Y.%m.%d %H:%M:%S")
    except ValueError:
        try:
            # Попытайтесь преобразовать входную дату в формат YYYY-MM-DD HH:MM:SS
            end_date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
            # Преобразуйте в нужный формат
            end_date = end_date.strftime("%Y.%m.%d %H:%M:%S")
            end_date = datetime.strptime(end_date, "%Y.%m.%d %H:%M:%S")
        except ValueError:
            logging.error("Неверный формат даты. Используйте 'YYYY.MM.DD HH:MM:SS'.")
            return pd.DataFrame()  # Возвращаем пустой DataFrame вместо ошибки

    # Установка даты начала и конца диапазона
    start_date = end_date - timedelta(days=90)

    # Преобразование формата даты в DataFrame
    transactions["Дата операции"] = pd.to_datetime(transactions["Дата операции"], format="%d.%m.%Y", errors="coerce")

    # Убедитесь, что данные не содержат NaT после преобразования
    if transactions["Дата операции"].isnull().any():
        logging.warning("Некоторые даты не были преобразованы. Проверьте данные.")
        transactions = transactions.dropna(subset=["Дата операции"])

    # Фильтрация данных по категории и дате
    filtered_df = transactions[
        (transactions["Категория"].str.contains(category, case=False, na=False))
        & (transactions["Дата операции"] >= start_date)
        & (transactions["Дата операции"] <= end_date)
    ].copy()

    # Преобразование формата даты в строку
    filtered_df["Дата операции"] = filtered_df["Дата операции"].dt.strftime("%Y.%m.%d %H:%M:%S")

    logging.info(f"Найдено {len(filtered_df)} транзакций по категории {category}.")

    return filtered_df


if __name__ == "__main__":
    data = {
        "Дата операции": ["01.07.2024", "10.07.2024", "15.07.2024", "20.04.2024"],
        "Категория": ["Супермаркеты", "Кафе", "Супермаркеты", "Кафе"],
        "Сумма операции": [1500, 800, 2000, 1200],
    }

    # Преобразование данных в DataFrame
    df = pd.DataFrame(data)

    result_json = spending_by_category(df, "Супермаркеты", "2024-07-15 00:00:00")
    print(result_json)
