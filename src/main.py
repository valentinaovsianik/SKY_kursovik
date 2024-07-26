import json
import logging
import os

from dotenv import load_dotenv

from src.utils import get_exchange_rates, get_stock_prices
from src.views import analyze_transactions, get_greeting, get_top_transactions

load_dotenv()

# Установка логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


