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

