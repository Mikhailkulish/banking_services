import pytest

from typing import List, Dict, Any, Iterator

from src.generators import filter_by_currency, transaction_descriptions, card_number_generator


# Тестирование функции filter_by_currency
def test_filter_by_currency_basic() -> None:
    """Тестирует фильтрацию по валюте"""
    transactions: List[Dict[str, Any]] = [
        {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},
        {"id": 2, "operationAmount": {"currency": {"code": "EUR"}}},
        {"id": 3, "operationAmount": {"currency": {"code": "USD"}}},
    ]

    result: List[Dict[str, Any]] = list(filter_by_currency(transactions, "USD"))

    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 3


def test_filter_by_currency_no_matches() -> None:
    """Тестирует при отсутствии совпадений"""
    transactions: List[Dict[str, Any]] = [
        {"id": 1, "operationAmount": {"currency": {"code": "EUR"}}},
        {"id": 2, "operationAmount": {"currency": {"code": "RUB"}}},
    ]

    result: List[Dict[str, Any]] = list(filter_by_currency(transactions, "USD"))

    assert result == []


def test_filter_by_currency_empty_list() -> None:
    """Тестирует при пустом списке"""
    result: List[Dict[str, Any]] = list(filter_by_currency([], "USD"))
    assert result == []


def test_filter_by_currency_returns_iterator() -> None:
    """Тестирует на возврат итератора"""
    transactions: List[Dict[str, Any]] = [
        {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},
        {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
    ]

    iterator: Iterator = filter_by_currency(transactions, "USD")

    assert next(iterator)["id"] == 1
    assert next(iterator)["id"] == 2
    with pytest.raises(StopIteration):
        next(iterator)


def test_filter_by_currency_case_sensitive() -> None:
    """Тестирует на чувствительность к регистру"""
    transactions: List[Dict[str, Any]] = [
        {"id": 1, "operationAmount": {"currency": {"code": "usd"}}},
        {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
    ]

    result: List[Dict[str, Any]] = list(filter_by_currency(transactions, "USD"))

    assert len(result) == 1
    assert result[0]["id"] == 2


def test_filter_by_currency_malformed_data() -> None:
    """Тестирует на ввод некорректных данных"""
    transactions: List[Any] = [
        {"id": 1},  # нет operationAmount
        {"id": 2, "operationAmount": "not a dict"},  # неправильный тип
        {"id": 3, "operationAmount": {"currency": {"code": "USD"}}},  # корректный
        {"id": 4, "operationAmount": {"currency": {}}},  # нет code
    ]

    result: List[Dict[str, Any]] = list(filter_by_currency(transactions, "USD"))

    assert len(result) == 1
    assert result[0]["id"] == 3


def test_filter_by_currency_invalid_inputs() -> None:
    """Тестирует на неверные типы входных параметров"""
    with pytest.raises(TypeError):
        list(filter_by_currency("not a list", "USD"))

    with pytest.raises(TypeError):
        list(filter_by_currency([], 123))

    with pytest.raises(ValueError):
        list(filter_by_currency([], ""))


@pytest.mark.parametrize("currency,expected_ids", [
    ("USD", [1, 3]),
    ("EUR", [2]),
    ("GBP", []),
])
def test_filter_by_currency_parametrized(currency: str, expected_ids: List[int]) -> None:
    """Тестирует с  параметризацией для разных валют"""
    transactions: List[Dict[str, Any]] = [
        {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},
        {"id": 2, "operationAmount": {"currency": {"code": "EUR"}}},
        {"id": 3, "operationAmount": {"currency": {"code": "USD"}}},
    ]

    result: List[Dict[str, Any]] = list(filter_by_currency(transactions, currency))
    result_ids: List[int] = [t["id"] for t in result]

    assert result_ids == expected_ids


# Тестирование функции transaction_descriptions
def test_transaction_descriptions_normal_case() -> None:
    """Тестирует на получение описаний транзакций"""
    transactions: List[Dict[str, str]] = [
        {"description": "Покупка продуктов"},
        {"description": "Оплата коммунальных услуг"},
        {"description": "Перевод другу"}
    ]

    result = list(transaction_descriptions(transactions))

    assert result == ["Покупка продуктов", "Оплата коммунальных услуг", "Перевод другу"]


def test_transaction_descriptions_empty_list() -> None:
    """Тестирует при пустом списке транзакций"""
    transactions: List[Dict] = []

    result = list(transaction_descriptions(transactions))

    assert result == []


def test_transaction_descriptions_single_transaction() -> None:
    """Тестирует при вводе данных с одной транзакцией"""
    transactions: List[Dict[str, str]] = [
        {"description": "Единственная транзакция"}
    ]

    result = list(transaction_descriptions(transactions))

    assert result == ["Единственная транзакция"]


def test_transaction_descriptions_missing_key() -> None:
    """Тестирует при отсутствии ключа 'description' в транзакции"""
    transactions: List[Dict[str, Any]] = [
        {"description": "Нормальная транзакция"},
        {"amount": 1000},  # Нет description
        {"description": "Еще одна нормальная"}
    ]

    with pytest.raises(KeyError, match="отсутствует ключ 'description'"):
        list(transaction_descriptions(transactions))


def test_transaction_descriptions_not_a_list() -> None:
    """Тестирует при вводе, если передан не список"""
    with pytest.raises(TypeError, match="transactions должен быть списком"):
        list(transaction_descriptions("not a list"))


def test_transaction_descriptions_element_not_dict() -> None:
    """Тестирует работу, если элемент списка не является словарем"""
    transactions = [
        {"description": "OK"},
        "not a dict",  # type: ignore
        {"description": "OK"}
    ]

    with pytest.raises(TypeError, match="Каждая транзакция должна быть словарем"):
        list(transaction_descriptions(transactions))


# Тестирование функции card_number_generator
def test_generator_returns_valid_card_number() -> None:
    """Тестирует генерацию корректного номера карты для одного значения"""
    generator: Iterator[str] = card_number_generator(0, 0)
    result: str = next(generator)

    assert result == "0000 0000 0000 0000"
    assert len(result.replace(" ", "")) == 16


def test_generator_returns_range_of_numbers() -> None:
    """Тестирует генерацию диапазона номеров"""
    generator: Iterator[str] = card_number_generator(1, 3)
    results: list[str] = list(generator)

    expected: list[str] = [
        "0000 0000 0000 0001",
        "0000 0000 0000 0002",
        "0000 0000 0000 0003"
    ]
    assert results == expected


def test_generator_handles_large_numbers() -> None:
    """Тестирует генерацию номеров с разным количеством цифр"""
    generator: Iterator[str] = card_number_generator(999, 1002)
    results: list[str] = list(generator)

    assert results[0] == "0000 0000 0000 0999"
    assert results[1] == "0000 0000 0000 1000"
    assert results[2] == "0000 0000 0000 1001"
    assert results[3] == "0000 0000 0000 1002"


def test_generator_raises_error_when_start_greater_than_fin() -> None:
    """Тестирует на ошибку при start > fin"""
    with pytest.raises(ValueError, match="start должно быть меньше или равно fin"):
        list(card_number_generator(10, 5))


def test_generator_raises_error_when_negative_start() -> None:
    """Тестирует на ошибку при отрицательном start"""
    with pytest.raises(ValueError, match="start не может быть отрицательным"):
        list(card_number_generator(-1, 5))


def test_generator_raises_error_when_exceeds_maximum() -> None:
    """Тестирует на ошибку при превышении максимального допустимого значения"""
    max_card: int = 10 ** 16 - 1
    with pytest.raises(ValueError, match="fin не может превышать"):
        list(card_number_generator(max_card, max_card + 1))
