import json
import pandas as pd
import logging
from src.read_excel import read_excel_file


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)

def search_transactions(file_name: str, search_query: str) -> str:
    """Ищет транзакции по строке запроса в описании или категории и возвращает результат в формате JSON"""
    logger.info(f"Начинаем поиск транзакций в файле {file_name} по запросу '{search_query}'")
    try:
        df = read_excel_file(file_name) # Чтение данных из Excel
        logger.debug(f"Данные успешно загружены из файла {file_name}")

        # Проверка наличия необходимых колонок
        required_columns = {"Описание", "Категория"}
        if not required_columns.issubset(df.columns):
            error_message = "Отсутствуют необходимые колонки в данных"
            logger.error(error_message)
            raise ValueError(error_message)

        # Поиск по описанию и категории
        search_query_lower = search_query.lower()
        filtered_df = df[
            df["Описание"].str.lower().str.contains(search_query_lower, na=False) |
            df["Категория"].str.lower().str.contains(search_query_lower, na=False)
        ]

        logger.info(f"Поиск завершен. Найдено {len(filtered_df)} транзакций.")

        # Формирование результата
        result = filtered_df.to_dict(orient="records")

        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error(f"Ошибка при поиске транзакций: {str(e)}")
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    file_name = "../data/operations.xlsx"
    search_query = "Супермаркеты"
    result = search_transactions(file_name, search_query)
    print(result)
