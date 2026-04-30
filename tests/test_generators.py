import pytest

from typing import List, Dict, Any, Iterator

from src.generators import filter_by_currency, transaction_descriptions, card_number_generator


# Тестирование функции filter_by_currency
# Фикстуры
@pytest.fixture
def sample_transactions() -> List[Dict[str, Any]]:
    """Фикстура с примерами транзакций"""
    return [
        {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},
        {"id": 2, "operationAmount": {"currency": {"code": "EUR"}}},
        {"id": 3, "operationAmount": {"currency": {"code": "USD"}}},
        {"id": 4, "operationAmount": {"currency": {"code": "RUB"}}},
    ]


@pytest.fixture
def malformed_transactions() -> List[Any]:
    """Фикстура с некорректными транзакциями"""
    return [
        "not a dict",  # не словарь
        {"id": 1},  # нет operationAmount
        {"id": 2, "operationAmount": "not a dict"},  # operationAmount не словарь
        {"id": 3, "operationAmount": {"currency": "not a dict"}},  # currency не словарь
        {"id": 4, "operationAmount": {"currency": {}}},  # нет code
        {"id": 5, "operationAmount": {"currency": {"code": "USD"}}},  # корректный
        {"id": 6, "operationAmount": {"currency": {"code": "EUR"}}},  # корректный
    ]


@pytest.fixture
def empty_transactions() -> List[Dict[str, Any]]:
    """Фикстура с пустым списком транзакций"""
    return []


