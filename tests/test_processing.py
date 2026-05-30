from typing import Any, Dict, List

import pytest

from src.processing import filter_by_state, sort_by_date


# Тестирование функции filter_by_state
# Фикстура с тестовыми данными
@pytest.fixture
def sample_data_filter() -> List[Dict[str, Any]]:
    return [
        {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
        {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
        {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
        {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
    ]


def test_filter_by_state_default(sample_data_filter: List[Dict[str, Any]]) -> None:
    """Тестирует фильтрацию по умолчанию"""
    result = filter_by_state(sample_data_filter)
    assert len(result) == 2
    assert all(item["state"] == "EXECUTED" for item in result)


def test_filter_by_state_custom(sample_data_filter: List[Dict[str, Any]]) -> None:
    """Тестирует фильтрацию с указанием другого статуса"""
    result = filter_by_state(sample_data_filter, state="CANCELED")
    assert len(result) == 2
    assert all(item["state"] == "CANCELED" for item in result)


def test_filter_by_state_no_matches(sample_data_filter: List[Dict[str, Any]]) -> None:
    """Тестирует обработку при отсутствии совпадений"""
    result = filter_by_state(sample_data_filter, state="PENDING")
    assert result == []


def test_filter_by_state_empty_list() -> None:
    """Тестирует обработку при пустом списке на входе"""
    input_data: list = []
    assert filter_by_state(input_data) == []


def test_filter_by_state_invalid_items() -> None:
    """Тестирует на пропуск некорректных элементов (не словари, нет ключа state)"""
    data: List[Any] = [
        {"id": 1, "state": "EXECUTED"},
        "not a dict",
        123,
        {"id": 2},  # нет ключа state
        {"id": 3, "state": "EXECUTED"},
    ]
    result = filter_by_state(data)
    assert len(result) == 2
    assert result[0]["id"] == 1
    assert result[1]["id"] == 3


def test_filter_by_state_invalid_input() -> None:
    """Тестирует обработку ошибки входных данных"""
    invalid_input: Any = "not a list"
    with pytest.raises(TypeError, match="Некорректный тип данных"):
        filter_by_state(invalid_input)


# Тестирование функции sort_by_date
# Фикстура с тестовыми данными
@pytest.fixture
def sample_data_sort() -> List[Dict[str, Any]]:
    return [
        {"id": 41428829, "state": "EXECUTED", "date": "2019-07-03T18:35:29.512364"},
        {"id": 939719570, "state": "EXECUTED", "date": "2018-06-30T02:08:58.425572"},
        {"id": 594226727, "state": "CANCELED", "date": "2018-09-12T21:27:25.241689"},
        {"id": 615064591, "state": "CANCELED", "date": "2018-10-14T08:21:33.419441"},
    ]


def test_sort_by_date_descending(sample_data_sort: List[Dict[str, Any]]) -> None:
    """Тестирование сортировки по убыванию (по умолчанию)"""
    result = sort_by_date(sample_data_sort)
    dates = [item["date"] for item in result]
    assert dates == [
        "2019-07-03T18:35:29.512364",
        "2018-10-14T08:21:33.419441",
        "2018-09-12T21:27:25.241689",
        "2018-06-30T02:08:58.425572",
    ]


def test_sort_by_date_ascending(sample_data_sort: List[Dict[str, Any]]) -> None:
    """Тестирует сортировку по возрастанию"""
    result = sort_by_date(sample_data_sort, descending=False)
    dates = [item["date"] for item in result]
    assert dates == [
        "2018-06-30T02:08:58.425572",
        "2018-09-12T21:27:25.241689",
        "2018-10-14T08:21:33.419441",
        "2019-07-03T18:35:29.512364",
    ]


def test_sort_by_date_missing_key() -> None:
    """Тестирует обработку, когда элементы без ключа 'date' должны оказаться в конце или начале"""
    data = [{"id": 1, "date": "2020-01-01"}, {"id": 2, "name": "no date"}, {"id": 3, "date": "2019-01-01"}]

    result = sort_by_date(data, descending=True)
    assert result[0]["id"] == 1
    assert result[1]["id"] == 3
    assert result[2]["id"] == 2


def test_sort_by_date_empty_list() -> None:
    """Тестирует обработку пустого списка на входе"""
    assert sort_by_date([]) == []


def test_sort_by_date_does_not_modify_original(sample_data_sort: list[dict[str, Any]]) -> None:
    """Тестирует на не изменение исходного списка"""
    original_copy = sample_data_sort.copy()
    sort_by_date(sample_data_sort)
    assert sample_data_sort == original_copy


def test_sort_by_date_invalid_input() -> None:
    """Тестирует обработку ошибки"""
    invalid_input: Any = "not a list"

    with pytest.raises(TypeError, match="Некорректный тип данных"):
        sort_by_date(invalid_input)
