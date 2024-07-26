import json
import logging

import pandas as pd

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def search_transactions(transactions: list[dict], search_query: str) -> str:
    """Ищет транзакции по строке запроса в описании или категории и возвращает результат в формате JSON"""
    logger.info(f"Начинаем поиск транзакций по запросу '{search_query}'")
    try:
        df = pd.DataFrame(transactions)
        logger.debug("Данные успешно преобразованы в DataFrame")

        # Проверка наличия необходимых колонок
        required_columns = {"Описание", "Категория"}
        if not required_columns.issubset(df.columns):
            error_message = "Отсутствуют необходимые колонки в данных"
            logger.error(error_message)
            raise ValueError(error_message)

        # Поиск по описанию и категории
        search_query_lower = search_query.lower()
        filtered_df = df[
            df["Описание"].str.lower().str.contains(search_query_lower, na=False)
            | df["Категория"].str.lower().str.contains(search_query_lower, na=False)
        ]

        # Приведение данных к строковому типу и замена NaN
        filtered_df = filtered_df.fillna("")
        for column in ["Кэшбэк", "MCC"]:
            if column in filtered_df.columns:
                filtered_df[column] = filtered_df[column].astype(str)

        logger.info(f"Поиск завершен. Найдено {len(filtered_df)} транзакций.")

        # Формирование результата
        result = filtered_df.to_dict(orient="records")

        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error(f"Ошибка при поиске транзакций: {str(e)}")
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    transactions = [
        {"Описание": "Купил кофе", "Категория": "Кафе", "Кэшбэк": 10, "MCC": 5812},
        {"Описание": "Оплата в супермаркете", "Категория": "Супермаркеты", "Кэшбэк": 20, "MCC": 5411},
        {"Описание": "Поездка на такси", "Категория": "Транспорт", "Кэшбэк": 15, "MCC": 4121},
        {"Описание": "Обед в ресторане", "Категория": "Рестораны", "Кэшбэк": 5, "MCC": 5811},
    ]
    search_query = "Супермаркет"
    result_json = search_transactions(transactions, search_query)
    print(result_json)
