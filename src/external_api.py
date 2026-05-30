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

    # Поддержка двух форматов структуры транзакции
    if "operationAmount" in transaction:
        # Вложенная структура (как в требовании)
        operation_amount = transaction["operationAmount"]
        amount = operation_amount.get("amount")
        currency_info = operation_amount.get("currency")
        currency = currency_info.get("code", "").upper() if currency_info else ""
    else:
        # Плоская структура (как в тесте)
        amount = transaction.get("amount")
        currency = transaction.get("currency", "RUB").upper()

    # Проверки корректности входных данных
    if amount is None:
        raise KeyError("Не удалось найти сумму транзакции (ключ 'amount' или 'operationAmount.amount')")

    if not isinstance(amount, (int, float)):
        raise TypeError("Поле 'amount' должно быть числом")
    if amount < 0:
        raise ValueError("Сумма транзакции не может быть отрицательной")

    if not currency:
        raise KeyError("Не удалось найти валюту транзакции (ключ 'currency' или 'operationAmount.currency.code')")

    # Если рубли — возвращаем как есть
    if currency == "RUB":
        return float(amount)

    # Если USD или EUR — конвертируем
    if currency in ("USD", "EUR"):
        # Проверяем кэш
        if currency not in _cache:
            url = f"{BASE_URL}/latest"
            params = {"base": currency, "symbols": "RUB"}
            headers = {"apikey": API_KEY}

            try:
                response = requests.get(url, headers=headers, params=params, timeout=5)
                response.raise_for_status()
                data = response.json()

                if data.get("success"):
                    _cache[currency] = data["rates"]["RUB"]
                else:
                    # Обрабатываем ошибку API, которая может быть как строкой, так и словарем
                    error_info = data.get("error")
                    if isinstance(error_info, dict):
                        error_msg = error_info.get("info", "Unknown error")
                    else:
                        error_msg = str(error_info) if error_info else "Unknown error"
                    raise ValueError(f"API вернул ошибку: {error_msg}")

            except requests.exceptions.RequestException as e:
                raise ConnectionError(f"Не удалось получить курс валюты {currency}: {e}")

        rate = _cache[currency]
        return float(amount * rate)
    else:
        raise ValueError(f"Неподдерживаемая валюта: {currency}. Допустимы RUB, USD, EUR")
