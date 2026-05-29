import pytest
import re
from typing import List, Dict, Any
from src.regularity import process_bank_search, count_operations_by_category


# Тестирование функции process_bank_search
# ТЕСТОВЫЕ ДАННЫЕ
sample_data: List[Dict[str, Any]] = [
    {"id": 1, "description": "Сбербанк - лучший банк"},
    {"id": 2, "description": "Тинькофф банк предлагает кредиты"},
    {"id": 3, "description": "Альфа-Банк: вклады и счета"},
    {"id": 4, "description": "Открытие банк - ипотека"},
    {"id": 5, "description": ""},  # пустой description
    {"id": 6},  # без ключа description
    {"id": 7, "description": None},  # None в description
]


def test_found_match() -> None:
    """Поиск существующей строки"""
    result: List[Dict[str, Any]] = process_bank_search(sample_data, "Сбербанк")
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_partial_match() -> None:
    """Поиск по части строки"""
    result: List[Dict[str, Any]] = process_bank_search(sample_data, "банк")
    assert len(result) == 4  # Сбербанк, Тинькофф банк, Альфа-Банк, Открытие банк


def test_case_insensitive() -> None:
    """Регистронезависимый поиск"""
    result: List[Dict[str, Any]] = process_bank_search(sample_data, "сбербанк")
    assert len(result) == 1
    assert result[0]["id"] == 1


def test_no_match() -> None:
    """Нет совпадений"""
    result: List[Dict[str, Any]] = process_bank_search(sample_data, "ВТБ")
    assert result == []


def test_empty_search() -> None:
    """Пустая строка поиска - должно вернуть все элементы"""
    result: List[Dict[str, Any]] = process_bank_search(sample_data, "")
    assert len(result) == len(sample_data)


def test_empty_description() -> None:
    """Пустой description не должен попадать в результат"""
    result: List[Dict[str, Any]] = process_bank_search(sample_data, "банк")
    ids: List[int] = [item["id"] for item in result]  # type: ignore
    assert 5 not in ids  # пустая строка
    assert 6 not in ids  # отсутствует ключ
    assert 7 not in ids  # None


def test_empty_data() -> None:
    """Пустой список на входе"""
    result: List[Dict[str, Any]] = process_bank_search([], "банк")
    assert result == []


def test_preserves_original_data() -> None:
    """Функция не изменяет исходные данные"""
    original: List[Dict[str, Any]] = sample_data.copy()
    process_bank_search(sample_data, "банк")
    assert sample_data == original


def test_special_characters() -> None:
    """Спецсимволы экранируются правильно"""
    data: List[Dict[str, Any]] = [{"id": 1, "description": "Кредит 100%"}]
    result: List[Dict[str, Any]] = process_bank_search(data, "100%")
    assert len(result) == 1


def test_unicode() -> None:
    """Поддержка Unicode"""
    data: List[Dict[str, Any]] = [{"id": 1, "description": "ПриватБанк — український банк"}]
    result: List[Dict[str, Any]] = process_bank_search(data, "український")
    assert len(result) == 1


# Параметризованный тест для компактности
@pytest.mark.parametrize("search,expected_count", [
    ("банк", 4),
    ("Сбер", 1),
    ("КРЕДИТ", 1),
    ("xyz", 0),
])
def test_multiple_queries(search: str, expected_count: int) -> None:
    """Тестирование разных поисковых запросов"""
    result: List[Dict[str, Any]] = process_bank_search(sample_data, search)
    assert len(result) == expected_count


# Тестирование функции count_operations_by_category

# ТЕСТОВЫЕ ДАННЫЕ
sample_data_categories: List[Dict[str, Any]] = [
    {"id": 1, "description": "Супермаркет Пятерочка", "amount": 500},
    {"id": 2, "description": "Кафе Макдоналдс", "amount": 300},
    {"id": 3, "description": "АЗС Лукойл", "amount": 1500},
    {"id": 4, "description": "Супермаркет Магнит", "amount": 800},
    {"id": 5, "description": "Кафе Кофе Хауз", "amount": 400},
    {"id": 6, "description": "Аптека", "amount": 200},
    {"id": 7, "description": ""},  # пустое описание
    {"id": 8},  # без ключа description
    {"id": 9, "description": None},  # None в description
]