# Тесты
def test_filter_by_currency_basic(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тестирует фильтрацию по валюте"""
    result: List[Dict[str, Any]] = list(filter_by_currency(sample_transactions, "USD"))

    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 3


def test_filter_by_currency_no_matches(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тестирует при отсутствии совпадений"""
    result: List[Dict[str, Any]] = list(filter_by_currency(sample_transactions, "GBP"))

    assert result == []


def test_filter_by_currency_empty_list(empty_transactions: List[Dict[str, Any]]) -> None:
    """Тестирует при пустом списке"""
    result: List[Dict[str, Any]] = list(filter_by_currency(empty_transactions, "USD"))
    assert result == []


def test_filter_by_currency_returns_iterator(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тестирует на возврат итератора"""
    iterator: Iterator = filter_by_currency(sample_transactions, "USD")

    # Проверяем, что у объекта есть метод __next__ (признак итератора)
    assert hasattr(iterator, '__next__')

    # Или проверяем тип через collections.abc
    from collections.abc import Iterator
    assert isinstance(iterator, Iterator)

    assert next(iterator)["id"] == 1
    assert next(iterator)["id"] == 3
    with pytest.raises(StopIteration):
        next(iterator)


def test_filter_by_currency_case_sensitive() -> None:
    """Тестирует на чувствительность к регистру"""
    transactions: List[Dict[str, Any]] = [
        {"id": 1, "operationAmount": {"currency": {"code": "usd"}}},
        {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
        {"id": 3, "operationAmount": {"currency": {"code": "UsD"}}},
    ]

    result: List[Dict[str, Any]] = list(filter_by_currency(transactions, "USD"))

    assert len(result) == 1
    assert result[0]["id"] == 2


def test_filter_by_currency_malformed_data(malformed_transactions: List[Any]) -> None:
    """Тестирует на ввод некорректных данных"""
    result: List[Dict[str, Any]] = list(filter_by_currency(malformed_transactions, "USD"))

    # Должны быть только корректные транзакции с USD
    assert len(result) == 1
    assert result[0]["id"] == 5


def test_filter_by_currency_all_malformed() -> None:
    """Тестирует когда все транзакции некорректные"""
    transactions: List[Any] = [
        "not a dict",
        {"id": 1},
        {"id": 2, "operationAmount": "wrong"},
        {"id": 3, "operationAmount": {"currency": "wrong"}},
        {"id": 4, "operationAmount": {"currency": {}}},
    ]

    result: List[Dict[str, Any]] = list(filter_by_currency(transactions, "USD"))
    assert result == []


def test_filter_by_currency_invalid_inputs() -> None:
    """Тестирует на неверные типы входных параметров"""
    # Неверный тип transactions
    with pytest.raises(TypeError, match="Неправильный тип данных в transactions"):
        list(filter_by_currency("not a list", "USD"))  # type: ignore

    # Неверный тип currency_code
    with pytest.raises(TypeError, match="Неправильный тип данных в currency_code"):
        list(filter_by_currency([], 123))  # type: ignore

    # Пустая строка currency_code
    with pytest.raises(ValueError, match="Не введены данные по фильтрации"):
        list(filter_by_currency([], ""))


def test_filter_by_currency_none_inputs() -> None:
    """Тестирует с None в качестве входных параметров"""
    with pytest.raises(TypeError, match="Неправильный тип данных в transactions"):
        list(filter_by_currency(None, "USD"))  # type: ignore

    with pytest.raises(TypeError, match="Неправильный тип данных в currency_code"):
        list(filter_by_currency([], None))  # type: ignore


def test_filter_by_currency_missing_keys() -> None:
    """Тестирует транзакции с отсутствующими ключами"""
    transactions: List[Dict[str, Any]] = [
        {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},  # корректный
        {"id": 2},  # нет operationAmount
        {"id": 3, "operationAmount": {}},  # нет currency
        {"id": 4, "wrong_key": "value"},  # нет operationAmount
    ]

    result: List[Dict[str, Any]] = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_filter_by_currency_none_values() -> None:
    """Тестирует с None в значениях"""
    transactions: List[Dict[str, Any]] = [
        {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},
        {"id": 2, "operationAmount": None},
        {"id": 3, "operationAmount": {"currency": None}},
        {"id": 4, "operationAmount": {"currency": {"code": None}}},
    ]

    result: List[Dict[str, Any]] = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_filter_by_currency_lazy_evaluation(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тестирует ленивую (ленивую) оценку итератора"""
    iterator = filter_by_currency(sample_transactions, "USD")

    # Итератор должен быть создан сразу, но элементы не должны вычисляться до запроса
    assert iterator is not None

    # Поэлементное получение
    first = next(iterator)
    assert first["id"] == 1

    second = next(iterator)
    assert second["id"] == 3

    # Итератор должен истощиться
    with pytest.raises(StopIteration):
        next(iterator)


def test_filter_by_currency_multiple_iterations(sample_transactions: List[Dict[str, Any]]) -> None:
    """Тестирует множественные итерации (каждый раз новый итератор)"""
    # Первая итерация
    result1 = list(filter_by_currency(sample_transactions, "USD"))
    assert len(result1) == 2

    # Вторая итерация (должна дать тот же результат)
    result2 = list(filter_by_currency(sample_transactions, "USD"))
    assert len(result2) == 2

    # Результаты должны быть одинаковыми
    assert result1 == result2


@pytest.mark.parametrize(
    "currency,expected_ids",
    [
        ("USD", [1, 3]),
        ("EUR", [2]),
        ("RUB", [4]),
        ("GBP", []),
        ("usd", []),  # чувствительность к регистру
    ],
)
def test_filter_by_currency_parametrized(
        sample_transactions: List[Dict[str, Any]],
        currency: str,
        expected_ids: List[int]
) -> None:
    """Тестирует с параметризацией для разных валют"""
    result: List[Dict[str, Any]] = list(filter_by_currency(sample_transactions, currency))
    result_ids: List[int] = [t["id"] for t in result]
    assert result_ids == expected_ids


def test_filter_by_currency_whitespace_currency_code() -> None:
    """Тестирует с пробельными символами в коде валюты"""
    transactions: List[Dict[str, Any]] = [
        {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},
        {"id": 2, "operationAmount": {"currency": {"code": "USD "}}},
        {"id": 3, "operationAmount": {"currency": {"code": " USD"}}},
    ]

    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_filter_by_currency_exception_handling() -> None:
    """Тестирует обработку исключений (KeyError, TypeError, AttributeError)"""

    # Транзакции, которые вызовут различные исключения
    transactions = [
        # Корректная транзакция
        {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},

        # TypeError: operationAmount не словарь
        {"id": 2, "operationAmount": "not a dict"},

        # AttributeError: у строки нет метода get
        {"id": 3, "operationAmount": {"currency": "not a dict"}},

        # KeyError: отсутствует ключ 'currency'
        {"id": 4, "operationAmount": {}},

        # KeyError: отсутствует ключ 'code'
        {"id": 5, "operationAmount": {"currency": {}}},

        # TypeError: сравнение int со str
        {"id": 6, "operationAmount": {"currency": {"code": 123}}},

        # Корректная транзакция
        {"id": 7, "operationAmount": {"currency": {"code": "USD"}}},
    ]

    result = list(filter_by_currency(transactions, "USD"))

    # Должны быть только корректные транзакции (id 1 и 7)
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 7

# Тестирование функции transaction_descriptions
# Фикстуры
@pytest.fixture
def normal_transactions() -> List[Dict[str, str]]:
    """Фикстура с нормальными транзакциями"""
    return [
        {"description": "Покупка продуктов"},
        {"description": "Оплата коммунальных услуг"},
        {"description": "Перевод другу"},
    ]


@pytest.fixture
def single_transaction() -> List[Dict[str, str]]:
    """Фикстура с одной транзакцией"""
    return [{"description": "Единственная транзакция"}]


@pytest.fixture
def empty_transactions() -> List[Dict]:
    """Фикстура с пустым списком"""
    return []


@pytest.fixture
def transactions_missing_key() -> List[Dict[str, Any]]:
    """Фикстура с транзакциями, где отсутствует ключ description"""
    return [
        {"description": "Нормальная транзакция"},
        {"amount": 1000},  # Нет description
        {"description": "Еще одна нормальная"},
    ]


@pytest.fixture
def transactions_with_non_dict() -> List:
    """Фикстура со списком, содержащим не словарь"""
    return [{"description": "OK"}, "not a dict", {"description": "OK"}]


# Тесты
def test_transaction_descriptions_normal_case(normal_transactions: List[Dict[str, str]]) -> None:
    """Тестирует на получение описаний транзакций"""
    result = list(transaction_descriptions(normal_transactions))
    assert result == ["Покупка продуктов", "Оплата коммунальных услуг", "Перевод другу"]


def test_transaction_descriptions_empty_list(empty_transactions: List[Dict]) -> None:
    """Тестирует при пустом списке транзакций"""
    result = list(transaction_descriptions(empty_transactions))
    assert result == []


def test_transaction_descriptions_single_transaction(single_transaction: List[Dict[str, str]]) -> None:
    """Тестирует при вводе данных с одной транзакцией"""
    result = list(transaction_descriptions(single_transaction))
    assert result == ["Единственная транзакция"]


def test_transaction_descriptions_missing_key(transactions_missing_key: List[Dict[str, Any]]) -> None:
    """Тестирует при отсутствии ключа 'description' в транзакции"""
    with pytest.raises(KeyError, match="отсутствует ключ 'description'"):
        list(transaction_descriptions(transactions_missing_key))


def test_transaction_descriptions_not_a_list() -> None:
    """Тестирует при вводе, если передан не список"""
    with pytest.raises(TypeError, match="transactions должен быть списком"):
        list(transaction_descriptions("not a list"))  # type: ignore

    with pytest.raises(TypeError, match="transactions должен быть списком"):
        list(transaction_descriptions(None))  # type: ignore

    with pytest.raises(TypeError, match="transactions должен быть списком"):
        list(transaction_descriptions({"key": "value"}))  # type: ignore


def test_transaction_descriptions_element_not_dict(transactions_with_non_dict: List) -> None:
    """Тестирует работу, если элемент списка не является словарем"""
    with pytest.raises(TypeError, match="Каждая транзакция должна быть словарем"):
        list(transaction_descriptions(transactions_with_non_dict))  # type: ignore


def test_transaction_descriptions_iterator_property() -> None:
    """Тестирует, что функция возвращает итератор"""
    transactions = [{"description": "test"}]
    result = transaction_descriptions(transactions)

    # Проверяем, что результат является генератором/итератором
    # Генераторы имеют методы __iter__ и __next__
    assert hasattr(result, '__iter__')
    assert hasattr(result, '__next__')

    # Проверяем, что это действительно итератор, вызвав next()
    assert next(result) == "test"

    # Проверяем, что после исчерпания генератор выбрасывает StopIteration
    with pytest.raises(StopIteration):
        next(result)


def test_transaction_descriptions_lazy_evaluation() -> None:
    """Тестирует ленивую выгрузку данных (генератор)"""
    transactions = [
        {"description": "Первый"},
        {"description": "Второй"},
        {"description": "Третий"},
    ]

    result = transaction_descriptions(transactions)

    # Постепенное получение значений
    assert next(result) == "Первый"
    assert next(result) == "Второй"
    assert next(result) == "Третий"

    # Проверка, что генератор исчерпан
    with pytest.raises(StopIteration):
        next(result)


def test_transaction_descriptions_exception_stops_iteration(transactions_missing_key: List[Dict[str, Any]]) -> None:
    """Тестирует, что при возникновении ошибки итерация прекращается"""
    gen = transaction_descriptions(transactions_missing_key)

    # Первая транзакция нормальная
    assert next(gen) == "Нормальная транзакция"

    # Вторая транзакция вызывает ошибку
    with pytest.raises(KeyError, match="отсутствует ключ 'description'"):
        next(gen)


def test_transaction_descriptions_different_description_types() -> None:
    """Тестирует различные типы значений description"""
    transactions: List[Dict[str, Any]] = [
        {"description": "Обычная строка"},
        {"description": 12345},  # Число
        {"description": 45.67},  # Число с плавающей точкой
        {"description": True},  # Булево значение
        {"description": None},  # None
    ]

    result = list(transaction_descriptions(transactions))
    assert result == ["Обычная строка", 12345, 45.67, True, None]


def test_transaction_descriptions_with_additional_keys() -> None:
    """Тестирует транзакции с дополнительными ключами"""
    transactions: List[Dict[str, Any]] = [
        {"description": "Покупка", "amount": 1000, "date": "2024-01-01"},
        {"description": "Оплата", "amount": 500, "category": "services"},
        {"description": "Перевод", "recipient": "Друг"},
    ]

    result = list(transaction_descriptions(transactions))
    assert result == ["Покупка", "Оплата", "Перевод"]


# Параметризованные тесты
@pytest.mark.parametrize("invalid_input", [
    123,  # число
    45.67,  # float
    True,  # boolean
    None,  # None
    {"key": "value"},  # словарь
])
def test_transaction_descriptions_invalid_input_types(invalid_input) -> None:
    """Параметризованный тест для различных неверных типов ввода"""
    with pytest.raises(TypeError, match="transactions должен быть списком"):
        list(transaction_descriptions(invalid_input))  # type: ignore


@pytest.mark.parametrize("test_input,expected", [
    ([{"description": "A"}, {"description": "B"}], ["A", "B"]),
    ([{"description": "X"}], ["X"]),
    ([], []),
    ([{"description": ""}], [""]),  # пустая строка
    ([{"description": "   "}], ["   "]),  # пробелы
])
def test_transaction_descriptions_parametrized(test_input: List[Dict[str, str]], expected: List[str]) -> None:
    """Параметризованный тест для различных корректных сценариев"""
    result = list(transaction_descriptions(test_input))
    assert result == expected


# Тестирование функции card_number_generator
# Фикстуры
@pytest.fixture
def max_card_number() -> int:
    """Максимально допустимый номер карты"""
    return 10 ** 16 - 1


@pytest.fixture
def valid_range_small() -> tuple[int, int]:
    """Небольшой валидный диапазон"""
    return (0, 0)


@pytest.fixture
def valid_range_sequence() -> tuple[int, int]:
    """Диапазон из нескольких последовательных чисел"""
    return (1, 3)


@pytest.fixture
def valid_range_with_padding() -> tuple[int, int]:
    """Диапазон, требующий разного форматирования"""
    return (999, 1002)


@pytest.fixture
def valid_large_range() -> tuple[int, int]:
    """Большой диапазон для проверки генерации"""
    return (1_000_000, 1_000_005)


@pytest.fixture
def invalid_range_start_greater() -> tuple[int, int]:
    """Диапазон с start > fin"""
    return (10, 5)


@pytest.fixture
def invalid_range_negative_start() -> tuple[int, int]:
    """Диапазон с отрицательным start"""
    return (-1, 5)


@pytest.fixture
def invalid_range_exceeds_max(max_card_number: int) -> tuple[int, int]:
    """Диапазон с fin превышающим максимум"""
    return (max_card_number, max_card_number + 1)


@pytest.fixture
def edge_max_range(max_card_number: int) -> tuple[int, int]:
    """Граничный диапазон на максимуме"""
    return (max_card_number - 2, max_card_number)


@pytest.fixture
def edge_zero_range() -> tuple[int, int]:
    """Граничный диапазон у нуля"""
    return (0, 2)


# Тесты
def test_generator_returns_valid_card_number(valid_range_small: tuple[int, int]) -> None:
    """Тестирует генерацию корректного номера карты для одного значения"""
    start, fin = valid_range_small
    generator: Iterator[str] = card_number_generator(start, fin)
    result: str = next(generator)

    assert result == "0000 0000 0000 0000"
    assert len(result.replace(" ", "")) == 16


def test_generator_returns_range_of_numbers(valid_range_sequence: tuple[int, int]) -> None:
    """Тестирует генерацию диапазона номеров"""
    start, fin = valid_range_sequence
    generator: Iterator[str] = card_number_generator(start, fin)
    results: list[str] = list(generator)

    expected: list[str] = ["0000 0000 0000 0001", "0000 0000 0000 0002", "0000 0000 0000 0003"]
    assert results == expected


def test_generator_handles_numbers_with_different_length(valid_range_with_padding: tuple[int, int]) -> None:
    """Тестирует генерацию номеров с разным количеством цифр"""
    start, fin = valid_range_with_padding
    generator: Iterator[str] = card_number_generator(start, fin)
    results: list[str] = list(generator)

    assert results[0] == "0000 0000 0000 0999"
    assert results[1] == "0000 0000 0000 1000"
    assert results[2] == "0000 0000 0000 1001"
    assert results[3] == "0000 0000 0000 1002"


def test_generator_handles_large_numbers(valid_large_range: tuple[int, int]) -> None:
    """Тестирует генерацию для больших чисел"""
    start, fin = valid_large_range
    generator: Iterator[str] = card_number_generator(start, fin)
    results: list[str] = list(generator)

    # 1 000 000 = 0000 0000 0100 0000 (16 цифр)
    assert results[0] == "0000 0000 0100 0000"
    assert results[1] == "0000 0000 0100 0001"
    assert results[2] == "0000 0000 0100 0002"
    assert results[3] == "0000 0000 0100 0003"
    assert results[4] == "0000 0000 0100 0004"
    assert results[5] == "0000 0000 0100 0005"


def test_generator_raises_error_when_start_greater_than_fin(invalid_range_start_greater: tuple[int, int]) -> None:
    """Тестирует на ошибку при start > fin"""
    start, fin = invalid_range_start_greater
    with pytest.raises(ValueError, match="start должно быть меньше или равно fin"):
        list(card_number_generator(start, fin))


def test_generator_raises_error_when_negative_start(invalid_range_negative_start: tuple[int, int]) -> None:
    """Тестирует на ошибку при отрицательном start"""
    start, fin = invalid_range_negative_start
    with pytest.raises(ValueError, match="start не может быть отрицательным"):
        list(card_number_generator(start, fin))


def test_generator_raises_error_when_exceeds_maximum(invalid_range_exceeds_max: tuple[int, int]) -> None:
    """Тестирует на ошибку при превышении максимального допустимого значения"""
    start, fin = invalid_range_exceeds_max
    with pytest.raises(ValueError, match="fin не может превышать"):
        list(card_number_generator(start, fin))


def test_generator_works_at_maximum_boundary(edge_max_range: tuple[int, int], max_card_number: int) -> None:
    """Тестирует работу на границе максимального значения"""
    start, fin = edge_max_range
    generator: Iterator[str] = card_number_generator(start, fin)
    results: list[str] = list(generator)

    expected_last = " ".join(f"{max_card_number:016d}"[i:i + 4] for i in range(0, 16, 4))
    assert len(results) == 3
    assert results[-1] == expected_last


def test_generator_works_at_zero_boundary(edge_zero_range: tuple[int, int]) -> None:
    """Тестирует работу на границе нулевого значения"""
    start, fin = edge_zero_range
    generator: Iterator[str] = card_number_generator(start, fin)
    results: list[str] = list(generator)

    assert results[0] == "0000 0000 0000 0000"
    assert results[1] == "0000 0000 0000 0001"
    assert results[2] == "0000 0000 0000 0002"


def test_generator_yields_correct_number_of_items(valid_range_sequence: tuple[int, int]) -> None:
    """Тестирует, что генератор возвращает правильное количество элементов"""
    start, fin = valid_range_sequence
    generator: Iterator[str] = card_number_generator(start, fin)
    results: list[str] = list(generator)

    expected_count = fin - start + 1
    assert len(results) == expected_count


def test_generator_handles_single_element_range() -> None:
    """Тестирует диапазон из одного элемента"""
    generator: Iterator[str] = card_number_generator(42, 42)
    result: str = next(generator)

    assert result == "0000 0000 0000 0042"


def test_generator_raises_error_when_start_equal_fin_but_invalid() -> None:
    """Тестирует ошибку при start = fin, но start отрицательный"""
    with pytest.raises(ValueError, match="start не может быть отрицательным"):
        list(card_number_generator(-5, -5))


def test_generator_handles_maximum_possible_range(max_card_number: int) -> None:
    """Тестирует максимально возможный диапазон"""
    start = 0
    fin = max_card_number
    generator: Iterator[str] = card_number_generator(start, fin)

    # Проверяем первые 5 элементов
    for i, value in enumerate(generator):
        if i >= 5:
            break
        expected = " ".join(f"{i:016d}"[j:j + 4] for j in range(0, 16, 4))
        assert value == expected
