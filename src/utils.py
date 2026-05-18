import json
import os
from typing import List, Dict, Any


def load_transactions(file_path: str) -> List[Dict[str, Any]]:
    """Загружает финансовые транзакции из JSON-файла"""

    try:
        if os.path.getsize(file_path) == 0:
            return []

        with open(file_path, "r", encoding="utf-8") as file:
            data = json.load(file)

        # Проверяем, что данные являются списком
        if isinstance(data, list):
            return data
        else:
            return []

    except json.JSONDecodeError, IOError, OSError:
        # Возвращаем пустой список при любой ошибке чтения/парсинга
        return []
