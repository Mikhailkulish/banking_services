import os
import requests
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv()

API_KEY = os.getenv('EXCHANGE_RATES_API_KEY')
BASE_URL = "https://api.apilayer.com/exchangerates_data"

_cache = {}


def get_exchange_rate(currency: str) -> float:
    """Запрашивает курс валюты для конвертации суммы в рублях"""
    if currency == "RUB":
        return 1.0

    # Проверяем кэш (в рамках одного запуска программы)
    if currency in _cache:
        return _cache[currency]

    headers = {"apikey": API_KEY}
    # Запрашиваем курс currency к RUB
    url = f"{BASE_URL}/latest"
    params = {
        "base": currency,  # базовая валюта — USD или EUR
        "symbols": "RUB"   # целевая валюта — RUB
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        response.raise_for_status()  # выбросит исключение при ошибке HTTP
        data = response.json()

        if data.get("success"):
            rate = data["rates"]["RUB"]  # сколько RUB за 1 currency
            _cache[currency] = rate
            return rate
        else:
            raise ValueError(f"API вернул ошибку: {data.get('error', 'Unknown error')}")

    except requests.exceptions.RequestException as e:
        raise ConnectionError(f"Не удалось получить курс валюты {currency}: {e}")


def convert_to_rub(transaction: dict) -> float:
    """Принимает транзакцию в виде словаря и возвращает сумму в рублях (float)"""
    amount = transaction.get('amount')
    currency = transaction.get('currency', 'RUB').upper()

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
        rate = get_exchange_rate(currency)  # сколько RUB за 1 USD/EUR
        return float(amount * rate)
    else:
        # В задании не сказано, как обрабатывать другие валюты, но можно добавить
        raise ValueError(f"Неподдерживаемая валюта: {currency}. Допустимы RUB, USD, EUR")
