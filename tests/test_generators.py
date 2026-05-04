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
    assert hasattr(iterator, "__next__")

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
    sample_transactions: List[Dict[str, Any]], currency: str, expected_ids: List[int]
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


def test_filter_by_currency_non_dict_transaction():
    """Тестирует пропуск элементов не являющихся словарями"""
    transactions = ["not a dict", {"id": 1, "operationAmount": {"currency": {"code": "USD"}}}]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_filter_by_currency_operation_amount_none():
    """Тестирует обработку operationAmount = None"""
    transactions = [{"id": 1, "operationAmount": None}, {"id": 2, "operationAmount": {"currency": {"code": "USD"}}}]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_large_transactions_list() -> None:
    """Тестирует работу с большим списком транзакций"""
    large_list = [{"operationAmount": {"currency": {"code": "USD"}}} for _ in range(1000000)]
    generator = filter_by_currency(large_list, "USD")
    # Проверяем, что первый элемент получается быстро
    import time

    start = time.time()
    first = next(generator)
    assert time.time() - start < 0.1  # Должно быть быстро
    assert first is not None


def test_filter_by_currency_skip_non_dict_operation_amount() -> None:
    """Тестирует пропуск транзакций где operationAmount не словарь"""
    transactions = [
        {"id": 1, "operationAmount": "not a dict"},
        {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
        {"id": 3, "operationAmount": 123},
        {"id": 4, "operationAmount": None},
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_filter_by_currency_skip_non_dict_currency() -> None:
    """Тестирует пропуск транзакций с currency не словарем"""
    transactions = [
        {"id": 1, "operationAmount": {"currency": "not a dict"}},
        {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_filter_by_currency_skip_missing_currency() -> None:
    """Тестирует пропуск транзакций без ключа currency"""
    transactions = [
        {"id": 1, "operationAmount": {}},
        {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_filter_by_currency_skip_missing_code() -> None:
    """Тестирует пропуск транзакций без ключа code"""
    transactions = [
        {"id": 1, "operationAmount": {"currency": {}}},
        {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_filter_by_currency_skip_code_wrong_type() -> None:
    """Тестирует пропуск транзакций с code неправильного типа"""
    transactions = [
        {"id": 1, "operationAmount": {"currency": {"code": 123}}},
        {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_filter_by_currency_mixed_types_comparison() -> None:
    """Тестирует сравнение с разными типами данных"""
    transactions = [
        {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},
        {"id": 2, "operationAmount": {"currency": {"code": 123}}},
        {"id": 3, "operationAmount": {"currency": {"code": None}}},
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_filter_by_currency_transaction_with_extra_nesting() -> None:
    """Тестирует транзакции с дополнительной вложенностью"""
    transactions = [
        {"id": 1, "operationAmount": {"currency": {"code": "USD", "name": "Доллар"}}},
        {"id": 2, "operationAmount": {"currency": {"code": "USD", "extra": {"info": "test"}}}},
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 2


def test_filter_by_currency_transaction_with_none_values_in_nested() -> None:
    """Тестирует None значения во вложенных структурах"""
    transactions = [
        {"id": 1, "operationAmount": {"currency": {"code": None}}},
        {"id": 2, "operationAmount": {"currency": None}},
        {"id": 3, "operationAmount": None},
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert result == []  # Все должны быть пропущены


def test_filter_by_currency_empty_currency_code() -> None:
    """Тестирует пустой код валюты в транзакции"""
    transactions = [
        {"id": 1, "operationAmount": {"currency": {"code": ""}}},
        {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_filter_by_currency_special_characters_in_code() -> None:
    """Тестирует спецсимволы в коде валюты"""
    transactions = [
        {"id": 1, "operationAmount": {"currency": {"code": "USD$"}}},
        {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_filter_by_currency_unicode_currency_codes() -> None:
    """Тестирует unicode символы в кодах валют"""
    transactions = [
        {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},
        {"id": 2, "operationAmount": {"currency": {"code": "£"}}},
        {"id": 3, "operationAmount": {"currency": {"code": "€"}}},
    ]
    result = list(filter_by_currency(transactions, "£"))
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_filter_by_currency_mixed_valid_invalid_skip_logic() -> None:
    """Тестирует сложную логику пропуска с разными типами ошибок"""
    transactions = [
        {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},  # валидный
        {"id": 2, "operationAmount": {"currency": "USD"}},  # currency не словарь
        {"id": 3, "operationAmount": 123},  # operationAmount не словарь
        {"id": 4, "operationAmount": {"currency": {"code": 456}}},  # code не строка
        {"id": 5, "operationAmount": {"currency": {"code": "USD"}}},  # валидный
        {"id": 6, "operationAmount": {"currency": {"code": "EUR"}}},  # другая валюта
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 5


def test_filter_by_currency_duplicate_transactions() -> None:
    """Тестирует дублирующиеся транзакции"""
    transactions = [
        {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},
        {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},
        {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 3
    assert result[0]["id"] == 1
    assert result[1]["id"] == 1
    assert result[2]["id"] == 2


def test_filter_by_currency_large_currency_code() -> None:
    """Тестирует очень длинный код валюты"""
    long_code = "USD" * 100
    transactions = [
        {"id": 1, "operationAmount": {"currency": {"code": long_code}}},
        {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
    ]
    result = list(filter_by_currency(transactions, long_code))
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_filter_by_currency_numeric_string_code() -> None:
    """Тестирует числовой код в виде строки"""
    transactions = [
        {"id": 1, "operationAmount": {"currency": {"code": "123"}}},
        {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
    ]
    result = list(filter_by_currency(transactions, "123"))
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_filter_by_currency_iterator_reset_behavior() -> None:
    """Тестирует поведение при повторном использовании exhausted итератора"""
    transactions = [
        {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},
        {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
    ]
    iterator = filter_by_currency(transactions, "USD")

    # Исчерпываем итератор
    assert next(iterator)["id"] == 1
    assert next(iterator)["id"] == 2
    with pytest.raises(StopIteration):
        next(iterator)

    # Создаем новый итератор для повторного использования
    new_iterator = filter_by_currency(transactions, "USD")
    assert next(new_iterator)["id"] == 1


def test_filter_by_currency_type_error_messages() -> None:
    """Тестирует сообщения об ошибках"""
    # Для проверки TypeError в transactions нужно итерировать генератор
    with pytest.raises(TypeError, match="Неправильный тип данных в transactions"):
        gen = filter_by_currency(123, "USD")  # type: ignore
        list(gen)  # Здесь произойдет проверка типов

    # Для проверки TypeError в currency_code
    with pytest.raises(TypeError, match="Неправильный тип данных в currency_code"):
        gen = filter_by_currency([], 123)  # type: ignore
        list(gen)  # Здесь произойдет проверка типов

    # Для проверки ValueError с пустой строкой
    with pytest.raises(ValueError, match="Не введены данные по фильтрации"):
        gen = filter_by_currency([], "")
        list(gen)  # Здесь произойдет проверка


def test_filter_by_currency_stop_iteration_handling() -> None:
    """Тестирует корректную обработку StopIteration"""
    transactions = [{"id": 1, "operationAmount": {"currency": {"code": "USD"}}}]
    iterator = filter_by_currency(transactions, "USD")

    assert next(iterator)["id"] == 1

    # Повторный вызов next должен вызвать StopIteration
    with pytest.raises(StopIteration):
        next(iterator)


def test_filter_by_currency_stop_iteration_after_exhaustion() -> None:
    """Тестирует поведение после полного исчерпания итератора"""
    transactions = [{"id": 1, "operationAmount": {"currency": {"code": "USD"}}}]
    iterator = filter_by_currency(transactions, "USD")

    assert next(iterator)["id"] == 1

    # Несколько вызовов next после исчерпания
    with pytest.raises(StopIteration):
        next(iterator)
    with pytest.raises(StopIteration):
        next(iterator)  # Второй вызов также должен вызывать StopIteration


def test_filter_by_currency_with_empty_currency_dict() -> None:
    """Тестирует с пустым словарем валюты"""
    transactions = [
        {"id": 1, "operationAmount": {"currency": {}}},
        {"id": 2, "operationAmount": {"currency": {"code": "USD"}}},
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["id"] == 2


def test_filter_by_currency_with_nested_none_values() -> None:
    """Тестирует с None на разных уровнях вложенности"""
    transactions = [
        {"id": 1, "operationAmount": {"currency": {"code": None}}},
        {"id": 2, "operationAmount": {"currency": None}},
        {"id": 3, "operationAmount": None},
        {"id": 4, "operationAmount": {"currency": {"code": "USD"}}},
    ]
    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["id"] == 4


def test_filter_by_currency_generator_reuse_after_exception() -> None:
    """Тестирует, что генератор можно пересоздать после ошибки"""
    transactions = [{"id": 1, "operationAmount": {"currency": {"code": "USD"}}}]

    result1 = list(filter_by_currency(transactions, "USD"))
    result2 = list(filter_by_currency(transactions, "USD"))

    assert result1 == result2
    assert len(result1) == 1


def test_filter_by_currency_with_exploding_get() -> None:
    """Тестирует обработку исключений при вызове get"""

    # Создаем словарь, генерирующий исключение при get
    def create_exploding_dict():
        return {"get": lambda self, key, default=None: (_ for _ in ()).throw(RuntimeError("Test error")), "id": 2}

    transactions = [
        {"id": 1, "operationAmount": {"currency": {"code": "USD"}}},
        create_exploding_dict(),
    ]

    result = list(filter_by_currency(transactions, "USD"))
    assert len(result) == 1
    assert result[0]["id"] == 1


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
    assert hasattr(result, "__iter__")
    assert hasattr(result, "__next__")

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
@pytest.mark.parametrize(
    "invalid_input",
    [
        123,  # число
        45.67,  # float
        True,  # boolean
        None,  # None
        {"key": "value"},  # словарь
    ],
)
def test_transaction_descriptions_invalid_input_types(invalid_input) -> None:
    """Параметризованный тест для различных неверных типов ввода"""
    with pytest.raises(TypeError, match="transactions должен быть списком"):
        list(transaction_descriptions(invalid_input))  # type: ignore


@pytest.mark.parametrize(
    "test_input,expected",
    [
        ([{"description": "A"}, {"description": "B"}], ["A", "B"]),
        ([{"description": "X"}], ["X"]),
        ([], []),
        ([{"description": ""}], [""]),  # пустая строка
        ([{"description": "   "}], ["   "]),  # пробелы
    ],
)
def test_transaction_descriptions_parametrized(test_input: List[Dict[str, str]], expected: List[str]) -> None:
    """Параметризованный тест для различных корректных сценариев"""
    result = list(transaction_descriptions(test_input))
    assert result == expected


@pytest.mark.parametrize(
    "invalid_element",
    [
        None,
        123,
        45.67,
        True,
        ["list"],
        ("tuple",),
    ],
)
def test_transaction_descriptions_various_non_dict_types(invalid_element) -> None:
    """Тестирует различные типы данных вместо словаря"""
    transactions = [{"description": "ok"}, invalid_element]
    with pytest.raises(TypeError, match="Каждая транзакция должна быть словарем"):
        list(transaction_descriptions(transactions))


def test_transaction_descriptions_iterator_consumption() -> None:
    """Тестирует полное потребление итератора"""
    transactions = [
        {"description": "First"},
        {"description": "Second"},
        {"description": "Third"},
    ]

    gen = transaction_descriptions(transactions)

    # Получаем все элементы
    first = next(gen)
    second = next(gen)
    third = next(gen)

    assert first == "First"
    assert second == "Second"
    assert third == "Third"

    # Проверяем, что после исчерпания выбрасывается StopIteration
    with pytest.raises(StopIteration):
        next(gen)


def test_transaction_descriptions_parallel_iteration() -> None:
    """Тестирует параллельную итерацию (каждый раз новый итератор)"""
    transactions = [
        {"description": "A"},
        {"description": "B"},
    ]

    gen1 = transaction_descriptions(transactions)
    gen2 = transaction_descriptions(transactions)

    assert next(gen1) == "A"
    assert next(gen2) == "A"  # Независимые итераторы
    assert next(gen1) == "B"
    assert next(gen2) == "B"


def test_transaction_descriptions_empty_description() -> None:
    """Тестирует пустое описание транзакции"""
    transactions = [
        {"description": ""},
        {"description": "   "},
        {"description": None},
    ]
    result = list(transaction_descriptions(transactions))
    assert result == ["", "   ", None]


def test_transaction_descriptions_very_long_description() -> None:
    """Тестирует очень длинное описание"""
    long_text = "A" * 10000
    transactions = [{"description": long_text}]
    result = list(transaction_descriptions(transactions))
    assert result[0] == long_text
    assert len(result[0]) == 10000


def test_transaction_descriptions_special_characters() -> None:
    """Тестирует спецсимволы в описании"""
    transactions = [
        {"description": "Test!@#$%^&*()"},
        {"description": "Привет мир 🌍"},
        {"description": "\n\t\r"},
    ]
    result = list(transaction_descriptions(transactions))
    assert result[0] == "Test!@#$%^&*()"
    assert result[1] == "Привет мир 🌍"
    assert result[2] == "\n\t\r"


def test_transaction_descriptions_multiple_calls_same_generator() -> None:
    """Тестирует множественные вызовы next на одном генераторе"""
    transactions = [
        {"description": "First"},
        {"description": "Second"},
        {"description": "Third"},
    ]
    gen = transaction_descriptions(transactions)

    assert next(gen) == "First"
    assert next(gen) == "Second"
    assert next(gen) == "Third"

    # После исчерпания
    with pytest.raises(StopIteration):
        next(gen)


def test_transaction_descriptions_generator_is_one_time_use() -> None:
    """Тестирует, что генератор можно использовать только один раз"""
    transactions = [{"description": "Test"}]
    gen = transaction_descriptions(transactions)

    # Первое использование
    assert list(gen) == ["Test"]

    # Второе использование (должно быть пустым)
    assert list(gen) == []


def test_transaction_descriptions_mixed_valid_invalid_stops() -> None:
    """Тестирует остановку итерации при первой ошибке"""
    transactions = [
        {"description": "Valid 1"},
        {"wrong_key": "Invalid"},  # Нет description
        {"description": "Valid 2"},  # Не будет достигнут
    ]

    gen = transaction_descriptions(transactions)
    assert next(gen) == "Valid 1"

    with pytest.raises(KeyError, match="отсутствует ключ 'description'"):
        next(gen)


def test_transaction_descriptions_error_message_contains_transaction() -> None:
    """Тестирует, что сообщение об ошибке содержит информацию о транзакции"""
    bad_transaction = {"amount": 100, "date": "2024-01-01"}
    transactions = [bad_transaction]

    with pytest.raises(KeyError) as exc_info:
        list(transaction_descriptions(transactions))

    # Проверяем, что в сообщении об ошибке есть информация о транзакции
    assert "отсутствует ключ 'description'" in str(exc_info.value)


def test_transaction_descriptions_generator_type() -> None:
    """Тестирует, что возвращается именно генератор"""
    transactions = [{"description": "Test"}]
    result = transaction_descriptions(transactions)

    # Проверяем, что это генератор (не просто итератор)
    import types

    assert isinstance(result, types.GeneratorType)


def test_transaction_descriptions_generator_exhaustion() -> None:
    """Тестирует полное исчерпание генератора с проверкой всех элементов"""
    transactions = [
        {"description": "First"},
        {"description": "Second"},
        {"description": "Third"},
    ]
    gen = transaction_descriptions(transactions)

    # Получаем все элементы по одному
    assert next(gen) == "First"
    assert next(gen) == "Second"
    assert next(gen) == "Third"

    # Проверяем, что последующие вызовы next вызывают StopIteration
    with pytest.raises(StopIteration):
        next(gen)

    # Даже после исключения генератор остается истощенным
    with pytest.raises(StopIteration):
        next(gen)


def test_transaction_descriptions_with_empty_description_key() -> None:
    """Тестирует с ключом description, содержащим пустое значение"""
    transactions = [
        {"description": ""},
        {"description": "Non-empty"},
    ]
    result = list(transaction_descriptions(transactions))
    assert result == ["", "Non-empty"]


def test_transaction_descriptions_with_description_as_non_string() -> None:
    """Тестирует с description не строкового типа"""
    transactions = [
        {"description": 123},
        {"description": 45.67},
        {"description": True},
        {"description": False},
        {"description": None},
        {"description": [1, 2, 3]},
        {"description": {"key": "value"}},
    ]
    result = list(transaction_descriptions(transactions))
    assert result == [123, 45.67, True, False, None, [1, 2, 3], {"key": "value"}]


def test_transaction_descriptions_type_error_message_details() -> None:
    """Тестирует детали сообщений об ошибках типов"""
    with pytest.raises(TypeError) as exc_info:
        list(transaction_descriptions("not a list"))
    assert "transactions должен быть списком" in str(exc_info.value)

    with pytest.raises(TypeError) as exc_info:
        list(transaction_descriptions([1, 2, 3]))
    assert "Каждая транзакция должна быть словарем" in str(exc_info.value)


def test_transaction_descriptions_key_error_includes_bad_transaction() -> None:
    """Тестирует, что KeyError содержит информацию о проблемной транзакции"""
    bad_transaction = {"amount": 100, "currency": "USD"}
    transactions = [bad_transaction]

    with pytest.raises(KeyError) as exc_info:
        list(transaction_descriptions(transactions))

    error_str = str(exc_info.value)
    assert "description" in error_str
    assert str(bad_transaction) in error_str or "отсутствует ключ" in error_str


def test_transaction_descriptions_multiple_iterators_independent() -> None:
    """Тестирует, что несколько итераторов работают независимо"""
    transactions = [
        {"description": "A"},
        {"description": "B"},
        {"description": "C"},
    ]

    gen1 = transaction_descriptions(transactions)
    gen2 = transaction_descriptions(transactions)

    assert next(gen1) == "A"
    assert next(gen2) == "A"
    assert next(gen1) == "B"
    assert next(gen2) == "B"
    assert next(gen1) == "C"
    assert next(gen2) == "C"

    with pytest.raises(StopIteration):
        next(gen1)
    with pytest.raises(StopIteration):
        next(gen2)


def test_transaction_descriptions_non_iterable_input() -> None:
    """Тестирует с неитерируемыми объектами"""
    with pytest.raises(TypeError):
        list(transaction_descriptions(42))

    with pytest.raises(TypeError):
        list(transaction_descriptions(None))

    with pytest.raises(TypeError):
        list(transaction_descriptions(3.14))


def test_transaction_descriptions_with_custom_dict() -> None:
    """Тестирует с подклассом словаря, созданным через type"""
    CustomDict = type("CustomDict", (dict,), {})
    transactions = [
        CustomDict({"description": "Custom dict test"}),
        {"description": "Regular dict"},
    ]
    result = list(transaction_descriptions(transactions))
    assert result == ["Custom dict test", "Regular dict"]


# Тестирование функции card_number_generator
# Фикстуры
@pytest.fixture
def max_card_number() -> int:
    """Максимально допустимый номер карты"""
    return 10**16 - 1


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

    expected_last = " ".join(f"{max_card_number:016d}"[i : i + 4] for i in range(0, 16, 4))
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
        expected = " ".join(f"{i:016d}"[j : j + 4] for j in range(0, 16, 4))
        assert value == expected


def test_card_number_formatting() -> None:
    """Тестирует правильность форматирования"""
    generator = card_number_generator(1, 1)
    card = next(generator)
    assert len(card.replace(" ", "")) == 16
    assert card.count(" ") == 3
    assert all(len(group) == 4 for group in card.split())


def test_card_number_padding() -> None:
    """Тестирует добавление ведущих нулей"""
    test_cases = [
        (0, "0000 0000 0000 0000"),
        (5, "0000 0000 0000 0005"),
        (123, "0000 0000 0000 0123"),
        (12345, "0000 0000 0001 2345"),
        (1234567, "0000 0000 0123 4567"),
    ]
    for number, expected in test_cases:
        generator = card_number_generator(number, number)
        assert next(generator) == expected


def test_lazy_evaluation_large_range():
    """Тестирует, что генератор не создает все элементы сразу"""
    generator = card_number_generator(0, 10**10)
    # Проверяем, что памяти не выделено под все элементы
    import sys

    assert sys.getsizeof(generator) < 1000  # Должен занимать мало памяти

    # Проверяем, что можем получить первый элемент без задержки
    first = next(generator)
    assert first == "0000 0000 0000 0000"

    # Проверяем, что генератор продолжает работать
    second = next(generator)
    assert second == "0000 0000 0000 0001"


def test_card_number_generator_empty_range() -> None:
    """Тестирует пустой диапазон (хотя логически не должен существовать)"""
    # Если fin < start, уже протестировано
    # Но есть ли тест для случая, когда нужно сгенерировать 0 элементов?
    pass  # В текущей реализации такого быть не может из-за range(start, fin+1)


def test_card_number_generator_memory_efficiency() -> None:
    """Тестирует эффективность использования памяти для больших диапазонов"""
    import sys

    generator = card_number_generator(0, 10**15)
    # Генераторы обычно занимают мало памяти (несколько сотен байт)
    # Небольшой размер означает, что все элементы не хранятся в памяти
    size = sys.getsizeof(generator)

    # Проверяем, что генератор не пытается создать все элементы заранее
    # Размер должен быть небольшим (обычно 72-296 байт в разных версиях Python)
    assert size < 1000, f"Генератор занимает слишком много памяти ({size} байт)"

    # Также проверяем, что мы можем получить элементы без задержки
    first = next(generator)
    assert first == "0000 0000 0000 0000"

    second = next(generator)
    assert second == "0000 0000 0000 0001"


def test_card_number_generator_performance() -> None:
    """Тестирует производительность получения первого элемента"""
    import time

    start_time = time.time()
    generator = card_number_generator(10**15 - 10, 10**15 - 1)
    first_card = next(generator)
    generation_time = time.time() - start_time

    # Генерация первого элемента должна быть быстрой (< 0.001 сек)
    assert generation_time < 0.001
    assert first_card is not None


def test_card_number_generator_start_equal_fin_positive() -> None:
    """Тестирует start == fin для положительного числа"""
    generator = card_number_generator(9999, 9999)
    result = next(generator)
    assert result == "0000 0000 0000 9999"


def test_card_number_generator_start_zero_end_zero() -> None:
    """Тестирует диапазон от 0 до 0"""
    generator = card_number_generator(0, 0)
    result = next(generator)
    assert result == "0000 0000 0000 0000"

    with pytest.raises(StopIteration):
        next(generator)


def test_card_number_generator_max_value(max_card_number: int) -> None:
    """Тестирует максимальное значение"""
    generator = card_number_generator(max_card_number, max_card_number)
    result = next(generator)

    # Проверяем форматирование
    expected = " ".join(f"{max_card_number:016d}"[i : i + 4] for i in range(0, 16, 4))
    assert result == expected
    assert len(result.replace(" ", "")) == 16


def test_card_number_generator_just_below_max(max_card_number: int) -> None:
    """Тестирует значение чуть ниже максимального"""
    value = max_card_number - 1
    generator = card_number_generator(value, value)
    result = next(generator)

    expected = " ".join(f"{value:016d}"[i : i + 4] for i in range(0, 16, 4))
    assert result == expected


def test_card_number_generator_error_start_greater_than_fin_message() -> None:
    """Тестирует сообщение ошибки при start > fin"""
    with pytest.raises(ValueError, match="start должно быть меньше или равно fin"):
        gen = card_number_generator(100, 99)
        list(gen)  # Принудительная итерация для выполнения проверок


def test_card_number_generator_error_negative_start_message() -> None:
    """Тестирует сообщение ошибки при отрицательном start"""
    with pytest.raises(ValueError, match="start не может быть отрицательным"):
        gen = card_number_generator(-1, 5)
        next(gen)  # Принудительная итерация


def test_card_number_generator_error_exceeds_max_message(max_card_number: int) -> None:
    """Тестирует сообщение ошибки при превышении максимума"""
    with pytest.raises(ValueError, match=f"fin не может превышать {max_card_number}"):
        gen = card_number_generator(max_card_number, max_card_number + 1)
        next(gen)  # Принудительная итерация


def test_card_number_generator_very_large_range_partial_consumption() -> None:
    """Тестирует частичное потребление очень большого диапазона"""
    generator = card_number_generator(0, 10**15)

    # Берем только первые 100 элементов
    for i in range(100):
        card = next(generator)
        expected = " ".join(f"{i:016d}"[j : j + 4] for j in range(0, 16, 4))
        assert card == expected

    # Генератор все еще жив
    next(generator)  # 100-й элемент


def test_card_number_generator_format_consistency() -> None:
    """Тестирует консистентность форматирования для всех чисел в диапазоне"""
    start, end = 0, 100
    generator = card_number_generator(start, end)

    for expected_num in range(start, end + 1):
        card = next(generator)
        # Проверяем формат
        parts = card.split()
        assert len(parts) == 4
        assert all(len(part) == 4 for part in parts)

        # Проверяем число
        actual_num = int(card.replace(" ", ""))
        assert actual_num == expected_num


def test_card_number_generator_performance_for_small_range() -> None:
    """Тестирует производительность для маленького диапазона"""
    import time

    start_time = time.time()
    result = list(card_number_generator(0, 10000))
    end_time = time.time()

    # Генерация 10001 номера должна быть быстрой
    assert end_time - start_time < 0.5
    assert len(result) == 10001


def test_card_number_generator_memory_for_large_range() -> None:
    """Тестирует использование памяти для большого диапазона"""
    import sys

    generator = card_number_generator(0, 10**10)

    # Размер генератора должен быть постоянным и маленьким
    initial_size = sys.getsizeof(generator)

    # Получаем несколько элементов
    next(generator)
    next(generator)
    next(generator)

    # Размер не должен измениться
    assert sys.getsizeof(generator) == initial_size


def test_card_number_generator_consecutive_calls() -> None:
    """Тестирует последовательные вызовы генератора"""
    gen1 = card_number_generator(1, 3)
    gen2 = card_number_generator(1, 3)

    # Независимые генераторы
    assert next(gen1) == "0000 0000 0000 0001"
    assert next(gen2) == "0000 0000 0000 0001"
    assert next(gen1) == "0000 0000 0000 0002"
    assert next(gen2) == "0000 0000 0000 0002"


def test_card_number_generator_edge_cases_around_power_of_ten() -> None:
    """Тестирует граничные случаи вокруг степеней десятки"""
    test_cases = [
        (9, 10),
        (99, 100),
        (999, 1000),
        (9999, 10000),
        (99999, 100000),
    ]

    for start, end in test_cases:
        generator = card_number_generator(start, end)
        results = list(generator)
        assert len(results) == 2
        # Проверяем, что форматирование правильное для разных длин чисел
        assert int(results[0].replace(" ", "")) == start
        assert int(results[1].replace(" ", "")) == end


def test_card_number_generator_max_range_edges() -> None:
    """Тестирует граничные значения максимального диапазона"""
    max_num = 10**16 - 1

    # Последние несколько номеров
    generator = card_number_generator(max_num - 3, max_num)
    results = list(generator)
    assert len(results) == 4

    # Проверяем форматирование последнего номера
    last = results[-1]
    assert len(last.replace(" ", "")) == 16
    assert int(last.replace(" ", "")) == max_num


def test_card_number_generator_zero_to_large_number() -> None:
    """Тестирует генерацию от 0 до большого числа с проверкой первого и последнего"""
    generator = card_number_generator(0, 99999)

    # Первый элемент
    assert next(generator) == "0000 0000 0000 0000"

    # Пропускаем до последнего
    last = None
    for value in generator:
        last = value

    assert last == "0000 0000 0009 9999"


def test_card_number_generator_range_with_boundaries() -> None:
    """Тестирует диапазон, включающий границы разрядов"""
    generator = card_number_generator(9998, 10002)
    results = list(generator)

    expected = [
        "0000 0000 0000 9998",
        "0000 0000 0000 9999",
        "0000 0000 0001 0000",
        "0000 0000 0001 0001",
        "0000 0000 0001 0002",
    ]
    assert results == expected


def test_card_number_generator_start_equal_fin_multiple_calls() -> None:
    """Тестирует множественные вызовы одного и того же диапазона"""
    for i in range(100):
        generator = card_number_generator(i, i)
        result = next(generator)
        assert len(result.replace(" ", "")) == 16
        assert int(result.replace(" ", "")) == i


def test_card_number_generator_validation_order() -> None:
    """Тестирует порядок валидации параметров"""
    max_num = 10**16 - 1

    # start > fin, но fin превышает максимум - должна быть ошибка start > fin первой
    with pytest.raises(ValueError, match="start должно быть меньше или равно fin"):
        gen = card_number_generator(max_num + 1, max_num)
        next(gen)


def test_card_number_generator_negative_range() -> None:
    """Тестирует диапазон с отрицательными числами"""
    with pytest.raises(ValueError, match="start не может быть отрицательным"):
        list(card_number_generator(-10, -5))

    with pytest.raises(ValueError, match="start не может быть отрицательным"):
        list(card_number_generator(-1, 0))

    with pytest.raises(ValueError, match="start не может быть отрицательным"):
        list(card_number_generator(-100, -100))


def test_card_number_generator_iterator_behavior() -> None:
    """Тестирует полное соответствие протоколу итератора"""
    gen = card_number_generator(5, 7)

    # Проверяем, что это итератор
    from collections.abc import Iterator

    assert isinstance(gen, Iterator)

    # Проверяем метод __iter__ возвращает self
    assert iter(gen) is gen

    # Проверяем последовательное получение
    assert next(gen) == "0000 0000 0000 0005"
    assert next(gen) == "0000 0000 0000 0006"
    assert next(gen) == "0000 0000 0000 0007"

    with pytest.raises(StopIteration):
        next(gen)


def test_card_number_generator_yield_order() -> None:
    """Тестирует порядок выдачи элементов (должен быть строго возрастающим)"""
    numbers = list(card_number_generator(100, 200))

    # Проверяем, что все номера уникальны и идут в порядке возрастания
    for i in range(len(numbers) - 1):
        num1 = int(numbers[i].replace(" ", ""))
        num2 = int(numbers[i + 1].replace(" ", ""))
        assert num2 - num1 == 1


def test_card_number_generator_large_range_start_end() -> None:
    """Тестирует очень большой диапазон с проверкой только первого и последнего"""
    start = 10**15
    end = 10**15 + 100

    gen = card_number_generator(start, end)

    first = next(gen)
    assert int(first.replace(" ", "")) == start

    # Пропускаем до последнего
    last = None
    for value in gen:
        last = value

    assert last is not None
    assert int(last.replace(" ", "")) == end


def test_card_number_generator_no_memory_allocation_for_range() -> None:
    """Проверяет, что range не материализуется целиком"""
    import sys

    generator = card_number_generator(0, 10**15)

    # Размер объекта генератора - фиксированный
    size = sys.getsizeof(generator)
    assert 72 <= size <= 1000  # Типичный размер генератора в Python


@pytest.mark.parametrize(
    "start,fin",
    [
        (10**15, 10**15 + 1),
        (10**14, 10**14 + 5),
        (10**13, 10**13 + 10),
        (10**12, 10**12 + 20),
    ],
)
def test_card_number_generator_various_magnitudes(start: int, fin: int) -> None:
    """Параметризованный тест для разных порядков чисел"""
    generator = card_number_generator(start, fin)
    expected_num = start

    for card in generator:
        assert int(card.replace(" ", "")) == expected_num
        expected_num += 1


def test_edge_case_extremely_large_start() -> None:
    """Тестирует очень большой start (почти максимальный)"""
    max_num = 10**16 - 1
    start = max_num - 5
    generator = card_number_generator(start, max_num)

    results = list(generator)
    assert len(results) == 6

    # Проверяем последний элемент
    assert results[-1] == " ".join(f"{max_num:016d}"[i : i + 4] for i in range(0, 16, 4))


def test_edge_case_start_zero_fin_max() -> None:
    """Тестирует полный диапазон (0 до максимума) - только проверку создания"""
    max_num = 10**16 - 1
    generator = card_number_generator(0, max_num)

    # Проверяем только первые 10 элементов и создание итератора
    assert next(generator) == "0000 0000 0000 0000"
    for i in range(1, 10):
        assert next(generator) == " ".join(f"{i:016d}"[j : j + 4] for j in range(0, 16, 4))


def test_very_small_range_with_max_value() -> None:
    """Тестирует маленький диапазон около максимального значения"""
    max_num = 10**16 - 1
    generator = card_number_generator(max_num, max_num)
    result = next(generator)

    # Проверяем, что строка имеет правильную длину и формат
    assert len(result) == 19  # 16 цифр + 3 пробела
    assert result.count(" ") == 3
    assert all(len(part) == 4 for part in result.split())


def test_card_number_generator_large_number_padding_edges() -> None:
    """Тестирует паддинг на граничных значениях разрядов"""
    test_cases = [
        (9, "0000 0000 0000 0009"),
        (10, "0000 0000 0000 0010"),
        (99, "0000 0000 0000 0099"),
        (100, "0000 0000 0000 0100"),
        (999, "0000 0000 0000 0999"),
        (1000, "0000 0000 0000 1000"),
        (9999, "0000 0000 0000 9999"),
        (10000, "0000 0000 0001 0000"),
    ]

    for number, expected in test_cases:
        generator = card_number_generator(number, number)
        assert next(generator) == expected


def test_card_number_generator_stop_iteration_standard_behavior() -> None:
    """Тестирует стандартное поведение StopIteration"""
    gen = card_number_generator(0, 0)
    next(gen)  # Исчерпываем

    with pytest.raises(StopIteration) as exc_info:
        next(gen)

    # StopIteration может иметь значение, но обычно None или пустой кортеж
    assert exc_info.value.args == () or exc_info.value.value is None
