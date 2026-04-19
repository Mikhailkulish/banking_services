from typing import Any, Dict, List


def filter_by_state(data_list: List[Dict[str, Any]], state: str = "EXECUTED") -> List[Dict[str, Any]]:
    """Функция выбирает из списка словари по значению ключа 'state'"""
    if not isinstance(data_list, list):
        raise TypeError("Некорректный тип данных")

    result = []
    for item in data_list:
        if isinstance(item, dict) and item.get("state") == state:
            result.append(item)

    return result


def sort_by_date(data_list: List[Dict[str, Any]], descending: bool = True) -> List[Dict[str, Any]]:
    """Сортирует список словарей по ключу 'date'"""
    if not isinstance(data_list, list):
        raise TypeError("Некорректный тип данных")

    result = []
    for item in data_list:
        result.append(item)

    result.sort(key=lambda x: x.get("date", ""), reverse=descending)

    return result
