from typing import Iterator, Dict, Any, List


def filter_by_currency(transactions: List[Dict[str, Any]], currency_code: str) -> Iterator[Dict[str, Any]]:
    """Выдает итератор для фильтрации списка словарей с информацией о транзакциях по валюте"""
    if not isinstance(transactions, list):
        raise TypeError("Неправильный тип данных в transactions")

    if not isinstance(currency_code, str):
        raise TypeError("Неправильный тип данных в currency_code")

    if not currency_code:
        raise ValueError("Не введены данные по фильтрации")

    for transaction in transactions:
        if not isinstance(transaction, dict):
            continue

        try:
            operation_amount = transaction.get("operationAmount")
            if not isinstance(operation_amount, dict):
                continue

            currency = operation_amount.get("currency")
            if not isinstance(currency, dict):
                continue

            code = currency.get("code")

            if code == currency_code:
                yield transaction

        except KeyError, TypeError, AttributeError:
            # Пропускаем транзакции с некорректной структурой
            continue


def transaction_descriptions(transactions: List[Dict[str, Any]]) -> Iterator[str]:
    """Поочередно возвращает описание транзакций"""
    if not isinstance(transactions, list):
        raise TypeError("transactions должен быть списком")

    for transaction in transactions:
        if not isinstance(transaction, dict):
            raise TypeError("Каждая транзакция должна быть словарем")
        if "description" not in transaction:
            raise KeyError(f"В транзакции {transaction} отсутствует ключ 'description'")
        yield transaction["description"]


def card_number_generator(start: int, fin: int) -> Iterator[str]:
    "Генерирует номера карт в заданном диапазоне значений"
    MAX_CARD_NUMBER = 10**16 - 1

    if start > fin:
        raise ValueError("start должно быть меньше или равно fin")

    if start < 0:
        raise ValueError("start не может быть отрицательным")

    if fin > MAX_CARD_NUMBER:
        raise ValueError(f"fin не может превышать {MAX_CARD_NUMBER}")

    for number in range(start, fin + 1):
        num_str = str(number)
        formatted = "0" * (16 - len(num_str)) + num_str
        card_number = " ".join(formatted[i : i + 4] for i in range(0, 16, 4))
        yield card_number
