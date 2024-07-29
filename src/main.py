import json
import logging
from typing import Optional

import pandas as pd
from dotenv import load_dotenv

from src.reports import spending_by_category
from src.services import search_transactions
from src.views import main_first

load_dotenv()

# Установка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def main(
    transactions: pd.DataFrame, date_time_str: str, search_query: Optional[str] = None, category: Optional[str] = None
) -> dict:
    logging.info("Начинаем анализ транзакций.")

    # Преобразование формата даты в DataFrame
    transactions["Дата операции"] = pd.to_datetime(
        transactions["Дата операции"], format="%d.%m.%Y %H:%M:%S", errors="coerce"
    )

    # Убедитесь, что данные не содержат NaT после преобразования
    if transactions["Дата операции"].isnull().any():
        logging.warning("Некоторые даты не были преобразованы. Проверьте данные.")
        transactions = transactions.dropna(subset=["Дата операции"])

    # Поиск транзакций
    if search_query:
        search_results = search_transactions(transactions, search_query)
        logging.info(f"Поиск завершен. Найдено {len(search_results)} транзакций.")
    else:
        search_results = []

    # Отчет по категории
    report_df = pd.DataFrame()
    if category:
        # Вызов обернутой функции spending_by_category и получение имени файла
        report_file_name = spending_by_category(transactions, category, date_time_str)

        # Проверка, что файл был создан и загрузка JSON-файла
        try:
            # Ожидание, что декоратор вернул имя файла
            with open(report_file_name, "r", encoding="utf-8") as f:
                report_json_str = f.read()
            report_df = pd.read_json(report_json_str, orient="records")
        except FileNotFoundError:
            logging.error(f"Не удалось найти файл отчета: {report_file_name}")
        except Exception as e:
            logging.error(f"Ошибка при чтении файла отчета: {e}")

    # Получение данных для main_first
    try:
        main_first_data_json = main_first(transactions, date_time_str)
        main_first_data = json.loads(main_first_data_json)
    except json.JSONDecodeError as e:
        logging.error(f"Ошибка при декодировании JSON: {e}")
        main_first_data = {}
    except Exception as e:
        logging.error(f"Неизвестная ошибка при вызове main_first: {e}")
        main_first_data = {}

    logging.info("Анализ транзакций завершен успешно.")

    # Результат в формате JSON
    result = {
        "search_transactions": search_results,
        "spending_by_category": report_df.to_dict(orient="records"),
        "main_first": main_first_data,
    }

    return result


# if __name__ == "__main__":
#     file_name = "..//data//operations.xlsx"
#     date_time_str = "2021-12-26 00:00:00"
#
#     # Считывание данных из Excel файла
#     df = read_excel_file(file_name)
#
#     # Вызов функции main с DataFrame
#     result = main(df, date_time_str, search_query="колхоз", category="Супермаркеты")
#
#     # Печать результата
#     print(json.dumps(result, indent=4, ensure_ascii=False))
