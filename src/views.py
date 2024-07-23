from  datetime import datetime
import json
import os

import pandas as pd
import logging
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
    date_time_obj = datetime.strptime(date_time_str, "%Y-%m-%d %H:%M:%S") # Преобразование строки в объект datetime

    hour = date_time_obj.hour # Получение часа из объекта datetime

    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 22:
        return "Добрый вечер"
    else:
        return "Доброй ночи"

    return greeting


def analyze_transactions(file_name: str, date_time: str) -> str:
    """Анализирует транзакции из excel-файла и возвращает JSON-ответ"""
    try:
        transactions_data = read_excel_file(file_name)

        if not transactions_data:
            logger.error(f"Нет данных для анализа в файле {file_name}.")
            return json.dumps({"error": f"Нет данных для анализа в файле {file_name}"}, ensure_ascii=False)

        logger.info(f"Начинаем анализ транзакций из файла {file_name}.")

        df = pd.DataFrame(transactions_data)

        # Последние 4 цифры номера карты
        last_digits = df.iloc[0]["Номер карты"][-4:] if not df.empty and "Номер карты" in df else ""

        # Общая сумма расходов
        total_spent = abs(df[df["Сумма операции"] < 0]["Сумма операции"].sum()) if not df.empty and "Сумма операции" in df else 0

        # Вычисление кэшбэка
        cashback = total_spent / 100.0 # Вычисляем кэшбэк (1 рубль на каждые 100 рублей потраченных)

        result = {
            "last_digits": last_digits,
            "total_spent": float(total_spent),
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