import re
from typing import List, Dict, Any


def process_bank_search(data: List[Dict[str, Any]], search: str) -> List[Dict[str, Any]]:
    """Возвращает список словарей, у которых в поле 'description' есть строка поиска."""
    # Если поисковая строка пустая, возвращаем все элементы
    if not search:
        return data.copy()  # возвращаем копию, чтобы не изменять оригинал

    # Компилируем регулярное выражение для поиска (регистронезависимый режим)
    pattern = re.compile(re.escape(search), re.IGNORECASE)

    # Фильтруем список, оставляя только те словари, где description содержит search
    result = [
        item for item in data
        if isinstance(item.get('description'), str) and pattern.search(item['description'])
    ]

    return result


def count_operations_by_category(data: List[Dict[str, Any]], categories: List[str]) -> Dict[str, int]:
    """Подсчитывает количество операций в каждой категории на основе описания."""
    # Инициализируем словарь с нулевыми значениями для всех категорий
    result = {category: 0 for category in categories}

    # Проходим по всем операциям
    for transaction in data:
        # Безопасно получаем description, преобразуем None в пустую строку
        description_raw = transaction.get('description', '')
        if description_raw is None:
            description_raw = ''
        description = description_raw.lower()

        # Проверяем каждую категорию
        for category in categories:
            if category.lower() in description:
                result[category] += 1
                break  # Считаем операцию только в первой подходящей категории

    return result
