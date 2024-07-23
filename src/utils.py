import json
import os
import time

import logging
import requests

from dotenv import load_dotenv
load_dotenv()

log_dir = os.path.join(os.path.dirname(__file__), "..", "logs")

os.makedirs(log_dir, exist_ok=True)


# Настройка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Создание обработчика для записи в файл
file_handler = logging.FileHandler(os.path.join(log_dir, "utils.log"), encoding="utf-8")
file_handler.setLevel(logging.DEBUG)

# Форматтер сообщений
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
file_handler.setFormatter(formatter)

# Добавление обработчика к логгеру
logger.addHandler(file_handler)

def get_load_user_setting(file_path="../user_settings.json"):
    """Функция для загрузки пользовательских настроек из файла user_settings.json"""
    try:
        settings_file = os.path.abspath(file_path)

        with open(settings_file, "r", encoding="utf-8") as file:
            settings = json.load(file)
        logging.info(f"Настройки успешно загружены из {file_path}")

        print(settings) # Вывод для отладки

        return settings

    except FileNotFoundError:
        logging.error(f"Файл настроек не найден: {settings_file}")
        return None
    except Exception as e:
        logging.error(f"Ошибка при загрузке настроек: {e}")
        return None

# if __name__ == "__main__":
#     settings = get_load_user_setting()
#     if settings:
#         print("Настройки загружены:")
#         print(settings)
#     else:
#         print("Не удалось загрузить настройки.")




def get_load_user_setting(file_path="../user_settings.json"):
    """Функция для загрузки пользовательских настроек из файла user_settings.json"""
    try:
        settings_file = os.path.abspath(file_path)

        with open(settings_file, "r") as file:
            settings = json.load(file)
        logging.info(f"Настройки успешно загружены из {file_path}")
        return settings
    except Exception as e:
        logging.error(f"Ошибка при загрузке настроек: {e}")
        return None


def get_exchange_rates():
    """Получает данных о курсах валют с использованием API"""

    user_settings = get_load_user_setting() # Вызываем функцию для загрузки настроек
    if not user_settings:
        return None

    user_currencies = user_settings.get("user_currencies", [])  # Получаем список валют из настроек
    exchange_rates = []

    api_key = os.getenv("API_KEY")  # Получаем API-ключ

    if not api_key:
        logging.error("Ошибка: API-ключ не установлен.")
        return None

    base_currency = "RUB"
    api_url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={','.join(user_currencies)}&base={base_currency}"
    headers = {"apikey": api_key}

    try:
        response = requests.get(api_url, headers=headers) # Отправляем get-запрос к API
        response.raise_for_status() # Проверка успешности запроса
        data = response.json() # Парсим JSON-ответ

        for currency in user_currencies:
            if currency in data.get("rates", {}):
                exchange_rates.append({
                "currency": currency,
                "rate": data["rates"][currency]
            })
        logging.info(f"Курсы валют успешно получены: {exchange_rates}")
        return exchange_rates

    except requests.exceptions.RequestException as e: # Обработка исключений
        logging.error(f"Ошибка при запросе к API: {e}")
        return None
    except KeyError as e:
        logging.error(f"Ошибка при обработке данных API: {e}")
        return None

if __name__ == "__main__":
    rates = get_exchange_rates()
    if rates:
        print("Полученные курсы валют:")
        for rate in rates:
            print(f"{rate['currency']}: {rate['rate']}")
    else:
        print("Не удалось получить курсы валют.")