def test_basic_counting() -> None:
    """Базовый подсчет операций по категориям"""
    # Используем категории, которые реально есть в описаниях
    categories: List[str] = ["супермаркет", "кафе", "транспорт", "аптека"]
    result: Dict[str, int] = count_operations_by_category(sample_data_categories, categories)

    assert result["супермаркет"] == 2  # Пятерочка и Магнит
    assert result["кафе"] == 2  # Макдоналдс и Кофе Хауз
    assert result["транспорт"] == 0  # нет операций с транспортом
    assert result["аптека"] == 1  # Аптека


def test_case_insensitive_matching() -> None:
    """Регистронезависимый поиск категорий"""
    categories: List[str] = ["СУПЕРМАРКЕТ", "Кафе"]
    data: List[Dict[str, Any]] = [
        {"id": 1, "description": "супермаркет"},
        {"id": 2, "description": "СУПЕРМАРКЕТ"},
        {"id": 3, "description": "СуперМаркет"},
    ]
    result: Dict[str, int] = count_operations_by_category(data, categories)

    assert result["СУПЕРМАРКЕТ"] == 3
    assert result["Кафе"] == 0


def test_category_matching_priority() -> None:
    """Операция должна попадать только в первую подходящую категорию"""
    categories: List[str] = ["супермаркет", "магнит"]  # обе категории есть в описании
    data: List[Dict[str, Any]] = [
        {"id": 1, "description": "Супермаркет Магнит"}  # подходит под обе категории
    ]
    result: Dict[str, int] = count_operations_by_category(data, categories)

    assert result["супермаркет"] == 1  # попала в первую категорию
    assert result["магнит"] == 0  # не попала во вторую


def test_empty_description() -> None:
    """Операции с пустым description не попадают ни в одну категорию"""
    categories: List[str] = ["супермаркет", "кафе"]
    data: List[Dict[str, Any]] = [
        {"id": 1, "description": ""},
        {"id": 2, "description": "   "},  # только пробелы
        {"id": 3, "description": None},
        {"id": 4},  # без ключа
    ]
    result: Dict[str, int] = count_operations_by_category(data, categories)

    assert result["супермаркет"] == 0
    assert result["кафе"] == 0


def test_missing_description_key() -> None:
    """Операции без ключа description не попадают ни в одну категорию"""
    categories: List[str] = ["супермаркет"]
    data: List[Dict[str, Any]] = [
        {"id": 1, "amount": 100},  # нет ключа description
        {"id": 2, "description": None},  # None
    ]
    result: Dict[str, int] = count_operations_by_category(data, categories)

    assert result["супермаркет"] == 0


def test_empty_data() -> None:
    """Пустой список операций"""
    categories: List[str] = ["супермаркет", "кафе"]
    result: Dict[str, int] = count_operations_by_category([], categories)

    assert result == {"супермаркет": 0, "кафе": 0}


def test_empty_categories() -> None:
    """Пустой список категорий"""
    categories: List[str] = []
    result: Dict[str, int] = count_operations_by_category(sample_data_categories, categories)

    assert result == {}


def test_partial_word_match() -> None:
    """Поиск по части слова (вхождение подстроки)"""
    categories: List[str] = ["продукты", "маркет"]
    data: List[Dict[str, Any]] = [
        {"id": 1, "description": "Супермаркет Пятерочка"}  # содержит "маркет"
    ]
    result: Dict[str, int] = count_operations_by_category(data, categories)

    assert result["продукты"] == 0  # не содержит "продукты"
    assert result["маркет"] == 1  # содержит "маркет"


def test_multiple_matches_same_category() -> None:
    """Несколько совпадений с одной категорией"""
    categories: List[str] = ["супермаркет"]
    data: List[Dict[str, Any]] = [
        {"id": 1, "description": "Супермаркет Пятерочка"},
        {"id": 2, "description": "Супермаркет Магнит"},
        {"id": 3, "description": "Продуктовый супермаркет"},
    ]
    result: Dict[str, int] = count_operations_by_category(data, categories)

    assert result["супермаркет"] == 3


def test_no_matches() -> None:
    """Нет совпадений ни с одной категорией"""
    categories: List[str] = ["транспорт", "связь"]
    data: List[Dict[str, Any]] = [
        {"id": 1, "description": "Супермаркет"},
        {"id": 2, "description": "Кафе"},
    ]
    result: Dict[str, int] = count_operations_by_category(data, categories)

    assert result["транспорт"] == 0
    assert result["связь"] == 0


