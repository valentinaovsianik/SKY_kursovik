import json
import logging
import os
import pandas as pd

from dotenv import load_dotenv

from datetime import datetime
from src.views import get_greeting, get_top_transactions, analyze_transactions
from src.read_excel import read_excel_file
from src.utils import get_stock_prices, get_exchange_rates

load_dotenv()

# Установка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


def main(datetime_str: str) -> str:
    """Главная функция, которая возвращает JSON-ответ с необходимыми параметрами"""
    try:
        # Получение данных
        greeting = get_greeting(datetime_str)
        cards_analysis_json = analyze_transactions("../data/operations.xlsx", datetime_str)
        top_transactions_json = get_top_transactions(datetime_str)
        exchange_rates = get_exchange_rates()
        stock_prices = get_stock_prices(
            api_key=os.getenv("alphavantage_co_API_KEY"),
            settings_file="../user_settings.json",
            date=datetime_str,
        )

        # Декодирование JSON-ответов в словари
        cards_analysis = json.loads(cards_analysis_json)
        top_transactions = json.loads(top_transactions_json)

        # Формирование результата в формате JSON
        result = {
            "greeting": greeting,
            "cards": cards_analysis,
            "top_transactions": top_transactions.get("top_transactions", []),
            "currency_rates": exchange_rates if exchange_rates else [],
            "stock_prices": stock_prices if stock_prices else [],
        }

        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error(f"Ошибка в главной функции: {str(e)}")
        return json.dumps({"error": str(e)}, ensure_ascii=False, indent=4)


# if __name__ == "__main__":
#     date_time = "2024-12-08 14:30:00"
#     result = main(date_time)
#     print(result)
