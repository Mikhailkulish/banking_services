def filter_by_currency(transactions: list[dict], currency_code: str) -> iter:
    """Выдает итератор для фильтрации списка словарей с информацией о транзакциях по валюте"""
    for transaction in transactions:
        if transaction["operationAmount"]["currency"]["code"] == currency_code:
            yield transaction


def transaction_descriptions(transactions: list[dict]) -> list:
    """Поочередно возвращает описание транзакций"""
    for transaction in transactions:
        yield transaction['description']


def card_number_generator(start: int, fin: int) -> str:
    "Генерирует номера карт в заданном диапазоне значений"
    for number in range(start, fin + 1):
        num_str = str(number)
        formatted = "0" * (16 - len(num_str)) + num_str
        card_number = " ".join(formatted[i:i + 4] for i in range(0, 16, 4))
        yield card_number