def test_category_not_in_result() -> None:
    """Категории, которых нет в данных, должны иметь значение 0"""
    categories: List[str] = ["супермаркет", "транспорт", "связь"]
    data: List[Dict[str, Any]] = [
        {"id": 1, "description": "Супермаркет"}
    ]
    result: Dict[str, int] = count_operations_by_category(data, categories)

    assert result["супермаркет"] == 1
    assert result["транспорт"] == 0
    assert result["связь"] == 0


def test_whitespace_in_description() -> None:
    """Описания с пробелами и разными регистрами"""
    categories: List[str] = ["кафе", "ресторан"]
    data: List[Dict[str, Any]] = [
        {"id": 1, "description": "  КАФЕ  "},
        {"id": 2, "description": "\tРесторан\t"},
    ]
    result: Dict[str, int] = count_operations_by_category(data, categories)

    assert result["кафе"] == 1
    assert result["ресторан"] == 1


def test_unicode_categories() -> None:
    """Поддержка Unicode в категориях и описаниях"""
    categories: List[str] = ["кафе", "ресторан", "аптека"]
    data: List[Dict[str, Any]] = [
        {"id": 1, "description": "Кафе Пузата хата"},
        {"id": 2, "description": "Ресторан McDonald's"},
        {"id": 3, "description": "Аптека 36,6"},
    ]
    result: Dict[str, int] = count_operations_by_category(data, categories)

    assert result["кафе"] == 1
    assert result["ресторан"] == 1
    assert result["аптека"] == 1


def test_preserves_original_data() -> None:
    """Функция не должна изменять исходные данные"""
    original_data: List[Dict[str, Any]] = sample_data_categories.copy()
    categories: List[str] = ["супермаркет"]
    count_operations_by_category(sample_data_categories, categories)
    assert sample_data_categories == original_data


def test_returns_new_dict() -> None:
    """Функция должна возвращать новый словарь"""
    categories: List[str] = ["супермаркет"]
    result1: Dict[str, int] = count_operations_by_category(sample_data_categories, categories)
    result2: Dict[str, int] = count_operations_by_category(sample_data_categories, categories)

    assert result1 is not result2  # разные объекты


# Параметризованные тесты
@pytest.mark.parametrize("categories,expected", [
    (["супермаркет"], {"супермаркет": 2}),
    (["кафе"], {"кафе": 2}),
    (["аптека"], {"аптека": 1}),
    (["транспорт"], {"транспорт": 0}),
    (["супермаркет", "кафе"], {"супермаркет": 2, "кафе": 2}),
])
def test_parametrized_counts(categories: List[str], expected: Dict[str, int]) -> None:
    """Параметризованный тест для разных категорий"""
    result: Dict[str, int] = count_operations_by_category(sample_data_categories, categories)
    assert result == expected


@pytest.mark.parametrize("description,category,expected", [
    ("Супермаркет", "супермаркет", 1),
    ("", "супермаркет", 0),
    (None, "супермаркет", 0),
    ("АЗС Лукойл", "азс", 1),  # изменено: категория "азс" вместо "транспорт"
    ("Кафе", "кафе", 1),
    ("Макдоналдс", "макдоналдс", 1),  # дополнительный тест
    ("Пятерочка", "пятерочка", 1),  # дополнительный тест
])
def test_single_transaction(description: Any, category: str, expected: int) -> None:
    """Тест на одной транзакции с разными description"""
    data: List[Dict[str, Any]] = [{"id": 1, "description": description}]
    categories: List[str] = [category]
    result: Dict[str, int] = count_operations_by_category(data, categories)
    assert result[category] == expected


# Тест на производительность
def test_performance_large_dataset() -> None:
    """Проверка производительности на большом наборе данных"""
    large_data: List[Dict[str, Any]] = [
        {"id": i, "description": f"Супермаркет {i}"} for i in range(10000)
    ]
    categories: List[str] = ["супермаркет", "кафе"]

    import time
    start: float = time.time()
    result: Dict[str, int] = count_operations_by_category(large_data, categories)
    end: float = time.time()

    assert result["супермаркет"] == 10000
    assert result["кафе"] == 0
    assert end - start < 0.5
