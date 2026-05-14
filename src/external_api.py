import os
import requests
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

API_KEY = os.getenv("EXCHANGE_RATES_API_KEY")
BASE_URL = os.getenv("EXCHANGE_RATES_BASE_URL")

_cache = {}


def convert_to_rub(transaction: dict) -> float:
    """Принимает транзакцию в виде словаря и возвращает сумму в рублях"""
    amount = transaction.get("amount")
    currency = transaction.get("currency", "RUB").upper()

    # Проверки корректности входных данных
    if not isinstance(amount, (int, float)):
        raise TypeError("Поле 'amount' должно быть числом")
    if amount < 0:
        raise ValueError("Сумма транзакции не может быть отрицательной")

    # Если рубли — возвращаем как есть
    if currency == "RUB":
        return float(amount)

    # Если USD или EUR — конвертируем
    if currency in ("USD", "EUR"):
        # Проверяем кэш
        if currency not in _cache:
            headers = {"apikey": API_KEY}
            url = f"{BASE_URL}/latest"
            params = {"base": currency, "symbols": "RUB"}

            try:
                response = requests.get(url, headers=headers, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()

                if data.get("success"):
                    _cache[currency] = data["rates"]["RUB"]
                else:
                    raise ValueError(f"API вернул ошибку: {data.get('error', 'Unknown error')}")

            except requests.exceptions.RequestException as e:
                raise ConnectionError(f"Не удалось получить курс валюты {currency}: {e}")

        rate = _cache[currency]
        return float(amount * rate)
    else:
        raise ValueError(f"Неподдерживаемая валюта: {currency}. Допустимы RUB, USD, EUR")
