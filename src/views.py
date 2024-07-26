import json
import logging
import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from src.read_excel import read_excel_file
from src.utils import get_exchange_rates, get_stock_prices

load_dotenv()

log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")
os.makedirs(log_dir, exist_ok=True)

# Настраиваем логгер
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler = logging.FileHandler(os.path.join(log_dir, "views.log"), mode="w", encoding="utf-8")
file_handler.setLevel(logging.DEBUG)
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


def get_greeting(date_time_str: str) -> str:
    """Функция приветствия в зависимости от времени суток"""
    now = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")

    if 6 <= now.hour < 12:
        return "Доброе утро"
    elif 12 <= now.hour < 18:
        return "Добрый день"
    elif 18 <= now.hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"

# if __name__ == "__main__":
#     test_date_time = "2024-07-26 15:00:00"
#     greeting = get_greeting(test_date_time)
#     print(greeting)


def analyze_transactions(df: pd.DataFrame, date_time_str: str) -> str:
    """Анализирует транзакции из DataFrame и возвращает JSON-ответ"""
    try:
        # Проверка, что DataFrame не пустой
        if df.empty:
            logger.error("Нет данных для анализа.")
            return json.dumps({"error": "Нет данных для анализа"}, ensure_ascii=False)

        logger.info("Начинаем анализ транзакций.")

        # Проверяем наличие необходимых колонок
        required_columns = ["Номер карты", "Сумма операции"]
        if not all(col in df.columns for col in required_columns):
            logger.error("Необходимые колонки отсутствуют в данных.")
            return json.dumps({"error": "Необходимые колонки отсутствуют в данных"}, ensure_ascii=False)

        # Последние 4 цифры номера карты
        if "Номер карты" in df.columns and not df.empty:
            last_digits = df["Номер карты"].astype(str).str[-4:].mode().iloc[0]  # Наиболее частые последние 4 цифры
        else:
            last_digits = ""

        # Общая сумма расходов
        df["Сумма операции"] = pd.to_numeric(df["Сумма операции"], errors="coerce")
        total_spent = abs(df[df["Сумма операции"] < 0]["Сумма операции"].sum())

        # Вычисление кэшбэка
        cashback = total_spent / 100.0  # 1 рубль на каждые 100 рублей потраченных

        result = {
            "last_digits": last_digits,
            "total_spent": round(float(total_spent), 2),
            "cashback": round(cashback, 2),
        }

        logger.info("Анализ транзакций завершен успешно.")
        return json.dumps(result, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error(f"Ошибка при анализе транзакций: {str(e)}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)



def get_top_transactions(df: pd.DataFrame, date_time_str: str) -> str:
    """Возвращает топ-5 транзакций по сумме платежа в формате JSON от начала месяца до указанной даты"""
    try:
        # Определение начала месяца
        now = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now

        logger.debug(f"Начало месяца: {start_of_month}")
        logger.debug(f"Конец диапазона: {end_date}")

        # Преобразование столбца даты в datetime
        date_format = "%Y-%m-%d %H:%M:%S"  # Убедитесь, что формат совпадает с вашим DataFrame
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format=date_format, errors="coerce")

        logger.debug(f"Данные после преобразования даты:\n{df.head()}")

        # Фильтрация транзакций по дате
        filtered_df = df[(df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= end_date)]

        logger.debug(f"Отфильтрованные данные:\n{filtered_df.head()}")

        # Сортировка транзакций по сумме в убывающем порядке и выбор топ-5
        sorted_df = filtered_df.sort_values(by="Сумма операции", ascending=False)
        top_transactions = sorted_df.head(5)

        logger.debug(f"Топ-5 транзакций:\n{top_transactions}")

        # Форматирование даты и суммы
        top_transactions["Дата операции"] = top_transactions["Дата операции"].dt.strftime("%d.%m.%Y")
        top_transactions["Сумма операции"] = top_transactions["Сумма операции"].astype(float)

        # Формирование результата в требуемом формате
        result = []
        for _, row in top_transactions.iterrows():
            result.append(
                {
                    "date": row["Дата операции"],
                    "amount": float(row["Сумма операции"]),
                    "category": row.get("Категория"),
                    "description": row.get("Описание"),
                }
            )

        logger.info("Топ-5 транзакций успешно получены.")
        return json.dumps({"top_transactions": result}, ensure_ascii=False, indent=4)

    except Exception as e:
        logger.error(f"Ошибка при получении топ-5 транзакций: {str(e)}")
        return json.dumps({"error": str(e)}, ensure_ascii=False)


def main_first(df: pd.DataFrame, date_time_str: str) -> str:
    """Главная функция, которая возвращает JSON-ответ с необходимыми параметрами"""
    try:
        # Получение данных
        greeting = get_greeting(date_time_str)
        cards_analysis_json = analyze_transactions(df, date_time_str)
        top_transactions_json = get_top_transactions(df, date_time_str)
        exchange_rates = get_exchange_rates()
        stock_prices = get_stock_prices(
            api_key=os.getenv("alphavantage_co_API_KEY"),
            settings_file="../user_settings.json",
            date=date_time_str
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


if __name__ == "__main__":
    data = {
        "Дата операции": ["2021-07-01 12:00:00", "2021-07-02 14:30:00", "2021-07-03 09:15:00"],
        "Категория": ["Супермаркеты", "Кафе", "Рестораны"],
        "Описание": ["Покупка в супермаркете", "Обед в кафе", "Ужин в ресторане"],
        "Сумма операции": [-1500, -800, -1200],
        "Номер карты": ["*7197", "*7197", "*7196"]
    }
    df = pd.DataFrame(data)
    date_time_str = "2021-07-03 14:30:00"
    result = main_first(df, date_time_str)
    print(result)