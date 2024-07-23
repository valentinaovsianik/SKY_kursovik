import json
import logging
import os
from datetime import datetime

import pandas as pd
from dotenv import load_dotenv

from src.read_excel import read_excel_file

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
    date_time_obj = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S")  # Преобразование строки в объект datetime

    hour = date_time_obj.hour  # Получение часа из объекта datetime

    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def analyze_transactions(file_name: str, date_time: str) -> str:
    """Анализирует транзакции из excel-файла и возвращает JSON-ответ"""
    try:
        transactions_data = read_excel_file(file_name)

        # Преобразование данных в DataFrame, если это необходимо
        if not isinstance(transactions_data, pd.DataFrame):
            df = pd.DataFrame(transactions_data)
        else:
            df = transactions_data

        # Проверка, что DataFrame не пустой
        if df.empty:
            logger.error(f"Нет данных для анализа в файле {file_name}.")
            return json.dumps(
                {"error": f"Нет данных для анализа в файле {file_name}"},
                ensure_ascii=False,
            )

        logger.info(f"Начинаем анализ транзакций из файла {file_name}.")

        # Проверяем наличие необходимых колонок
        if "Номер карты" not in df.columns or "Сумма операции" not in df.columns:
            logger.error(f"Необходимые колонки отсутствуют в файле {file_name}.")
            return json.dumps(
                {"error": "Необходимые колонки отсутствуют в данных"},
                ensure_ascii=False,
            )

        # Последние 4 цифры номера карты
        last_digits = df["Номер карты"].iloc[0][-4:] if not df.empty and "Номер карты" in df.columns else ""

        # Общая сумма расходов
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


# if __name__ == "__main__":
#     file_name = "../data/operations.xlsx"
#     date_time = "2024-07-23 14:30:00"
#
#     result = analyze_transactions(file_name, date_time)
#     print(result)


def get_top_transactions(date_time: str) -> str:
    """Возвращает топ-5 транзакций по сумме платежа в формате JSON от начала месяца до указанной даты"""
    try:
        # Определение начала месяца
        now = datetime.strptime(date_time, "%Y-%m-%d %H:%M:%S")
        start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        end_date = now

        # Загрузка данных из файла
        file_name = "../data/operations.xlsx"
        transactions_data = read_excel_file(file_name)
        df = pd.DataFrame(transactions_data)

        # Преобразование столбца даты в datetime
        date_format = "%d.%m.%Y %H:%M:%S"
        df["Дата операции"] = pd.to_datetime(df["Дата операции"], format=date_format, errors="coerce")

        # Фильтрация транзакций по дате
        filtered_df = df[(df["Дата операции"] >= start_of_month) & (df["Дата операции"] <= end_date)]

        # Сортировка транзакций по сумме в убывающем порядке и выбор топ-5
        sorted_df = filtered_df.sort_values(by="Сумма операции", ascending=False)
        top_transactions = sorted_df.head(5)

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


# if __name__ == "__main__":
#     date_time = "2021-12-08 14:30:00"
#     result = get_top_transactions(date_time)
#     print(result)
