import json
import logging
import os
import time

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

        print(settings)  # Вывод для отладки

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


def get_exchange_rates():
    """Получает данных о курсах валют с использованием API"""

    user_settings = get_load_user_setting()  # Вызываем функцию для загрузки настроек
    if not user_settings:
        return None

    user_currencies = user_settings.get("user_currencies", [])  # Получаем список валют из настроек
    exchange_rates = []

    api_key = os.getenv("API_KEY")  # Получаем API-ключ

    if not api_key:
        logging.error("Ошибка: API-ключ не установлен.")
        return None

    base_currency = "RUB"
    symbols = ",".join(user_currencies)
    api_url = f"https://api.apilayer.com/exchangerates_data/latest?symbols={symbols}&base={base_currency}"
    headers = {"apikey": api_key}

    try:
        response = requests.get(api_url, headers=headers)  # Отправляем get-запрос к API
        response.raise_for_status()  # Проверка успешности запроса
        data = response.json()  # Парсим JSON-ответ

        for currency in user_currencies:
            if currency in data["rates"]:
                exchange_rates.append({"currency": currency, "rate": data["rates"][currency]})
        logging.info(f"Курсы валют успешно получены: {exchange_rates}")
        return exchange_rates

    except requests.exceptions.RequestException as e:  # Обработка исключений
        logging.error(f"Ошибка при запросе к API: {e}")
        return None
    except KeyError as e:
        logging.error(f"Ошибка при обработке данных API: {e}")
        return None


# if __name__ == "__main__":
#     rates = get_exchange_rates()
#     if rates:
#         print("Полученные курсы валют:")
#         for rate in rates:
#             print(f"{{\n  \"currency\": \"{rate['currency']}\",\n  \"rate\": {rate['rate']}\n}}")
#     else:
#         print("Не удалось получить курсы валют.")


def get_stock_prices(api_key: str, settings_file: str, date: str) -> dict:
    """Получает цены на акции на определенную дату"""
    # Загрузка настроек пользователя
    user_settings = get_load_user_setting(settings_file)
    if not user_settings:
        return []

    # Получение списка символов акций из настроек
    user_stocks = user_settings.get("user_stocks", [])
    prices = []

    # URL для запроса
    url = "https://www.alphavantage.co/query"

    for symbol in user_stocks:
        params = {"function": "TIME_SERIES_DAILY", "symbol": symbol, "apikey": api_key}

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()

            # Логирование полного ответа для отладки
            logger.debug(f"Ответ от API для {symbol}: {data}")

            # Проверка наличия данных и обработки ошибок
            if "Time Series (Daily)" in data:
                time_series = data["Time Series (Daily)"]
                if date in time_series:
                    price = float(time_series[date]["4. close"])  # Цена закрытия
                    prices.append({"stock": symbol, "price": price})
                else:
                    logger.warning(f"Нет данных для {symbol} на дату {date}")
            elif "Information" in data:
                error_message = data["Information"]
                logger.error(f"Ошибка в данных для {symbol}: {error_message}")
            else:
                error_message = data.get("Error Message", "Неизвестная ошибка")
                logger.error(f"Ошибка в данных для {symbol}: {error_message}")

        except requests.exceptions.RequestException as e:
            logger.error(f"Ошибка запроса для {symbol}: {e}")
            # В случае сетевой ошибки, подождите перед следующим запросом
            time.sleep(1)

    return prices


# if __name__ == "__main__":
#     api_key = "WBKGN6R9SFIZ499P"
#     settings_file = "../user_settings.json"
#     date = "2024-07-25"
#     stock_prices = get_stock_prices(api_key, settings_file, date)
#     if stock_prices:
#         print("Цены на акции на дату", date)
#         print(json.dumps(stock_prices, indent=4, ensure_ascii=False))
#     else:
#         print("Не удалось получить данные о ценах на акции.")
